"""Automated tests for Stage 5 Forecasting & Machine Learning module."""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd
from httpx import AsyncClient, ASGITransport

from backend.ml.features.pipeline import TimeSeriesFeatureExtractor
from backend.ml.training.models import (
    PersistenceModel,
    SeasonalNaiveModel,
    LinearDriftModel,
    RidgeForecastModel,
    RandomForestForecastModel,
)
from backend.ml.evaluation.validator import ChronologicalHoldoutEvaluator
from backend.ml.inference.service import ForecastInferenceService
from backend.app.main import app


def test_feature_extractor_no_leakage():
    """Verify that lag features do not leak future information."""
    dates = pd.date_range("2001-01-01", periods=36, freq="MS")
    vals = np.arange(36, dtype=float)
    df = pd.DataFrame({"timestamp": dates, "display_value": vals})

    fe = TimeSeriesFeatureExtractor(lags=[1, 2, 12], rolling_windows=[3])
    X, y, names = fe.create_features(df, target_col="display_value")

    assert "lag_1" in names
    assert "lag_2" in names
    assert "lag_12" in names
    assert len(X) == len(y)

    # First row of y corresponds to index 12 (value = 12.0)
    assert y.iloc[0] == 12.0
    # Lag 1 of this row must be 11.0, lag 2 must be 10.0, lag 12 must be 0.0
    assert X.iloc[0]["lag_1"] == 11.0
    assert X.iloc[0]["lag_2"] == 10.0
    assert X.iloc[0]["lag_12"] == 0.0


def test_model_ladder_training_and_inference():
    """Verify all 5 models in the ladder can fit and predict correctly."""
    y_train = pd.Series([10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 32.0, 31.0, 28.0, 22.0, 16.0, 11.0])
    horizon = 6

    # 1. Persistence
    pers = PersistenceModel()
    pers.fit(y_train)
    p_pers = pers.predict(horizon)
    assert len(p_pers) == horizon
    assert p_pers[0] == 11.0

    # 2. Seasonal Naive
    sn = SeasonalNaiveModel(period=12)
    sn.fit(y_train)
    p_sn = sn.predict(horizon)
    assert len(p_sn) == horizon
    assert p_sn[0] == 10.0 # Repeated from index 0

    # 3. Linear Drift
    drift = LinearDriftModel()
    drift.fit(y_train)
    p_drift = drift.predict(horizon)
    assert len(p_drift) == horizon

    # 4. ML Models
    X_dummy = pd.DataFrame({"feat1": np.arange(12), "feat2": np.arange(12) * 2})
    ridge = RidgeForecastModel(alpha=1.0)
    ridge.fit(X_dummy, y_train)
    p_ridge = ridge.predict(X_dummy.iloc[:horizon])
    assert len(p_ridge) == horizon

    rf = RandomForestForecastModel(n_estimators=10, max_depth=3)
    rf.fit(X_dummy, y_train)
    p_rf = rf.predict(X_dummy.iloc[:horizon])
    assert len(p_rf) == horizon


def test_chronological_holdout_evaluator():
    """Verify chronological holdout evaluation computes valid metrics."""
    dates = pd.date_range("2010-01-01", "2024-12-01", freq="MS")
    n = len(dates)
    # Seasonal wave + trend
    months = dates.month.values
    vals = 20.0 + np.sin(2 * np.pi * months / 12.0) * 8.0 + (np.arange(n) / 12.0) * 0.2
    df = pd.DataFrame({"timestamp": dates, "display_value": vals})

    evaluator = ChronologicalHoldoutEvaluator(cutoff_date="2022-12-01")
    res = evaluator.evaluate_all_models(df, var_id="test_t2m")

    assert res["train_observations"] > 0
    assert res["test_observations"] > 0
    assert "models" in res
    assert "ridge_lag" in res["models"]
    assert res["models"]["ridge_lag"]["metrics"]["mae"] >= 0.0
    assert res["models"]["ridge_lag"]["metrics"]["rmse"] >= 0.0


def test_inference_service_uncertainty_bounds():
    """Verify inference service outputs forecast points with valid lower and upper bounds."""
    processed_dir = Path("data/processed")
    df = pd.read_parquet(processed_dir / "t2m.parquet")

    service = ForecastInferenceService()
    fc = service.generate_forecast(df, var_id="t2m", horizon_months=12, model_id="ridge_lag")

    assert fc.variable_id == "t2m"
    assert fc.horizon_months == 12
    assert len(fc.predictions) == 12
    assert fc.metrics.rmse > 0

    for pt in fc.predictions:
        assert pt.lower_bound <= pt.predicted_value <= pt.upper_bound


@pytest.mark.asyncio
async def test_api_forecast_endpoint():
    """Verify POST /api/v1/forecast endpoint executes and returns ForecastResponse schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "variable_id": "precipitation",
            "horizon_months": 12,
            "model_id": "ridge_lag",
            "confidence_level": 0.95
        }
        response = await client.post("/api/v1/forecast", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["variable_id"] == "precipitation"
        assert data["model_id"] == "ridge_lag"
        assert len(data["predictions"]) == 12
        assert data["metrics"]["mae"] > 0
        assert data["metrics"]["rmse"] > 0
        assert data["forecast_origin"] == "2025-09-01"

        # Verify physical lower bound is non-negative for rain
        for pt in data["predictions"]:
            assert pt["lower_bound"] >= 0.0
