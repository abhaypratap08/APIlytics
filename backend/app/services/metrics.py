"""Summary and endpoint aggregation — authored by Abhay Pratap Singh.

All queries are scoped to a single project_id. Mode B: never aggregate
across projects — a project_id missing from the filter is a bug.
"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.intelligence.cost import estimate_cost
from app.models.telemetry import TelemetryEvent

ALLOWED_WINDOWS: dict[str, timedelta] = {
    "15m": timedelta(minutes=15),
    "60m": timedelta(minutes=60),
    "24h": timedelta(hours=24),
}


class InvalidWindowError(ValueError):
    pass


def parse_window(window: str) -> timedelta:
    if window not in ALLOWED_WINDOWS:
        allowed = ", ".join(ALLOWED_WINDOWS.keys())
        raise InvalidWindowError(f"Unsupported window '{window}'. Use one of: {allowed}.")
    return ALLOWED_WINDOWS[window]


def _window_filters(project_id: uuid.UUID, start: datetime, end: datetime, source_type: str | None = None):
    filters = [
        TelemetryEvent.project_id == project_id,
        TelemetryEvent.timestamp >= start,
        TelemetryEvent.timestamp <= end,
    ]
    if source_type:
        filters.append(TelemetryEvent.source_type == source_type)
    return tuple(filters)


def compute_summary(db: Session, window: str, project_id: uuid.UUID, source_type: str | None = None) -> dict:
    delta = parse_window(window)
    now = datetime.now(timezone.utc)
    start = now - delta
    base_filters = _window_filters(project_id, start, now, source_type)

    total = db.scalar(select(func.count()).select_from(TelemetryEvent).where(*base_filters)) or 0
    error_count = db.scalar(
        select(func.count()).select_from(TelemetryEvent).where(*base_filters, TelemetryEvent.status_code >= 500)
    ) or 0
    avg_latency = db.scalar(select(func.avg(TelemetryEvent.latency_ms)).where(*base_filters))
    p95_latency = db.scalar(
        select(func.percentile_cont(0.95).within_group(TelemetryEvent.latency_ms)).where(*base_filters)
    )

    error_rate_pct = (error_count / total * 100) if total else 0.0
    estimated_cost = estimate_cost(total, settings.COST_PER_1000_REQUESTS)

    return {
        "window": window,
        "generated_at": now,
        "total_requests": int(total),
        "error_count": int(error_count),
        "error_rate_pct": round(error_rate_pct, 2),
        "avg_latency_ms": round(float(avg_latency), 1) if avg_latency is not None else 0.0,
        "p95_latency_ms": round(float(p95_latency), 1) if p95_latency is not None else 0.0,
        "estimated_cost": round(estimated_cost, 2),
        "cost_unit": settings.COST_UNIT,
        "alerts_count": _count_alerts(db, window, project_id),
    }


def compute_endpoints(db: Session, window: str, limit: int, project_id: uuid.UUID, source_type: str | None = None) -> dict:
    delta = parse_window(window)
    now = datetime.now(timezone.utc)
    start = now - delta
    base_filters = _window_filters(project_id, start, now, source_type)

    count_col = func.count().label("request_count")
    error_col = func.count().filter(TelemetryEvent.status_code >= 500).label("error_count")
    avg_col = func.avg(TelemetryEvent.latency_ms).label("avg_latency")
    p95_col = func.percentile_cont(0.95).within_group(TelemetryEvent.latency_ms).label("p95_latency")

    stmt = (
        select(
            TelemetryEvent.method, TelemetryEvent.route_template,
            count_col, error_col, avg_col, p95_col,
        )
        .where(*base_filters)
        .group_by(TelemetryEvent.method, TelemetryEvent.route_template)
        .order_by(count_col.desc())
        .limit(limit)
    )
    rows = db.execute(stmt).all()

    items = []
    for method, route, rc, ec, avg, p95 in rows:
        items.append({
            "route_template": route,
            "method": method,
            "request_count": int(rc),
            "error_rate_pct": round((ec / rc * 100) if rc else 0.0, 2),
            "avg_latency_ms": round(float(avg), 1) if avg is not None else 0.0,
            "p95_latency_ms": round(float(p95), 1) if p95 is not None else 0.0,
            "estimated_cost": round(estimate_cost(rc, settings.COST_PER_1000_REQUESTS), 2),
            "cost_unit": settings.COST_UNIT,
        })
    return {"window": window, "items": items}


def _count_alerts(db: Session, window: str, project_id: uuid.UUID) -> int:
    from app.services.alerts import compute_alerts
    return len(compute_alerts(db, window, project_id, limit=1000)["items"])
