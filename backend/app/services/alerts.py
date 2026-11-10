"""Alerts adapter — authored by Abhay Pratap Singh.

Fetches current + baseline endpoint aggregates from Postgres, calls
Hariom's detector, and serializes stable findings.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.intelligence.rules import EndpointAggregate, detect_findings
from app.models.telemetry import TelemetryEvent
from app.services.metrics import parse_window


def _aggregate_window(db: Session, start: datetime, end: datetime) -> list[EndpointAggregate]:
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
            count_col, error_col, avg_col, p95_col,
        )
        .where(TelemetryEvent.timestamp >= start, TelemetryEvent.timestamp <= end)
        .group_by(TelemetryEvent.method, TelemetryEvent.route_template)
    )
    rows = db.execute(stmt).all()
    return [
        EndpointAggregate(
            method=method,
            route_template=route,
            request_count=int(rc),
            error_count=int(ec),
            avg_latency_ms=float(avg) if avg is not None else 0.0,
            p95_latency_ms=float(p95) if p95 is not None else 0.0,
        )
        for method, route, rc, ec, avg, p95 in rows
    ]


def compute_alerts(db: Session, window: str, limit: int = 50) -> dict:
    delta = parse_window(window)
    now = datetime.now(timezone.utc)
    start = now - delta
    baseline_start = start - delta

    current = _aggregate_window(db, start, now)
    baseline = _aggregate_window(db, baseline_start, start)

    findings = detect_findings(current, baseline, window)
    items = [
        {
            "id": f.id,
            "type": f.type,
            "severity": f.severity,
            "method": f.method,
            "route_template": f.route_template,
            "title": f.title,
            "message": f.message,
            "recommendation": f.recommendation,
            "generated_at": now,
        }
        for f in findings[:limit]
    ]
    return {"window": window, "items": items}
