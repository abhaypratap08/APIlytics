"""Dev-only routes (404 when DEV_MODE is false)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.telemetry import IngestResponse, TelemetryBatchIn
from app.services.dev import DEMO_INTEGRATION_ID, DEMO_PROJECT_ID, ensure_demo_project
from app.services.events import ingest_events

router = APIRouter()


def _require_dev_mode() -> None:
    if not settings.DEV_MODE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@router.get(
    "/api/v1/dev/context",
    dependencies=[Depends(_require_dev_mode)],
    tags=["Dev"],
    summary="Demo project/integration IDs (dev only)",
)
def dev_context(db: Session = Depends(get_db)):
    ensure_demo_project(db)
    return {
        "project_id": str(DEMO_PROJECT_ID),
        "integration_id": str(DEMO_INTEGRATION_ID),
    }


@router.post(
    "/api/v1/dev/ingest",
    response_model=IngestResponse,
    dependencies=[Depends(_require_dev_mode)],
    tags=["Dev"],
    summary="Unauthenticated ingest into demo project (dev only)",
)
def dev_ingest(payload: TelemetryBatchIn, db: Session = Depends(get_db)) -> IngestResponse:
    ensure_demo_project(db)
    accepted, duplicates = ingest_events(
        db, payload.events, DEMO_PROJECT_ID, DEMO_INTEGRATION_ID
    )
    return IngestResponse(accepted=accepted, duplicates=duplicates)
