"""Dev-mode demo project/integration. Owned by Abhay Pratap Singh."""
import uuid

from sqlalchemy.orm import Session

from app.core.security import hash_token
from app.models.integration import Integration
from app.models.project import Project

DEMO_PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_INTEGRATION_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
DEMO_TOKEN = "dev-demo-token-do-not-use-in-production"


def ensure_demo_project(db: Session) -> Integration:
    if db.get(Project, DEMO_PROJECT_ID) is None:
        db.add(Project(
            id=DEMO_PROJECT_ID,
            name="Demo Project",
            description="Auto-created in DEV_MODE for the local dev console.",
        ))
        db.flush()

    integration = db.get(Integration, DEMO_INTEGRATION_ID)
    if integration is None:
        integration = Integration(
            id=DEMO_INTEGRATION_ID,
            project_id=DEMO_PROJECT_ID,
            provider="dev",
            name="Demo Integration",
            credential_hash=hash_token(DEMO_TOKEN),
            status="active",
        )
        db.add(integration)

    db.commit()
    db.refresh(integration)
    return integration
