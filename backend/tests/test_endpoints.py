import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.telemetry import TelemetryEvent

client = TestClient(app)


def make_event(project_ctx, **overrides) -> TelemetryEvent:
    base = dict(
        event_id=uuid.uuid4(),
        project_id=uuid.UUID(project_ctx["project_id"]),
        integration_id=uuid.UUID(project_ctx["integration_id"]),
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


def test_empty_returns_empty_items():
    r = client.get("/api/v1/endpoints?window=60m")
    assert r.status_code == 200
    assert r.json()["items"] == []


def test_groups_by_method_and_route(project_ctx):
    _insert([
        make_event(project_ctx, route_template="/a", method="GET"),
        make_event(project_ctx, route_template="/a", method="GET"),
        make_event(project_ctx, route_template="/a", method="POST"),
        make_event(project_ctx, route_template="/b", method="GET"),
    ])
    items = client.get("/api/v1/endpoints?window=60m").json()["items"]
    assert len(items) == 3


def test_sorted_by_request_count_desc(project_ctx):
    _insert([
        make_event(project_ctx, route_template="/small"),
        make_event(project_ctx, route_template="/big"),
        make_event(project_ctx, route_template="/big"),
        make_event(project_ctx, route_template="/big"),
        make_event(project_ctx, route_template="/mid"),
        make_event(project_ctx, route_template="/mid"),
    ])
    routes = [i["route_template"] for i in client.get("/api/v1/endpoints?window=60m").json()["items"]]
    assert routes == ["/big", "/mid", "/small"]


def test_per_endpoint_values_correct(project_ctx):
    _insert([
        make_event(project_ctx, route_template="/x", status_code=200, latency_ms=100.0),
        make_event(project_ctx, route_template="/x", status_code=500, latency_ms=200.0),
    ])
    item = client.get("/api/v1/endpoints?window=60m").json()["items"][0]
    assert item["request_count"] == 2
    assert item["error_rate_pct"] == 50.0
    assert item["avg_latency_ms"] == 150.0
    assert item["p95_latency_ms"] == 195.0


def test_limit_respected(project_ctx):
    _insert([make_event(project_ctx, route_template=f"/r{i}") for i in range(10)])
    assert len(client.get("/api/v1/endpoints?window=60m&limit=3").json()["items"]) == 3


def test_limit_out_of_range_rejected():
    assert client.get("/api/v1/endpoints?window=60m&limit=0").status_code == 422
    assert client.get("/api/v1/endpoints?window=60m&limit=101").status_code == 422


def test_invalid_window_rejected():
    assert client.get("/api/v1/endpoints?window=5m").status_code == 422


def test_endpoint_totals_match_summary(project_ctx):
    _insert([
        make_event(project_ctx, route_template="/a", status_code=200),
        make_event(project_ctx, route_template="/a", status_code=500),
        make_event(project_ctx, route_template="/b", status_code=200),
        make_event(project_ctx, route_template="/c", status_code=200),
        make_event(project_ctx, route_template="/c", status_code=200),
    ])
    s = client.get("/api/v1/summary?window=60m").json()
    e = client.get("/api/v1/endpoints?window=60m&limit=100").json()
    assert sum(i["request_count"] for i in e["items"]) == s["total_requests"] == 5
    assert sum(round(i["error_rate_pct"] * i["request_count"] / 100) for i in e["items"]) == s["error_count"] == 1
