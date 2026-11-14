"""Automated tests for Stage 3 Exploratory Data Analysis module."""

import json
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from backend.analytics.eda.analyzer import (
    compute_variable_descriptive_stats,
    compute_correlation_matrices,
    detect_top_extreme_anomalies,
    compute_seasonal_climatology_profile,
)


def test_compute_variable_descriptive_stats():
    """Verify parametric and non-parametric stats calculations."""
    dates = pd.date_range("2001-01-01", periods=100, freq="MS")
    vals = np.linspace(10, 30, 100)
    df = pd.DataFrame({"timestamp": dates, "display_value": vals})

    st = compute_variable_descriptive_stats(df, value_col="display_value")
    assert st["count"] == 100
    assert st["mean"] == pytest.approx(20.0)
    assert st["median"] == pytest.approx(20.0)
    assert st["min"] == pytest.approx(10.0)
    assert st["max"] == pytest.approx(30.0)
    assert st["range"] == pytest.approx(20.0)
    assert st["iqr"] > 0
    assert isinstance(st["skewness"], float)
    assert isinstance(st["kurtosis"], float)


def test_compute_correlation_matrices():
    """Verify Pearson and Spearman correlation matrices on coupled datasets."""
    dates = pd.date_range("2001-01-01", periods=24, freq="MS")
    t2m = np.sin(np.linspace(0, 4 * np.pi, 24)) * 10 + 20
    # Positively correlated variable
    ts = t2m + np.random.normal(0, 0.5, 24)
    # Negatively correlated variable
    rain = -t2m * 0.5 + 30

    wide_df = pd.DataFrame({
        "timestamp": dates,
        "t2m_value": t2m,
        "ts_value": ts,
        "precipitation_value": rain,
        "t2m_anomaly": t2m - 20,
        "ts_anomaly": ts - 20,
        "precipitation_anomaly": rain - 20,
    })

    corr = compute_correlation_matrices(wide_df, value_suffix="_value")
    assert "raw_value_pearson" in corr
    assert "anomaly_pearson" in corr
    assert corr["raw_value_pearson"]["t2m"]["ts"] > 0.8
    assert corr["raw_value_pearson"]["t2m"]["precipitation"] < 0.0


def test_detect_top_extreme_anomalies():
    """Verify top anomaly detection identifies highest magnitude events."""
    dates = pd.date_range("2001-01-01", periods=20, freq="MS")
    anoms = np.zeros(20)
    anoms[5] = 10.5 # Top positive anomaly
    anoms[12] = -8.2 # Top negative anomaly

    df = pd.DataFrame({
        "timestamp": dates,
        "display_value": anoms + 20.0,
        "anomaly": anoms,
        "standardized_anomaly": anoms / 2.0,
    })

    ext = detect_top_extreme_anomalies(df, var_id="test_var", top_n=2)
    assert len(ext["top_positive_anomalies"]) == 2
    assert ext["top_positive_anomalies"][0]["anomaly"] == pytest.approx(10.5)
    assert ext["top_positive_anomalies"][0]["timestamp"] == dates[5].strftime("%Y-%m-%d")
    assert ext["top_negative_anomalies"][0]["anomaly"] == pytest.approx(-8.2)


def test_seasonal_climatology_profile():
    """Verify 12-month climatological profile structure."""
    dates = pd.date_range("2001-01-01", periods=36, freq="MS")
    df = pd.DataFrame({
        "timestamp": dates,
        "display_value": np.random.uniform(10, 30, 36)
    })
    prof = compute_seasonal_climatology_profile(df, value_col="display_value")
    assert len(prof) == 12
    assert "month_name" in prof.columns
    assert "mean" in prof.columns
    assert "std" in prof.columns


def test_eda_artifacts_exist():
    """Verify Stage 3 required metadata files and figures exist."""
    meta_dir = Path("data/metadata")
    fig_dir = Path("docs/figures")

    assert (meta_dir / "eda_descriptive_stats.json").exists()
    assert (meta_dir / "eda_correlations.json").exists()
    assert (meta_dir / "eda_extreme_anomalies.json").exists()

    assert (fig_dir / "historical_timeseries_all.png").exists()
    assert (fig_dir / "seasonal_climatology_all.png").exists()
    assert (fig_dir / "anomaly_timeseries_all.png").exists()
    assert (fig_dir / "correlation_heatmaps.png").exists()
