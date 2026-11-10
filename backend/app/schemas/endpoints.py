from pydantic import BaseModel


class EndpointItem(BaseModel):
    route_template: str
    method: str
    request_count: int
    error_rate_pct: float
    avg_latency_ms: float
    p95_latency_ms: float
    estimated_cost: float
    cost_unit: str


class EndpointsResponse(BaseModel):
    window: str
    items: list[EndpointItem]
