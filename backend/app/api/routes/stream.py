import asyncio
import json
import uuid

from fastapi import APIRouter, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

from app.db.session import SessionLocal
from app.services.metrics import compute_summary, compute_endpoints

router = APIRouter()

async def event_generator(project_id: uuid.UUID, source_type: str | None, request: Request):
    """Yields JSON strings representing the latest metrics every 2 seconds."""
    while True:
        if await request.is_disconnected():
            break

        db = SessionLocal()
        try:
            summary = compute_summary(db, "60m", project_id, source_type)
            endpoints = compute_endpoints(db, "60m", 10, project_id, source_type)
            
            payload = {
                "summary": summary,
                "endpoints": endpoints["items"]
            }
            
            # jsonable_encoder converts datetime/UUIDs to JSON-safe strings
            safe_payload = jsonable_encoder(payload)
            yield f"data: {json.dumps(safe_payload)}\n\n"
            
        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            db.close()

        await asyncio.sleep(2)

@router.get("/api/v1/stream/metrics")
async def stream_metrics(
    request: Request,
    project_id: uuid.UUID = Query(...),
    source_type: str | None = Query(None)
):
    return StreamingResponse(
        event_generator(project_id, source_type, request),
        media_type="text/event-stream"
    )
