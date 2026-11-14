"""Forecasting request and response schemas."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    """Forecast data point with uncertainty interval."""
    timestamp: str = Field(..., description="Timestamp in ISO 8601 string format (YYYY-MM-DD)")
    predicted_value: float = Field(..., description="Point forecast value")
    lower_bound: Optional[float] = Field(None, description="Lower prediction interval bound")
    upper_bound: Optional[float] = Field(None, description="Upper prediction interval bound")


class ModelEvaluationMetrics(BaseModel):
    """Out-of-sample chronological evaluation metrics."""
    model_id: str = Field(..., description="Model identifier (e.g., seasonal_naive, ridge_lag, random_forest)")
    model_name: str = Field(..., description="Model display name")
    mae: float = Field(..., description="Mean Absolute Error on holdout test set")
    rmse: float = Field(..., description="Root Mean Squared Error on holdout test set")
    r2_score: Optional[float] = Field(None, description="R2 determination coefficient on holdout")
    test_observations: int = Field(..., description="Number of holdout test points evaluated")
    is_baseline: bool = Field(False, description="Whether this model is a benchmark baseline")


class ForecastRequest(BaseModel):
    """Forecast generation request."""
    variable_id: str = Field(..., description="Target variable identifier")
    horizon_months: int = Field(12, ge=1, le=60, description="Forecast horizon in months")
    model_id: str = Field("ridge_lag", description="Model: persistence | seasonal_naive | linear_drift | ridge_lag | random_forest")
    confidence_level: float = Field(0.95, ge=0.5, le=0.99, description="Prediction interval confidence level")


class ForecastResponse(BaseModel):
    """Forecast response schema."""
    variable_id: str = Field(..., description="Variable identifier")
    unit: str = Field(..., description="Measurement unit")
    region: str = Field(..., description="Geographical region")
    forecast_origin: str = Field(..., description="Last observed historical date used for forecasting")
    horizon_months: int = Field(..., description="Number of months predicted into the future")
    model_id: str = Field(..., description="Selected model identifier")
    model_name: str = Field(..., description="Selected model display name")
    metrics: ModelEvaluationMetrics = Field(..., description="Out-of-sample validation metrics")
    predictions: List[ForecastPoint] = Field(..., description="Future predicted values with bounds")
    limitations: List[str] = Field(default_factory=list, description="Forecasting limitations and caveats")
    artifact_loaded: bool = Field(False, description="Whether forecasts used a persisted production artifact")
    trained_on: Optional[str] = Field(None, description="Fit regime: full_history_production or ephemeral_full_history")
