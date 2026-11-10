import uuid
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class SandboxSessionCreate(BaseModel):
    target_url: HttpUrl = Field(..., description="The authorized URL to test")

class SandboxSessionOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    target_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
