import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.session import engine
from app.main import app

client = TestClient(app)


def make_event(**overrides):
    base = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": "GET",
        "route_template": "/api/test",
        "source_type": "nginx",
        "status_code": 200,
        "latency_ms": 100.0,
    }
    base.update(overrides)
    return base


def auth_h(ctx):
    return {"Authorization": f"Bearer {ctx['token']}"}


def test_ingest_requires_auth():
    r = client.post("/api/v1/ingest/events", json={"events": [make_event()]})
    assert r.status_code == 401


def test_invalid_token_rejected():
    r = client.post("/api/v1/ingest/events", json={"events": [make_event()]},
                    headers={"Authorization": "Bearer obviously-wrong"})
    assert r.status_code == 401


def test_ingest_single_event(project_ctx):
    r = client.post("/api/v1/ingest/events", json={"events": [make_event()]}, headers=auth_h(project_ctx))
    assert r.status_code == 200
    assert r.json() == {"accepted": 1, "duplicates": 0}


def test_ingest_batch_of_three(project_ctx):
    r = client.post("/api/v1/ingest/events",
                    json={"events": [make_event() for _ in range(3)]},
                    headers=auth_h(project_ctx))
    assert r.json() == {"accepted": 3, "duplicates": 0}


def test_duplicate_event_id_skipped(project_ctx):
    event = make_event()
    r1 = client.post("/api/v1/ingest/events", json={"events": [event]}, headers=auth_h(project_ctx))
    r2 = client.post("/api/v1/ingest/events", json={"events": [event]}, headers=auth_h(project_ctx))
    assert r1.json() == {"accepted": 1, "duplicates": 0}
    assert r2.json() == {"accepted": 0, "duplicates": 1}


def test_duplicate_within_same_batch(project_ctx):
    eid = str(uuid.uuid4())
    events = [make_event(event_id=eid), make_event(event_id=eid)]
    r = client.post("/api/v1/ingest/events", json={"events": events}, headers=auth_h(project_ctx))
    assert r.json() == {"accepted": 1, "duplicates": 1}


def test_invalid_status_code_rejected(project_ctx):
    r = client.post("/api/v1/ingest/events",
                    json={"events": [make_event(status_code=99)]},
                    headers=auth_h(project_ctx))
    assert r.status_code == 422


def test_missing_timezone_rejected(project_ctx):
    r = client.post("/api/v1/ingest/events",
                    json={"events": [make_event(timestamp="2026-11-05T10:00:00")]},
                    headers=auth_h(project_ctx))
    assert r.status_code == 422


def test_empty_batch_rejected(project_ctx):
    r = client.post("/api/v1/ingest/events", json={"events": []}, headers=auth_h(project_ctx))
    assert r.status_code == 422


def test_events_persisted_with_correct_ids(project_ctx):
    client.post("/api/v1/ingest/events",
                json={"events": [make_event(route_template="/api/persist")]},
                headers=auth_h(project_ctx))
    with engine.connect() as conn:
        row = conn.execute(text(
            "SELECT route_template, project_id::text, integration_id::text FROM telemetry_events"
        )).fetchone()
    assert row[0] == "/api/persist"
    assert row[1] == project_ctx["project_id"]
    assert row[2] == project_ctx["integration_id"]


def test_revoked_credential_rejected(project_ctx):
    ok = client.post("/api/v1/ingest/events", json={"events": [make_event()]}, headers=auth_h(project_ctx))
    assert ok.status_code == 200
    with engine.begin() as conn:
        conn.execute(text("UPDATE integrations SET status='revoked' WHERE id = :id"),
                     {"id": project_ctx["integration_id"]})
    bad = client.post("/api/v1/ingest/events", json={"events": [make_event()]}, headers=auth_h(project_ctx))
    assert bad.status_code == 401
