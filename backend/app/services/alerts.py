"""Alerts adapter — authored by Abhay Pratap Singh.

Fetches current + baseline aggregates for a single project, calls
Hariom's detector, serializes findings.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.intelligence.rules import EndpointAggregate, detect_findings
from app.models.telemetry import TelemetryEvent
from app.services.metrics import parse_window


def _aggregate_window(db: Session, start: datetime, end: datetime, project_id: uuid.UUID) -> list[EndpointAggregate]:
    count_col = func.count().label("rc")
    error_col = func.count().filter(TelemetryEvent.status_code >= 500).label("ec")
    avg_col = func.avg(TelemetryEvent.latency_ms).label("avg_l")
    p95_col = func.percentile_cont(0.95).within_group(TelemetryEvent.latency_ms).label("p95_l")

    stmt = (
        select(TelemetryEvent.method, TelemetryEvent.route_template, count_col, error_col, avg_col, p95_col)
        .where(
            TelemetryEvent.project_id == project_id,
            TelemetryEvent.timestamp >= start,
            TelemetryEvent.timestamp <= end,
        )
        .group_by(TelemetryEvent.method, TelemetryEvent.route_template)
    )
    rows = db.execute(stmt).all()
    return [
        EndpointAggregate(
            method=m, route_template=r,
            request_count=int(rc), error_count=int(ec),
            avg_latency_ms=float(avg) if avg is not None else 0.0,
            p95_latency_ms=float(p95) if p95 is not None else 0.0,
        )
        for m, r, rc, ec, avg, p95 in rows
    ]


def compute_alerts(db: Session, window: str, project_id: uuid.UUID, limit: int = 50) -> dict:
    delta = parse_window(window)
    now = datetime.now(timezone.utc)
    start = now - delta
    baseline_start = start - delta

    current = _aggregate_window(db, start, now, project_id)
    baseline = _aggregate_window(db, baseline_start, start, project_id)
    findings = detect_findings(current, baseline, window)

    items = [
        {
            "id": f.id, "type": f.type, "severity": f.severity,
            "method": f.method, "route_template": f.route_template,
            "title": f.title, "message": f.message,
            "recommendation": f.recommendation, "generated_at": now,
        }
        for f in findings[:limit]
    ]
    return {"window": window, "items": items}
