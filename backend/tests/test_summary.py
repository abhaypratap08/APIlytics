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
        source_type="nginx",
        project_id=uuid.UUID(project_ctx["project_id"]),
        integration_id=uuid.UUID(project_ctx["integration_id"]),
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=5),
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


def test_empty_window_returns_zeros(project_ctx):
    r = client.get(f"/api/v1/summary?window=60m&project_id={project_ctx['project_id']}")
    data = r.json()
    assert r.status_code == 200
    assert data["total_requests"] == 0
    assert data["error_count"] == 0
    assert data["error_rate_pct"] == 0.0
    assert data["avg_latency_ms"] == 0.0
    assert data["p95_latency_ms"] == 0.0
    assert data["estimated_cost"] == 0.0
    assert data["cost_unit"] == "demo-units"
    assert data["alerts_count"] == 0


def test_known_events_produce_expected_summary(project_ctx):
    _insert([
        make_event(project_ctx, latency_ms=100.0),
        make_event(project_ctx, latency_ms=200.0),
        make_event(project_ctx, latency_ms=300.0, status_code=500),
    ])
    data = client.get(f"/api/v1/summary?window=60m&project_id={project_ctx['project_id']}").json()
    assert data["total_requests"] == 3
    assert data["error_count"] == 1
    assert data["error_rate_pct"] == 33.33
    assert data["avg_latency_ms"] == 200.0
    assert data["p95_latency_ms"] == 290.0


def test_project_id_required():
    assert client.get("/api/v1/summary?window=60m").status_code == 422


def test_unsupported_window_returns_422(project_ctx):
    r = client.get(f"/api/v1/summary?window=5m&project_id={project_ctx['project_id']}")
    assert r.status_code == 422
    assert "Unsupported window" in r.json()["detail"]


def test_all_supported_windows_accepted(project_ctx):
    for w in ("15m", "60m", "24h"):
        r = client.get(f"/api/v1/summary?window={w}&project_id={project_ctx['project_id']}")
        assert r.status_code == 200
        assert r.json()["window"] == w


def test_events_outside_window_excluded(project_ctx):
    _insert([
        make_event(project_ctx, timestamp=datetime.now(timezone.utc) - timedelta(minutes=5)),
        make_event(project_ctx, timestamp=datetime.now(timezone.utc) - timedelta(hours=2)),
    ])
    pid = project_ctx["project_id"]
    assert client.get(f"/api/v1/summary?window=60m&project_id={pid}").json()["total_requests"] == 1
    assert client.get(f"/api/v1/summary?window=24h&project_id={pid}").json()["total_requests"] == 2
