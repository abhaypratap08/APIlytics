import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.telemetry import TelemetryEvent

client = TestClient(app)


def make_event(project_ctx, minutes_ago: float, **overrides) -> TelemetryEvent:
    base = dict(
        event_id=uuid.uuid4(),
        project_id=uuid.UUID(project_ctx["project_id"]),
        integration_id=uuid.UUID(project_ctx["integration_id"]),
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
        method="GET", route_template="/api/test",
        status_code=200, latency_ms=100.0,
    )
    base.update(overrides)
    return TelemetryEvent(**base)


def _insert(events):
    db = SessionLocal()
    try:
        db.add_all(events); db.commit()
    finally:
        db.close()


def test_empty_returns_no_alerts(project_ctx):
    r = client.get(f"/api/v1/alerts?window=60m&project_id={project_ctx['project_id']}")
    assert r.status_code == 200
    assert r.json()["items"] == []


def test_project_id_required():
    assert client.get("/api/v1/alerts?window=60m").status_code == 422


def test_high_error_rate_alert_fires(project_ctx):
    _insert([make_event(project_ctx, 5, status_code=500) for _ in range(6)]
            + [make_event(project_ctx, 5) for _ in range(4)])
    items = client.get(f"/api/v1/alerts?window=60m&project_id={project_ctx['project_id']}").json()["items"]
    types = [i["type"] for i in items]
    assert "HIGH_ERROR_RATE" in types
    hr = next(i for i in items if i["type"] == "HIGH_ERROR_RATE")
    assert hr["id"] == "high-error-rate:GET:/api/test:60m"


def test_normal_traffic_does_not_alert(project_ctx):
    _insert([make_event(project_ctx, 5) for _ in range(10)])
    assert client.get(f"/api/v1/alerts?window=60m&project_id={project_ctx['project_id']}").json()["items"] == []


def test_traffic_spike_requires_baseline(project_ctx):
    _insert([make_event(project_ctx, 5) for _ in range(20)]
            + [make_event(project_ctx, 90) for _ in range(2)])
    items = client.get(f"/api/v1/alerts?window=60m&project_id={project_ctx['project_id']}").json()["items"]
    assert len([i for i in items if i["type"] == "TRAFFIC_ANOMALY"]) == 1


def test_no_baseline_no_spike(project_ctx):
    _insert([make_event(project_ctx, 5) for _ in range(30)])
    types = [i["type"] for i in
             client.get(f"/api/v1/alerts?window=60m&project_id={project_ctx['project_id']}").json()["items"]]
    assert "TRAFFIC_ANOMALY" not in types


def test_latency_regression_fires(project_ctx):
    _insert([make_event(project_ctx, 5, latency_ms=1000.0) for _ in range(10)]
            + [make_event(project_ctx, 90, latency_ms=100.0) for _ in range(10)])
    types = [i["type"] for i in
             client.get(f"/api/v1/alerts?window=60m&project_id={project_ctx['project_id']}").json()["items"]]
    assert "LATENCY_REGRESSION" in types


def test_alert_ids_deterministic(project_ctx):
    _insert([make_event(project_ctx, 5, status_code=500) for _ in range(10)])
    pid = project_ctx["project_id"]
    first = [i["id"] for i in client.get(f"/api/v1/alerts?window=60m&project_id={pid}").json()["items"]]
    second = [i["id"] for i in client.get(f"/api/v1/alerts?window=60m&project_id={pid}").json()["items"]]
    assert first == second


def test_summary_alerts_count_reflects_findings(project_ctx):
    _insert([make_event(project_ctx, 5, status_code=500) for _ in range(10)])
    s = client.get(f"/api/v1/summary?window=60m&project_id={project_ctx['project_id']}").json()
    assert s["alerts_count"] >= 1
