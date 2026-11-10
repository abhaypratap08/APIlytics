import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_sandbox_session(project_ctx):
    pid = project_ctx["project_id"]
    payload = {"target_url": "https://example.com"}
    r = client.post(f"/api/v1/projects/{pid}/sandbox-sessions", json=payload)
    assert r.status_code == 201
    assert r.json()["status"] == "active"
    assert r.json()["target_url"] == "https://example.com/"

def test_ssrf_protection(project_ctx):
    pid = project_ctx["project_id"]
    # localhost should be blocked
    r = client.post(f"/api/v1/projects/{pid}/sandbox-sessions", json={"target_url": "http://127.0.0.1:8000"})
    assert r.status_code == 400
    assert "SSRF Protection" in r.json()["detail"]

    # private IP should be blocked
    r = client.post(f"/api/v1/projects/{pid}/sandbox-sessions", json={"target_url": "http://192.168.1.1"})
    assert r.status_code == 400

def test_stop_session(project_ctx):
    pid = project_ctx["project_id"]
    created = client.post(f"/api/v1/projects/{pid}/sandbox-sessions", json={"target_url": "https://example.com"}).json()
    sid = created["id"]

    r = client.post(f"/api/v1/sandbox-sessions/{sid}/stop")
    assert r.status_code == 200
    assert r.json()["status"] == "stopped"

def test_internal_ingest(project_ctx):
    pid = project_ctx["project_id"]
    created = client.post(f"/api/v1/projects/{pid}/sandbox-sessions", json={"target_url": "https://example.com"}).json()
    sid = created["id"]

    ev = {
        "event_id": str(uuid.uuid4()),
        "source_type": "browser_sandbox",
        "timestamp": "2026-11-11T12:00:00Z",
        "method": "GET",
        "route_template": "/api/test",
        "status_code": 200,
        "latency_ms": 150.0,
        "origin_host": "example.com"
    }
    
    r = client.post(f"/api/v1/internal/sandbox-sessions/{sid}/events", json={"events": [ev]})
    assert r.status_code == 200
    assert r.json()["accepted"] == 1
