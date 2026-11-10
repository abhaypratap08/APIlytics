import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.endpoints import EndpointsResponse
from app.services.metrics import InvalidWindowError, compute_endpoints

router = APIRouter()


@router.get("/api/v1/endpoints", response_model=EndpointsResponse, tags=["Metrics"],
            summary="Per-endpoint aggregates for a project and window")
def get_endpoints(
    window: str = Query("60m", description="One of 15m, 60m, 24h"),
    limit: int = Query(20, ge=1, le=100),
    project_id: uuid.UUID = Query(..., description="Project ID"),
    source_type: str | None = Query(None, description="Filter by 'nginx' or 'browser_sandbox'"),
    db: Session = Depends(get_db),
) -> EndpointsResponse:
    try:
        data = compute_endpoints(db, window, limit, project_id, source_type)
    except InvalidWindowError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return EndpointsResponse(**data)
