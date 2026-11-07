from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models.telemetry import TelemetryEvent
from app.schemas.telemetry import TelemetryEventIn


def ingest_events(db: Session, events: list[TelemetryEventIn]) -> tuple[int, int]:
    """
    Insert telemetry events, skipping duplicates on event_id.

    Uses PostgreSQL ON CONFLICT DO NOTHING so:
      - duplicates across batches are skipped atomically
      - duplicates within the same batch are also skipped correctly
      - concurrent inserts cannot create double rows

    Returns (accepted_count, duplicate_count).
    """
    if not events:
        return 0, 0

    values = [
        {
            "event_id": e.event_id,
            "timestamp": e.timestamp,
            "method": e.method,
            "route_template": e.route_template,
            "status_code": e.status_code,
            "latency_ms": e.latency_ms,
            "request_size_bytes": e.request_size_bytes,
            "response_size_bytes": e.response_size_bytes,
            "client_id": e.client_id,
            "service_name": e.service_name,
        }
        for e in events
    ]

    stmt = (
        pg_insert(TelemetryEvent)
        .values(values)
        .on_conflict_do_nothing(index_elements=["event_id"])
        .returning(TelemetryEvent.event_id)
    )

    result = db.execute(stmt)
    inserted = len(result.fetchall())
    db.commit()

    return inserted, len(events) - inserted
