from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health Check Endpoint")
def get_health():
    """Return backend operational status."""
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.APP_ENV,
    )
