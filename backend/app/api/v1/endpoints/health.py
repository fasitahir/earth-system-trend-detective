"""Health check endpoint."""

from datetime import datetime, timezone
from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Return application health status and environment configuration."""
    raw_data_exists = settings.RAW_DATA_DIR.exists()
    return HealthResponse(
        status="healthy",
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
        components={
            "api": "operational",
            "raw_data_accessible": raw_data_exists,
            "raw_data_path": str(settings.RAW_DATA_DIR)
        }
    )
