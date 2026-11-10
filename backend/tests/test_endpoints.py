import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.session import SessionLocal, engine
from app.main import app
from app.models.telemetry import TelemetryEvent

client = TestClient(app)


def make_event(**overrides) -> TelemetryEvent:
    base = dict(
        event_id=uuid.uuid4(),
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=5),
        method="GET",
        route_template="/api/test",
        status_code=200,
        latency_ms=100.0,
    )
    base.update(overrides)
    return TelemetryEvent(**base)


def _insert(events):
    db = SessionLocal()
    try:
        db.add_all(events)
        db.commit()
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_events():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE telemetry_events RESTART IDENTITY"))
    yield


def test_empty_endpoints_returns_empty_items():
    r = client.get("/api/v1/endpoints?window=60m")
    assert r.status_code == 200
    data = r.json()
    assert data["window"] == "60m"
    assert data["items"] == []


def test_groups_by_method_and_route():
    _insert([
        make_event(route_template="/a", method="GET"),
        make_event(route_template="/a", method="GET"),
        make_event(route_template="/a", method="POST"),
        make_event(route_template="/b", method="GET"),
    ])
    r = client.get("/api/v1/endpoints?window=60m")
    data = r.json()
    keys = [(i["method"], i["route_template"]) for i in data["items"]]
    assert len(keys) == 3


def test_sorted_by_request_count_desc():
    _insert([
        make_event(route_template="/small"),
        make_event(route_template="/big"),
        make_event(route_template="/big"),
        make_event(route_template="/big"),
        make_event(route_template="/mid"),
        make_event(route_template="/mid"),
    ])
    r = client.get("/api/v1/endpoints?window=60m")
    routes = [i["route_template"] for i in r.json()["items"]]
    assert routes == ["/big", "/mid", "/small"]


def test_per_endpoint_values_correct():
    _insert([
        make_event(route_template="/x", status_code=200, latency_ms=100.0),
        make_event(route_template="/x", status_code=500, latency_ms=200.0),
    ])
    r = client.get("/api/v1/endpoints?window=60m")
    item = r.json()["items"][0]
    assert item["route_template"] == "/x"
    assert item["request_count"] == 2
    assert item["error_rate_pct"] == 50.0
    assert item["avg_latency_ms"] == 150.0
    assert item["p95_latency_ms"] == 195.0
    assert item["estimated_cost"] == 0.0
    assert item["cost_unit"] == "demo-units"


def test_limit_respected():
    _insert([make_event(route_template=f"/r{i}") for i in range(10)])
    r = client.get("/api/v1/endpoints?window=60m&limit=3")
    assert len(r.json()["items"]) == 3


def test_limit_out_of_range_rejected():
    assert client.get("/api/v1/endpoints?window=60m&limit=0").status_code == 422
    assert client.get("/api/v1/endpoints?window=60m&limit=101").status_code == 422


def test_invalid_window_rejected():
    r = client.get("/api/v1/endpoints?window=5m")
    assert r.status_code == 422
    assert "Unsupported window" in r.json()["detail"]


def test_endpoint_totals_match_summary():
    _insert([
        make_event(route_template="/a", status_code=200),
        make_event(route_template="/a", status_code=500),
        make_event(route_template="/b", status_code=200),
        make_event(route_template="/c", status_code=200),
        make_event(route_template="/c", status_code=200),
    ])
    s = client.get("/api/v1/summary?window=60m").json()
    e = client.get("/api/v1/endpoints?window=60m&limit=100").json()

    total_from_endpoints = sum(i["request_count"] for i in e["items"])
    assert total_from_endpoints == s["total_requests"] == 5

    error_count_from_endpoints = sum(
        round(i["error_rate_pct"] * i["request_count"] / 100) for i in e["items"]
    )
    assert error_count_from_endpoints == s["error_count"] == 1
