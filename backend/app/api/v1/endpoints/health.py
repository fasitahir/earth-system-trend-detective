"""Health check endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter

from backend.app.core.config import settings
from backend.app.schemas.health import HealthResponse
from backend.ml.training.persistence import ModelRegistry

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Return application health status and environment configuration."""
    registry = ModelRegistry()
    saved_models = registry.list_saved_variables()
    processed_exists = settings.PROCESSED_DATA_DIR.exists()
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
            "raw_data_path": str(settings.RAW_DATA_DIR),
            "processed_data_accessible": processed_exists,
            "saved_model_variables": saved_models,
            "saved_model_count": len(saved_models),
        },
    )
