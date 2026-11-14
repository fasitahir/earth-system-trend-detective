"""Schema validation tests."""

import pytest
from pydantic import ValidationError
from backend.app.schemas import (
    HealthResponse,
    VariableMeta,
    DatasetMeta,
    TrendResponse,
    TrendRequest,
    ForecastResponse,
    ForecastRequest,
    ModelEvaluationMetrics,
    ErrorResponse,
)


def test_variable_meta_schema():
    """Verify VariableMeta schema serialization and validation."""
    var = VariableMeta(
        id="air_temperature_2m",
        name="2-Meter Air Temperature",
        source_variable_name="T2M",
        category="Atmosphere",
        unit="K",
        display_unit="°C",
        mission_source="MERRA-2",
        description="Monthly mean 2-meter air temperature",
        frequency="monthly",
        start_date="2001-01-01",
        end_date="2025-12-31",
        total_months=300,
        region="Pakistan",
    )
    assert var.id == "air_temperature_2m"
    assert var.display_unit == "°C"
    assert var.total_months == 300


def test_trend_schemas():
    """Verify TrendRequest and TrendResponse validation."""
    req = TrendRequest(
        variable_id="air_temperature_2m",
        method="mann_kendall",
        alpha=0.05,
        deseasonalize=True
    )
    assert req.alpha == 0.05

    res = TrendResponse(
        dataset_id="merra2_t2m",
        variable_id="air_temperature_2m",
        unit="K",
        display_unit="°C/decade",
        region="Pakistan",
        period_start="2001-01-01",
        period_end="2025-12-31",
        n_observations=300,
        method="mann_kendall",
        trend_direction="increasing",
        slope_per_year=0.025,
        sen_slope_per_year=0.024,
        p_value=0.001,
        significance_level=0.05,
        is_statistically_significant=True,
        assumptions=["Independent observations after pre-whitening"],
        limitations=["Area-averaged polygon masks local microclimates"]
    )
    assert res.is_statistically_significant is True
    assert res.sen_slope_per_year == 0.024


def test_forecast_schemas():
    """Verify forecast schemas."""
    req = ForecastRequest(
        variable_id="air_temperature_2m",
        horizon_months=12,
        model_id="seasonal_naive"
    )
    assert req.horizon_months == 12

    # Negative horizon should fail
    with pytest.raises(ValidationError):
        ForecastRequest(variable_id="air_temp", horizon_months=-5)
