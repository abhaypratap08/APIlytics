import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.summary import SummaryResponse
from app.services.metrics import InvalidWindowError, compute_summary

router = APIRouter()


@router.get("/api/v1/summary", response_model=SummaryResponse, tags=["Metrics"],
            summary="Project-scoped aggregate metrics for a time window")
def get_summary(
    window: str = Query("60m", description="One of 15m, 60m, 24h"),
    project_id: uuid.UUID = Query(..., description="Project ID (required, Mode B tenant scope)"),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    try:
        data = compute_summary(db, window, project_id)
    except InvalidWindowError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return SummaryResponse(**data)
