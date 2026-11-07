import uuid
from datetime import datetime, timezone

import pytest
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
        "status_code": 200,
        "latency_ms": 100.0,
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def clean_events_table():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE telemetry_events RESTART IDENTITY"))
    yield


def test_ingest_single_event():
    event = make_event()
    r = client.post("/api/v1/events", json={"events": [event]})
    assert r.status_code == 200
    assert r.json() == {"accepted": 1, "duplicates": 0}


def test_ingest_batch_of_three():
    events = [make_event() for _ in range(3)]
    r = client.post("/api/v1/events", json={"events": events})
    assert r.status_code == 200
    assert r.json() == {"accepted": 3, "duplicates": 0}


def test_duplicate_event_id_skipped():
    event = make_event()
    r1 = client.post("/api/v1/events", json={"events": [event]})
    r2 = client.post("/api/v1/events", json={"events": [event]})
    assert r1.json() == {"accepted": 1, "duplicates": 0}
    assert r2.json() == {"accepted": 0, "duplicates": 1}


def test_duplicate_within_same_batch():
    eid = str(uuid.uuid4())
    events = [make_event(event_id=eid), make_event(event_id=eid)]
    r = client.post("/api/v1/events", json={"events": events})
    assert r.json() == {"accepted": 1, "duplicates": 1}


def test_invalid_status_code_rejected():
    bad = make_event(status_code=99)
    r = client.post("/api/v1/events", json={"events": [bad]})
    assert r.status_code == 422


def test_missing_timezone_rejected():
    bad = make_event(timestamp="2026-11-05T10:00:00")
    r = client.post("/api/v1/events", json={"events": [bad]})
    assert r.status_code == 422


def test_empty_batch_rejected():
    r = client.post("/api/v1/events", json={"events": []})
    assert r.status_code == 422


def test_events_are_persisted():
    event = make_event(route_template="/api/persist")
    client.post("/api/v1/events", json={"events": [event]})
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT route_template, status_code FROM telemetry_events")
        ).fetchone()
    assert row[0] == "/api/persist"
    assert row[1] == 200
