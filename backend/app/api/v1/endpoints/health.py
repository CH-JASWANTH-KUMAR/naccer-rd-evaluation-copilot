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


@router.get("/ai/status", summary="AI Provider Status Endpoint")
def get_ai_status():
    """Return safe AI provider status without exposing API keys or secrets."""
    from app.services.ai_analysis_provider import AIProviderFactory
    provider = AIProviderFactory.get_provider()
    return {
        "configured_provider": settings.AI_PROVIDER,
        "configured_model": settings.AI_MODEL,
        "active_provider": provider.provider_name,
        "active_model": provider.model_name,
        "prompt_version": provider.prompt_version,
        "available": True,
        "fallback_available": True,
    }


@router.get("/health/readiness", summary="Subsystem Readiness Check Endpoint")
def get_readiness():
    """Return operational subsystem readiness status."""
    from app.services.reviewer_operations import ReviewerOperationsService
    return ReviewerOperationsService.get_system_readiness()
