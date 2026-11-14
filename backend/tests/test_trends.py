"""Automated tests for Stage 4 Statistical Trend Detection module."""

import pytest
import numpy as np
import pandas as pd
from httpx import AsyncClient, ASGITransport
import pymannkendall as mk

from backend.analytics.trend_detection.methods import (
    linear_regression_trend,
    mann_kendall_test,
    sens_slope_estimator,
    seasonal_mann_kendall_test,
    modified_mann_kendall_yue_pilon,
)
from backend.analytics.trend_detection.engine import TrendAnalysisEngine
from backend.app.main import app


def test_synthetic_increasing_trend():
    """Verify statistical methods detect known positive monotonic trend."""
    np.random.seed(42)
    n = 100
    x = np.arange(n)
    y = 0.1 * x + np.random.normal(0, 0.5, n)

    # Mann-Kendall
    res_mk = mann_kendall_test(y, alpha=0.05)
    assert res_mk["trend_direction"] == "increasing"
    assert res_mk["p_value"] < 0.001
    assert res_mk["is_statistically_significant"] is True
    assert res_mk["sen_slope_per_year"] > 0

    # Linear regression
    res_lr = linear_regression_trend(x / 12.0, y, alpha=0.05)
    assert res_lr["trend_direction"] == "increasing"
    assert res_lr["p_value"] < 0.001


def test_synthetic_decreasing_trend():
    """Verify statistical methods detect known negative monotonic trend."""
    np.random.seed(42)
    n = 100
    x = np.arange(n)
    y = -0.1 * x + np.random.normal(0, 0.5, n)

    res_mk = mann_kendall_test(y, alpha=0.05)
    assert res_mk["trend_direction"] == "decreasing"
    assert res_mk["p_value"] < 0.001
    assert res_mk["is_statistically_significant"] is True


def test_synthetic_stationary_white_noise():
    """Verify statistical methods do not detect false trend on stationary white noise."""
    np.random.seed(42)
    n = 100
    y = np.random.normal(0, 1.0, n)

    res_mk = mann_kendall_test(y, alpha=0.05)
    assert res_mk["trend_direction"] == "no_detected_trend"
    assert res_mk["p_value"] > 0.05
    assert res_mk["is_statistically_significant"] is False


def test_cross_validation_with_pymannkendall():
    """Cross-validate native Mann-Kendall implementation against third-party pymannkendall package."""
    np.random.seed(123)
    y = np.cumsum(np.random.normal(0.05, 1.0, 80)) # Random walk with positive drift

    # Native implementation
    native_res = mann_kendall_test(y, alpha=0.05)

    # PyMannKendall reference
    pmk_res = mk.original_test(y, alpha=0.05)

    # Verify S statistic, z, and p-value match closely
    assert native_res["s_statistic"] == pmk_res.s
    assert native_res["z_statistic"] == pytest.approx(pmk_res.z, rel=1e-3)
    assert native_res["p_value"] == pytest.approx(pmk_res.p, rel=1e-3)
    assert native_res["trend_direction"] == ("increasing" if pmk_res.trend == "increasing" else "decreasing")


def test_seasonal_mann_kendall_synthetic():
    """Verify seasonal Mann-Kendall on strong seasonal series with positive interannual trend."""
    np.random.seed(42)
    n_years = 15
    period = 12
    months = np.tile(np.arange(12), n_years)
    years = np.repeat(np.arange(n_years), period)

    # Seasonal pattern + upward yearly trend + noise
    seasonal_cycle = np.sin(2 * np.pi * months / 12.0) * 10
    trend = 0.5 * years
    noise = np.random.normal(0, 1.0, n_years * period)
    y = seasonal_cycle + trend + noise

    res_smk = seasonal_mann_kendall_test(y, period=12, alpha=0.05)
    assert res_smk["trend_direction"] == "increasing"
    assert res_smk["p_value"] < 0.001
    assert res_smk["sen_slope_per_year"] == pytest.approx(0.5, abs=0.15)


@pytest.mark.asyncio
async def test_api_trend_endpoint():
    """Verify POST /api/v1/analysis/trend endpoint executes analysis and returns TrendResponse schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test precipitation trend
        payload = {
            "variable_id": "precipitation",
            "method": "mann_kendall",
            "deseasonalize": True,
            "alpha": 0.05
        }
        response = await client.post("/api/v1/analysis/trend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["variable_id"] == "precipitation"
        assert data["trend_direction"] == "increasing"
        assert data["is_statistically_significant"] is True
        assert data["sen_slope_per_year"] is not None
        assert data["confidence_interval"]["lower"] is not None
        assert data["confidence_interval"]["upper"] is not None

        # 2. Test t2m linear regression
        payload_t2m = {
            "variable_id": "t2m",
            "method": "linear_regression",
            "deseasonalize": True,
            "alpha": 0.05
        }
        res_t2m = await client.post("/api/v1/analysis/trend", json=payload_t2m)
        assert res_t2m.status_code == 200
        data_t2m = res_t2m.json()
        assert data_t2m["variable_id"] == "t2m"
        assert data_t2m["method"] == "linear_regression"
        assert data_t2m["slope_per_year"] is not None

        # 3. Test non-existent variable returns 404
        payload_bad = {
            "variable_id": "non_existent_var",
            "method": "mann_kendall"
        }
        res_bad = await client.post("/api/v1/analysis/trend", json=payload_bad)
        assert res_bad.status_code == 404
