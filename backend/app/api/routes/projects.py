import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import generate_token, hash_token
from app.db.session import get_db
from app.models.integration import Integration
from app.models.project import Project
from app.schemas.projects import (
    IntegrationCreate,
    IntegrationCreated,
    IntegrationOut,
    ProjectCreate,
    ProjectOut,
)

router = APIRouter()


# ---------- Projects ----------
@router.post("/api/v1/projects", response_model=ProjectOut, status_code=201, tags=["Projects"])
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    p = Project(name=payload.name, description=payload.description)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/api/v1/projects", response_model=list[ProjectOut], tags=["Projects"])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.get("/api/v1/projects/{project_id}", response_model=ProjectOut, tags=["Projects"])
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    p = db.get(Project, project_id)
    if p is None:
        raise HTTPException(404, "Project not found")
    return p


# ---------- Integrations ----------
@router.post(
    "/api/v1/projects/{project_id}/integrations",
    response_model=IntegrationCreated,
    status_code=201,
    tags=["Integrations"],
    summary="Create integration — returns raw credential ONCE",
)
def create_integration(project_id: uuid.UUID, payload: IntegrationCreate, db: Session = Depends(get_db)):
    if db.get(Project, project_id) is None:
        raise HTTPException(404, "Project not found")
    raw = generate_token()
    i = Integration(
        project_id=project_id,
        provider=payload.provider,
        name=payload.name,
        credential_hash=hash_token(raw),
        status="active",
    )
    db.add(i)
    db.commit()
    db.refresh(i)
    return IntegrationCreated(**IntegrationOut.model_validate(i).model_dump(), credential=raw)


@router.get(
    "/api/v1/projects/{project_id}/integrations",
    response_model=list[IntegrationOut],
    tags=["Integrations"],
)
def list_integrations(project_id: uuid.UUID, db: Session = Depends(get_db)):
    if db.get(Project, project_id) is None:
        raise HTTPException(404, "Project not found")
    return (
        db.query(Integration)
        .filter(Integration.project_id == project_id)
        .order_by(Integration.created_at.desc())
        .all()
    )


@router.post(
    "/api/v1/integrations/{integration_id}/rotate-credential",
    response_model=IntegrationCreated,
    tags=["Integrations"],
    summary="Rotate credential — old token invalidated, new one shown ONCE",
)
def rotate_credential(integration_id: uuid.UUID, db: Session = Depends(get_db)):
    i = db.get(Integration, integration_id)
    if i is None:
        raise HTTPException(404, "Integration not found")
    if i.status != "active":
        raise HTTPException(400, "Only active integrations can rotate credentials")
    raw = generate_token()
    i.credential_hash = hash_token(raw)
    db.commit()
    db.refresh(i)
    return IntegrationCreated(**IntegrationOut.model_validate(i).model_dump(), credential=raw)


@router.post(
    "/api/v1/integrations/{integration_id}/revoke",
    response_model=IntegrationOut,
    tags=["Integrations"],
    summary="Revoke credential — ingestion will reject immediately",
)
def revoke_credential(integration_id: uuid.UUID, db: Session = Depends(get_db)):
    i = db.get(Integration, integration_id)
    if i is None:
        raise HTTPException(404, "Integration not found")
    i.status = "revoked"
    db.commit()
    db.refresh(i)
    return i
