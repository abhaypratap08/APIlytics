"""APIlytics backend — created by Abhay Pratap Singh."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routes import alerts, dev, endpoints, health, ingest, projects, sandbox, stream, summary
from app.core.config import settings

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEV_MODE:
        from app.db.session import SessionLocal
        from app.services.dev import ensure_demo_project
        db = SessionLocal()
        try:
            ensure_demo_project(db)
        finally:
            db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Telemetry ingestion, storage, detection, and API for APIlytics MVP.\n\n"
        f"Created by **{settings.CREATOR_NAME}** ({settings.CREATOR_ROLE}).\n\n"
        "Operating mode: **B** — continuous API telemetry monitoring."
    ),
    contact={
        "name": settings.CREATOR_NAME,
        "url": f"https://github.com/{settings.CREATOR_HANDLE}",
    },
    lifespan=lifespan,
)


@app.middleware("http")
async def creator_signature(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Creator"] = settings.CREATOR_NAME
    response.headers["X-Project-Owner"] = settings.CREATOR_ROLE
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Creator", "X-Project-Owner"],
)


app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(dev.router)
app.include_router(summary.router)
app.include_router(endpoints.router)
app.include_router(alerts.router)
app.include_router(projects.router)
app.include_router(sandbox.router)
app.include_router(stream.router)


@app.get("/ui", include_in_schema=False)
def ui():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "APIlytics backend is running. Go to /docs for the API, /ui for the dev console.",
        "creator": settings.CREATOR_NAME,
        "role": settings.CREATOR_ROLE,
        "mode": "B",
        "dev_mode": settings.DEV_MODE,
    }
