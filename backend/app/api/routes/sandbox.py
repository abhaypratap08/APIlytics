import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.ssrf import is_safe_url
from app.db.session import get_db
from app.models.project import Project
from app.models.sandbox import SandboxSession
from app.schemas.sandbox import SandboxSessionCreate, SandboxSessionOut
from app.schemas.telemetry import IngestResponse, TelemetryBatchIn
from app.services.events import ingest_events

router = APIRouter()

@router.post(
    "/api/v1/projects/{project_id}/sandbox-sessions",
    response_model=SandboxSessionOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Sandbox"],
    summary="Start a new isolated browser session"
)
def create_sandbox_session(
    project_id: uuid.UUID,
    payload: SandboxSessionCreate,
    db: Session = Depends(get_db)
):
    if db.get(Project, project_id) is None:
        raise HTTPException(404, "Project not found")

    url_str = str(payload.target_url)
    safe, reason = is_safe_url(url_str)
    if not safe:
        raise HTTPException(status_code=400, detail=f"SSRF Protection: {reason}")

    session = SandboxSession(
        project_id=project_id,
        target_url=url_str,
        status="active"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get(
    "/api/v1/sandbox-sessions/{session_id}",
    response_model=SandboxSessionOut,
    tags=["Sandbox"],
    summary="Get the status of a sandbox session"
)
def get_sandbox_session(session_id: uuid.UUID, db: Session = Depends(get_db)):
    session = db.get(SandboxSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session

@router.post(
    "/api/v1/sandbox-sessions/{session_id}/stop",
    response_model=SandboxSessionOut,
    tags=["Sandbox"],
    summary="Stop an active sandbox session"
)
def stop_sandbox_session(session_id: uuid.UUID, db: Session = Depends(get_db)):
    session = db.get(SandboxSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    session.status = "stopped"
    db.commit()
    db.refresh(session)
    return session

@router.post(
    "/api/v1/internal/sandbox-sessions/{session_id}/events",
    response_model=IngestResponse,
    tags=["Sandbox"],
    summary="Internal endpoint for Playwright worker to push captured events"
)
def ingest_sandbox_events(
    session_id: uuid.UUID,
    payload: TelemetryBatchIn,
    db: Session = Depends(get_db)
):
    # TODO: Add service-to-service authentication here before production.
    session = db.get(SandboxSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if session.status != "active":
        raise HTTPException(400, "Session is not active")

    for e in payload.events:
        if e.source_type != "browser_sandbox":
            raise HTTPException(400, "Events for a sandbox session must have source_type='browser_sandbox'")

    accepted, duplicates = ingest_events(
        db=db,
        events=payload.events,
        project_id=session.project_id,
        integration_id=None,
        sandbox_session_id=session.id
    )
    return IngestResponse(accepted=accepted, duplicates=duplicates)
