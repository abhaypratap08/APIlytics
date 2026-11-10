import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_project():
    r = client.post("/api/v1/projects", json={"name": "Acme", "description": "Test"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Acme"
    assert body["status"] == "active"
    assert "id" in body


def test_list_projects():
    client.post("/api/v1/projects", json={"name": "P1"})
    client.post("/api/v1/projects", json={"name": "P2"})
    r = client.get("/api/v1/projects")
    assert r.status_code == 200
    names = [p["name"] for p in r.json()]
    assert "P1" in names and "P2" in names


def test_get_project_404():
    r = client.get(f"/api/v1/projects/{uuid.uuid4()}")
    assert r.status_code == 404


def test_create_integration_returns_credential_once():
    p = client.post("/api/v1/projects", json={"name": "Proj"}).json()
    r = client.post(
        f"/api/v1/projects/{p['id']}/integrations",
        json={"provider": "nginx", "name": "Prod Nginx"},
    )
    assert r.status_code == 201
    body = r.json()
    assert "credential" in body
    assert len(body["credential"]) > 20
    # Subsequent list does NOT include credential
    listed = client.get(f"/api/v1/projects/{p['id']}/integrations").json()
    assert all("credential" not in i for i in listed)


def test_rotate_credential_invalidates_old():
    p = client.post("/api/v1/projects", json={"name": "Proj"}).json()
    created = client.post(
        f"/api/v1/projects/{p['id']}/integrations",
        json={"provider": "nginx", "name": "Nginx"},
    ).json()
    old_token = created["credential"]
    iid = created["id"]

    # Old token works for ingest
    ev = {"event_id": str(uuid.uuid4()),
          "timestamp": "2026-11-10T12:00:00Z",
          "method": "GET", "route_template": "/api/x",
          "status_code": 200, "latency_ms": 50}
    ok = client.post("/api/v1/ingest/events", json={"events": [ev]},
                     headers={"Authorization": f"Bearer {old_token}"})
    assert ok.status_code == 200

    # Rotate
    rotated = client.post(f"/api/v1/integrations/{iid}/rotate-credential")
    assert rotated.status_code == 200
    new_token = rotated.json()["credential"]
    assert new_token != old_token

    # Old token rejected
    bad = client.post("/api/v1/ingest/events", json={"events": [ev]},
                      headers={"Authorization": f"Bearer {old_token}"})
    assert bad.status_code == 401

    # New token works
    ev2 = {**ev, "event_id": str(uuid.uuid4())}
    good = client.post("/api/v1/ingest/events", json={"events": [ev2]},
                       headers={"Authorization": f"Bearer {new_token}"})
    assert good.status_code == 200


def test_revoke_credential():
    p = client.post("/api/v1/projects", json={"name": "Proj"}).json()
    created = client.post(
        f"/api/v1/projects/{p['id']}/integrations",
        json={"provider": "nginx", "name": "Nginx"},
    ).json()
    iid = created["id"]
    token = created["credential"]

    revoked = client.post(f"/api/v1/integrations/{iid}/revoke")
    assert revoked.status_code == 200
    assert revoked.json()["status"] == "revoked"

    ev = {"event_id": str(uuid.uuid4()),
          "timestamp": "2026-11-10T12:00:00Z",
          "method": "GET", "route_template": "/api/x",
          "status_code": 200, "latency_ms": 50}
    bad = client.post("/api/v1/ingest/events", json={"events": [ev]},
                      headers={"Authorization": f"Bearer {token}"})
    assert bad.status_code == 401
