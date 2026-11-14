"""Time-series observation and query schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ObservationPoint(BaseModel):
    """Single time-series point."""
    timestamp: str = Field(..., description="Timestamp in ISO 8601 string format (YYYY-MM-DD)")
    value: float = Field(..., description="Numeric measurement value in original physical unit")
    display_value: Optional[float] = Field(None, description="Value converted to standard display unit")
    anomaly: Optional[float] = Field(None, description="Anomaly relative to baseline climatology")


class TimeSeriesSummary(BaseModel):
    """Descriptive statistics for a time-series series."""
    count: int = Field(..., description="Number of valid observations")
    mean: float = Field(..., description="Mean value")
    std: float = Field(..., description="Standard deviation")
    min: float = Field(..., description="Minimum value")
    max: float = Field(..., description="Maximum value")
    median: float = Field(..., description="Median value")


class TimeSeriesResponse(BaseModel):
    """Time-series response schema with full provenance."""
    variable_id: str = Field(..., description="Variable identifier")
    variable_name: str = Field(..., description="Display name of variable")
    unit: str = Field(..., description="Source measurement unit")
    display_unit: str = Field(..., description="Display unit")
    region: str = Field(..., description="Geographical coverage region")
    start_date: str = Field(..., description="Earliest observation timestamp")
    end_date: str = Field(..., description="Latest observation timestamp")
    summary: TimeSeriesSummary = Field(..., description="Summary statistics")
    data: List[ObservationPoint] = Field(..., description="Chronological series of observations")
    downsampled: bool = Field(False, description="Whether the series was downsampled for response size")
    stride: int = Field(1, description="Sampling stride applied when downsampled")
