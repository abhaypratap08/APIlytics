from fastapi import FastAPI

from app.api.routes import events, health, summary
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Telemetry ingestion, storage, detection, and API for APIlytics MVP.",
)

app.include_router(health.router)
app.include_router(events.router)
app.include_router(summary.router)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "APIlytics backend is running. Go to /docs for the API."}
