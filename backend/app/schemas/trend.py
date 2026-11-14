"""Trend detection schemas matching EarthScope scientific specification."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ConfidenceInterval(BaseModel):
    """Confidence interval for trend slope."""
    lower: Optional[float] = Field(None, description="Lower bound of slope")
    upper: Optional[float] = Field(None, description="Upper bound of slope")


class TrendRequest(BaseModel):
    """Trend analysis request parameters."""
    variable_id: str = Field(..., description="Target variable identifier")
    method: str = Field("mann_kendall", description="Trend method: mann_kendall | linear_regression | seasonal_mann_kendall")
    start_date: Optional[str] = Field(None, description="Optional start date filter (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Optional end date filter (YYYY-MM-DD)")
    alpha: float = Field(0.05, ge=0.001, le=0.2, description="Significance level alpha")
    deseasonalize: bool = Field(True, description="Whether to remove seasonal climatological cycle first")


class TrendResponse(BaseModel):
    """Trend analysis response matching EarthScope scientific contract."""
    dataset_id: str = Field(..., description="Source dataset identifier")
    variable_id: str = Field(..., description="Variable identifier")
    unit: str = Field(..., description="Source unit")
    display_unit: str = Field(..., description="Display unit for slope")
    region: str = Field(..., description="Region identifier (e.g., Pakistan)")
    period_start: str = Field(..., description="Period start date (YYYY-MM-DD)")
    period_end: str = Field(..., description="Period end date (YYYY-MM-DD)")
    n_observations: int = Field(..., description="Count of observations analyzed")
    method: str = Field(..., description="Statistical method applied")
    trend_direction: str = Field(..., description="increasing | decreasing | no_detected_trend")
    slope_per_year: Optional[float] = Field(None, description="Linear slope per year")
    sen_slope_per_year: Optional[float] = Field(None, description="Sen's non-parametric slope per year")
    p_value: Optional[float] = Field(None, description="Statistical p-value")
    confidence_interval: ConfidenceInterval = Field(default_factory=ConfidenceInterval)
    significance_level: float = Field(0.05, description="Significance threshold alpha")
    is_statistically_significant: bool = Field(..., description="Whether p_value < significance_level")
    multiple_testing_adjusted_p_value: Optional[float] = Field(None, description="Adjusted p-value if applicable")
    assumptions: List[str] = Field(default_factory=list, description="Method assumptions")
    limitations: List[str] = Field(default_factory=list, description="Known limitations")
