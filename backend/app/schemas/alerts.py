from datetime import datetime

from pydantic import BaseModel


class AlertItem(BaseModel):
    id: str
    type: str
    severity: str
    method: str
    route_template: str
    title: str
    message: str
    recommendation: str
    generated_at: datetime


class AlertsResponse(BaseModel):
    window: str
    items: list[AlertItem]
