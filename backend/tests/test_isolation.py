"""Mode B critical property: a project's read routes must not expose
another project's telemetry, even if the project_id is guessed correctly."""
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.telemetry import TelemetryEvent

client = TestClient(app)


def _seed(project_ctx, n: int, route: str, status_code: int = 200):
    db = SessionLocal()
    try:
        for _ in range(n):
            db.add(TelemetryEvent(
                event_id=uuid.uuid4(),
        source_type="nginx",
                project_id=uuid.UUID(project_ctx["project_id"]),
                integration_id=uuid.UUID(project_ctx["integration_id"]),
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=2),
                method="GET", route_template=route,
                status_code=status_code, latency_ms=100.0,
            ))
        db.commit()
    finally:
        db.close()


def _make_other_project():
    """Create a second project + integration directly in DB."""
    from app.core.security import hash_token
    from app.models.integration import Integration
    from app.models.project import Project

    db = SessionLocal()
    try:
        p = Project(name="Other Project")
        db.add(p); db.flush()
        i = Integration(project_id=p.id, provider="test", name="Other",
                        credential_hash=hash_token("other-token"))
        db.add(i); db.commit()
        return {"project_id": str(p.id), "integration_id": str(i.id), "token": "other-token"}
    finally:
        db.close()


def test_summary_scoped_to_project_a(project_ctx):
    other = _make_other_project()
    _seed(project_ctx, 3, "/api/a")
    _seed(other, 7, "/api/b")  # other project has 7

    a = client.get(f"/api/v1/summary?window=60m&project_id={project_ctx['project_id']}").json()
    b = client.get(f"/api/v1/summary?window=60m&project_id={other['project_id']}").json()
    assert a["total_requests"] == 3
    assert b["total_requests"] == 7


def test_endpoints_scoped_to_project_a(project_ctx):
    other = _make_other_project()
    _seed(project_ctx, 3, "/api/a")
    _seed(other, 7, "/api/b")

    a = client.get(f"/api/v1/endpoints?window=60m&project_id={project_ctx['project_id']}").json()
    b = client.get(f"/api/v1/endpoints?window=60m&project_id={other['project_id']}").json()

    a_routes = {i["route_template"] for i in a["items"]}
    b_routes = {i["route_template"] for i in b["items"]}
    assert a_routes == {"/api/a"}
    assert b_routes == {"/api/b"}
    assert sum(i["request_count"] for i in a["items"]) == 3
    assert sum(i["request_count"] for i in b["items"]) == 7


def test_alerts_scoped_to_project_a(project_ctx):
    other = _make_other_project()
    # Both projects have high error rate; each should see only its own alert
    _seed(project_ctx, 10, "/api/a", status_code=500)
    _seed(other, 10, "/api/b", status_code=500)

    a = client.get(f"/api/v1/alerts?window=60m&project_id={project_ctx['project_id']}").json()
    b = client.get(f"/api/v1/alerts?window=60m&project_id={other['project_id']}").json()

    assert len(a["items"]) >= 1
    assert all(i["route_template"] == "/api/a" for i in a["items"])
    assert all(i["route_template"] == "/api/b" for i in b["items"])


def test_unknown_project_id_returns_empty_data():
    bogus = uuid.uuid4()
    s = client.get(f"/api/v1/summary?window=60m&project_id={bogus}").json()
    e = client.get(f"/api/v1/endpoints?window=60m&project_id={bogus}").json()
    a = client.get(f"/api/v1/alerts?window=60m&project_id={bogus}").json()
    assert s["total_requests"] == 0
    assert e["items"] == []
    assert a["items"] == []
