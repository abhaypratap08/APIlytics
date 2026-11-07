from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.telemetry import IngestResponse, TelemetryBatchIn
from app.services.events import ingest_events

router = APIRouter()


@router.post(
    "/api/v1/events",
    response_model=IngestResponse,
    status_code=200,
    tags=["Events"],
    summary="Ingest a batch of telemetry events",
)
def create_events(payload: TelemetryBatchIn, db: Session = Depends(get_db)) -> IngestResponse:
    accepted, duplicates = ingest_events(db, payload.events)
    return IngestResponse(accepted=accepted, duplicates=duplicates)
