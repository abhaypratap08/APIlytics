from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TelemetryEventIn(BaseModel):
    event_id: UUID
    timestamp: datetime
    method: str = Field(..., min_length=1, max_length=10)
    route_template: str = Field(..., min_length=1, max_length=512)
    status_code: Optional[int] = Field(default=None, ge=100, le=599)
    latency_ms: float = Field(..., ge=0)
    
    # Source fields
    source_type: str = Field(..., min_length=1, max_length=32)
    origin_host: Optional[str] = Field(default=None, max_length=255)
    resource_type: Optional[str] = Field(default=None, max_length=32)
    failure_kind: Optional[str] = Field(default=None, max_length=64)

    # Sizes & Metadata
    request_size_bytes: Optional[int] = Field(default=None, ge=0)
    response_size_bytes: Optional[int] = Field(default=None, ge=0)
    client_id: Optional[str] = Field(default=None, max_length=128)
    service_name: Optional[str] = Field(default=None, max_length=128)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_have_tz(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must include timezone information")
        return v

    @field_validator("method")
    @classmethod
    def method_uppercase(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("route_template")
    @classmethod
    def route_must_start_with_slash(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("route_template must start with '/'")
        return v


class TelemetryBatchIn(BaseModel):
    events: list[TelemetryEventIn] = Field(..., min_length=1, max_length=500)


class IngestResponse(BaseModel):
    accepted: int
    duplicates: int
