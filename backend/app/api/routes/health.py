from fastapi import APIRouter
from app.schemas.common import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint. 
    Does not require database or ML modules to be running.
    """
    return {"status": "ok"}
