"""Health check schemas."""

from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health status response schema."""
    status: str = Field("healthy", description="Current service health status")
    project_name: str = Field(..., description="Project name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Running environment")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of the check")
    components: Dict[str, Any] = Field(default_factory=dict, description="Subsystem component statuses")
