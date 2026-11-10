import uuid

import pytest
from sqlalchemy import text

from app.core.security import hash_token
from app.db.session import SessionLocal, engine
import app.models  # noqa: F401
from app.models.integration import Integration
from app.models.project import Project


@pytest.fixture(autouse=True)
def clean_db():
    with engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE telemetry_events, integrations, projects RESTART IDENTITY CASCADE"
        ))
    yield


@pytest.fixture
def project_ctx():
    db = SessionLocal()
    try:
        p = Project(name="Test Project")
        db.add(p)
        db.flush()
        raw_token = "test-token-" + uuid.uuid4().hex
        i = Integration(
            project_id=p.id,
            provider="test",
            name="Test Integration",
            credential_hash=hash_token(raw_token),
        )
        db.add(i)
        db.commit()
        db.refresh(p)
        db.refresh(i)
        return {
            "project_id": str(p.id),
            "integration_id": str(i.id),
            "token": raw_token,
        }
    finally:
        db.close()
