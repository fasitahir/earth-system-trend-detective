"""Automated tests for Stage 2 Data Ingestion & Preprocessing pipeline."""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from backend.data_pipeline.preprocessing.units import (
    kelvin_to_celsius,
    celsius_to_kelvin,
    flux_to_mm_per_day,
    flux_to_monthly_accumulation,
)
from backend.data_pipeline.preprocessing.anomalies import ClimatologyEngine
from backend.data_pipeline.aggregation.temporal import (
    compute_annual_summary,
    compute_seasonal_summary,
)
from backend.data_pipeline.validation.validator import validate_processed_dataframe


def test_unit_conversions():
    """Verify Kelvin to Celsius and flux conversions."""
    # Kelvin to Celsius
    assert kelvin_to_celsius(273.15) == pytest.approx(0.0)
    assert kelvin_to_celsius(300.0) == pytest.approx(26.85)
    assert celsius_to_kelvin(0.0) == pytest.approx(273.15)

    # Flux to mm/day (1 kg m-2 s-1 = 86,400 mm/day)
    flux = 1e-5 # kg m-2 s-1
    expected_mm_day = 1e-5 * 86400.0 # 0.864 mm/day
    assert flux_to_mm_per_day(flux) == pytest.approx(expected_mm_day)

    # Monthly accumulation (31-day January)
    timestamps = pd.Series([pd.Timestamp("2021-01-01")])
    fluxes = pd.Series([flux])
    monthly_mm = flux_to_monthly_accumulation(fluxes, timestamps)
    assert monthly_mm.iloc[0] == pytest.approx(expected_mm_day * 31)


def test_climatology_and_anomalies():
    """Verify baseline climatology calculation and anomaly decomposition."""
    # Create 2 years of monthly synthetic data with known cycle
    dates = pd.date_range("2001-01-01", "2002-12-01", freq="MS")
    # Base pattern repeated twice
    pattern = [10, 12, 15, 20, 25, 30, 32, 31, 28, 22, 16, 11] * 2
    df = pd.DataFrame({"timestamp": dates, "value": pattern})

    engine = ClimatologyEngine(baseline_start="2001-01-01", baseline_end="2002-12-31")
    clim = engine.fit_climatology(df, value_col="value")

    assert len(clim) == 12
    assert clim.loc[1, "climatology_mean"] == pytest.approx(10.0)
    assert clim.loc[6, "climatology_mean"] == pytest.approx(30.0)

    # Decompose
    res = engine.calculate_anomalies(df, value_col="value", climatology=clim)
    assert "anomaly" in res.columns
    assert "standardized_anomaly" in res.columns
    # With identical years, anomalies should be exactly 0
    assert np.allclose(res["anomaly"], 0.0)


def test_temporal_aggregation():
    """Verify annual and seasonal summaries."""
    dates = pd.date_range("2001-01-01", "2002-12-01", freq="MS")
    vals = np.ones(len(dates)) * 5.0
    df = pd.DataFrame({"timestamp": dates, "display_value": vals})

    annual = compute_annual_summary(df, var_id="t2m", value_col="display_value")
    assert len(annual) == 2
    assert annual.iloc[0]["annual_mean"] == pytest.approx(5.0)
    assert annual.iloc[0]["is_complete_year"] == True

    seasonal = compute_seasonal_summary(df, var_id="t2m", value_col="display_value")
    assert not seasonal.empty
    assert "season" in seasonal.columns


def test_validator_detects_bounds():
    """Verify validator catches physical outliers or invalid structures."""
    dates = pd.date_range("2001-01-01", periods=12, freq="MS")
    valid_df = pd.DataFrame({
        "timestamp": dates,
        "variable_id": ["t2m"] * 12,
        "region": ["Pakistan"] * 12,
        "dataset_id": ["MERRA-2"] * 12,
        "raw_value": [290.0] * 12,
        "source_unit": ["K"] * 12,
        "display_value": [16.85] * 12,
        "display_unit": ["°C"] * 12,
        "climatology_mean": [16.85] * 12,
        "climatology_std": [1.0] * 12,
        "anomaly": [0.0] * 12,
        "standardized_anomaly": [0.0] * 12,
    })

    ok, errors = validate_processed_dataframe(valid_df, "t2m")
    assert ok is True
    assert len(errors) == 0

    # Corrupt with extreme physically impossible temperature (500 K = 227 °C)
    bad_df = valid_df.copy()
    bad_df.loc[0, "raw_value"] = 500.0
    ok, errors = validate_processed_dataframe(bad_df, "t2m")
    assert ok is False
    assert any("exceed bounds" in e for e in errors)


def test_processed_files_exist_and_valid():
    """Verify all canonical processed files in data/processed exist and are non-empty."""
    processed_dir = Path("data/processed")
    expected_vars = [
        "t2m",
        "ts",
        "precipitation",
        "evapotranspiration",
        "soil_moisture_0_10cm",
        "soil_moisture_10_40cm",
    ]

    for v in expected_vars:
        parquet_file = processed_dir / f"{v}.parquet"
        csv_file = processed_dir / f"{v}.csv"
        assert parquet_file.exists(), f"Missing {parquet_file}"
        assert csv_file.exists(), f"Missing {csv_file}"

        df = pd.read_parquet(parquet_file)
        assert len(df) in (297, 300)
        assert df["raw_value"].notna().all()
        assert df["display_value"].notna().all()
        assert df["anomaly"].notna().all()

    # Multi-variable dataset
    multi_file = processed_dir / "earth_system_pakistan_monthly.parquet"
    assert multi_file.exists()
    multi_df = pd.read_parquet(multi_file)
    assert len(multi_df) == 297
    assert multi_df["timestamp"].is_monotonic_increasing
    assert multi_df.isna().sum().sum() == 0
