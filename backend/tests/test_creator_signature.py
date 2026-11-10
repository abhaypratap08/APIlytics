from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_creator_header_on_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.headers.get("x-creator") == "Abhay Pratap Singh"
    assert r.headers.get("x-project-owner") == "Backend and Integration"


def test_creator_header_on_summary(project_ctx):
    r = client.get(f"/api/v1/summary?window=60m&project_id={project_ctx['project_id']}")
    assert r.status_code == 200
    assert r.headers.get("x-creator") == "Abhay Pratap Singh"


def test_creator_header_on_endpoints(project_ctx):
    r = client.get(f"/api/v1/endpoints?window=60m&project_id={project_ctx['project_id']}")
    assert r.status_code == 200
    assert r.headers.get("x-creator") == "Abhay Pratap Singh"


def test_root_returns_creator():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["creator"] == "Abhay Pratap Singh"
    assert body["role"] == "Backend and Integration"


def test_openapi_metadata_names_creator():
    spec = client.get("/openapi.json").json()
    assert spec["info"]["contact"]["name"] == "Abhay Pratap Singh"
    assert "Abhay Pratap Singh" in spec["info"]["description"]
