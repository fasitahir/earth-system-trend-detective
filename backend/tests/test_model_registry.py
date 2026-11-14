"""Tests for persisted forecast artifacts."""

from pathlib import Path

import pandas as pd

from backend.ml.evaluation.validator import ChronologicalHoldoutEvaluator
from backend.ml.inference.service import ForecastInferenceService
from backend.ml.training.persistence import ModelRegistry, fit_production_bundle, recommend_model_id


def test_recommend_model_id_picks_lowest_rmse():
    metrics = {
        "seasonal_naive": {"metrics": {"rmse": 2.0}},
        "ridge_lag": {"metrics": {"rmse": 1.5}},
        "random_forest": {"metrics": {"rmse": 1.8}},
    }
    assert recommend_model_id(metrics) == "ridge_lag"


def test_save_and_load_bundle_roundtrip(tmp_path: Path):
    df = pd.read_parquet("data/processed/t2m.parquet")
    evaluator = ChronologicalHoldoutEvaluator(cutoff_date="2022-12-01")
    eval_res = evaluator.evaluate_all_models(df, var_id="t2m")
    bundle = fit_production_bundle(df, "t2m", eval_res)

    registry = ModelRegistry(models_dir=tmp_path)
    path = registry.save_variable_bundle("t2m", bundle)
    assert path.exists()
    assert (tmp_path / "manifest.json").exists()

    loaded = registry.load_variable_bundle("t2m")
    assert loaded["variable_id"] == "t2m"
    assert loaded["fit_mode"] == "full_history_production"
    assert set(loaded["estimators"].keys()) == {
        "persistence",
        "seasonal_naive",
        "linear_drift",
        "ridge_lag",
        "random_forest",
    }

    service = ForecastInferenceService(registry=registry, prefer_saved_models=True)
    fc = service.generate_forecast(df, var_id="t2m", horizon_months=6, model_id="ridge_lag")
    assert fc.artifact_loaded is True
    assert fc.trained_on == "full_history_production"
    assert len(fc.predictions) == 6
    for pt in fc.predictions:
        assert pt.lower_bound <= pt.predicted_value <= pt.upper_bound
