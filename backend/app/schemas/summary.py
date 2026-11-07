from datetime import datetime

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    window: str
    generated_at: datetime
    total_requests: int
    error_count: int
    error_rate_pct: float
    avg_latency_ms: float
    p95_latency_ms: float
    estimated_cost: float
    cost_unit: str
    alerts_count: int
