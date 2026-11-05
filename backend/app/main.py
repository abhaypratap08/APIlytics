from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import health

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Telemetry ingestion, storage, detection, and API for APIlytics MVP.",
)

# Register routers
app.include_router(health.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "APIlytics backend is running. Go to /docs for the API."}
