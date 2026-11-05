from fastapi import FastAPI

app = FastAPI(
    title="APIlytics Backend",
    description="Telemetry ingestion, storage, detection, and API for APIlytics MVP.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "APIlytics backend is running. Go to /docs for the API."}
