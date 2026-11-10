import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: str | None
    status: str
    created_at: datetime


class IntegrationCreate(BaseModel):
    provider: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)


class IntegrationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    provider: str
    name: str
    status: str
    last_event_at: datetime | None
    created_at: datetime


class IntegrationCreated(IntegrationOut):
    """Returned only at creation / rotation. Raw credential shown once."""
    credential: str
