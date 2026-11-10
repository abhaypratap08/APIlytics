from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alerts import AlertsResponse
from app.services.alerts import compute_alerts
from app.services.metrics import InvalidWindowError

router = APIRouter()


@router.get(
    "/api/v1/alerts",
    response_model=AlertsResponse,
    tags=["Detection"],
    summary="Rule-based findings for a time window",
)
def get_alerts(
    window: str = Query("60m", description="One of 15m, 60m, 24h"),
    limit: int = Query(50, ge=1, le=200, description="Max findings to return (1-200)"),
    db: Session = Depends(get_db),
) -> AlertsResponse:
    try:
        data = compute_alerts(db, window, limit)
    except InvalidWindowError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return AlertsResponse(**data)
