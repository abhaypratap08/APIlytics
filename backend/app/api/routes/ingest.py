"""Authenticated telemetry ingestion (Mode B path)."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_integration
from app.db.session import get_db
from app.models.integration import Integration
from app.schemas.telemetry import IngestResponse, TelemetryBatchIn
from app.services.events import ingest_events

router = APIRouter()


@router.post(
    "/api/v1/ingest/events",
    response_model=IngestResponse,
    tags=["Ingestion"],
    summary="Ingest a batch of telemetry events (bearer token required)",
)
def ingest_batch(
    payload: TelemetryBatchIn,
    integration: Integration = Depends(get_current_integration),
    db: Session = Depends(get_db),
) -> IngestResponse:
    accepted, duplicates = ingest_events(
        db, payload.events, integration.project_id, integration.id
    )
    if accepted > 0:
        integration.last_event_at = datetime.now(timezone.utc)
        db.commit()
    return IngestResponse(accepted=accepted, duplicates=duplicates)
