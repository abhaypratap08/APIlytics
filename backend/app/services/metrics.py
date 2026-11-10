"""Summary and endpoint aggregation — authored by Abhay Pratap Singh."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.telemetry import TelemetryEvent

ALLOWED_WINDOWS: dict[str, timedelta] = {
    "15m": timedelta(minutes=15),
    "60m": timedelta(minutes=60),
    "24h": timedelta(hours=24),
}


class InvalidWindowError(ValueError):
    pass


def parse_window(window: str) -> timedelta:
    """Convert '15m' / '60m' / '24h' to a timedelta. Raises InvalidWindowError otherwise."""
    if window not in ALLOWED_WINDOWS:
        allowed = ", ".join(ALLOWED_WINDOWS.keys())
        raise InvalidWindowError(f"Unsupported window '{window}'. Use one of: {allowed}.")
    return ALLOWED_WINDOWS[window]


def compute_summary(db: Session, window: str) -> dict:
    """
    Aggregate telemetry over the selected window.

    Error = status_code >= 500 (per API contract).
    p95 uses percentile_cont(0.95) (linear interpolation) on latency_ms.
    Cost = total_requests / 1000 * COST_PER_1000_REQUESTS (demo estimate).
    Empty window: all counts, latencies, and cost return 0.
    """
    delta = parse_window(window)
    now = datetime.now(timezone.utc)
    start = now - delta

    base_filters = (
        TelemetryEvent.timestamp >= start,
        TelemetryEvent.timestamp <= now,
    )

    total = db.scalar(
        select(func.count()).select_from(TelemetryEvent).where(*base_filters)
    ) or 0

    error_count = db.scalar(
        select(func.count())
        .select_from(TelemetryEvent)
        .where(*base_filters, TelemetryEvent.status_code >= 500)
    ) or 0

    avg_latency = db.scalar(
        select(func.avg(TelemetryEvent.latency_ms)).where(*base_filters)
    )

    p95_latency = db.scalar(
        select(
            func.percentile_cont(0.95).within_group(TelemetryEvent.latency_ms)
        ).where(*base_filters)
    )

    error_rate_pct = (error_count / total * 100) if total else 0.0
    estimated_cost = (total / 1000) * settings.COST_PER_1000_REQUESTS

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
        "alerts_count": 0,  # wired up after alerts service is implemented
    }


def compute_endpoints(db: Session, window: str, limit: int = 20) -> dict:
    """
    Aggregate telemetry by (method, route_template) for the selected window.

    Same window, error definition (status_code >= 500), p95 method,
    and cost formula as compute_summary — totals must agree across both endpoints.
    """
    delta = parse_window(window)
    now = datetime.now(timezone.utc)
    start = now - delta

    base_filters = (
        TelemetryEvent.timestamp >= start,
        TelemetryEvent.timestamp <= now,
    )

    count_col = func.count().label("request_count")
    error_col = func.count().filter(TelemetryEvent.status_code >= 500).label("error_count")
    avg_col = func.avg(TelemetryEvent.latency_ms).label("avg_latency")
    p95_col = func.percentile_cont(0.95).within_group(
        TelemetryEvent.latency_ms
    ).label("p95_latency")

    stmt = (
        select(
            TelemetryEvent.method,
            TelemetryEvent.route_template,
            count_col,
            error_col,
            avg_col,
            p95_col,
        )
        .where(*base_filters)
        .group_by(TelemetryEvent.method, TelemetryEvent.route_template)
        .order_by(count_col.desc())
        .limit(limit)
    )

    rows = db.execute(stmt).all()

    items = []
    for method, route_template, request_count, error_count, avg_latency, p95_latency in rows:
        error_rate_pct = (error_count / request_count * 100) if request_count else 0.0
        estimated_cost = (request_count / 1000) * settings.COST_PER_1000_REQUESTS
        items.append(
            {
                "route_template": route_template,
                "method": method,
                "request_count": int(request_count),
                "error_rate_pct": round(error_rate_pct, 2),
                "avg_latency_ms": round(float(avg_latency), 1) if avg_latency is not None else 0.0,
                "p95_latency_ms": round(float(p95_latency), 1) if p95_latency is not None else 0.0,
                "estimated_cost": round(estimated_cost, 2),
                "cost_unit": settings.COST_UNIT,
            }
        )

    return {"window": window, "items": items}
