"""Serialize and load fitted EarthScope forecast estimators.

Stage 5 originally persisted only holdout metrics JSON and diagnostic figures.
Production inference then refit Ridge/Random Forest on every API request.
This registry stores one joblib bundle per variable so Stage 6 can load
full-history production estimators plus the frozen holdout metrics.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import pandas as pd

from backend.app.core.catalog import MODEL_DISPLAY_NAMES, SUPPORTED_MODEL_IDS
from backend.app.core.config import settings
from backend.ml.features.pipeline import TimeSeriesFeatureExtractor
from backend.ml.training.models import (
    LinearDriftModel,
    PersistenceModel,
    RandomForestForecastModel,
    RidgeForecastModel,
    SeasonalNaiveModel,
)

ARTIFACT_SCHEMA_VERSION = 1


def recommend_model_id(model_metrics: Dict[str, Any]) -> str:
    """Select the model with the lowest holdout RMSE (ties keep seasonal naive)."""
    best_id = "seasonal_naive"
    best_rmse = float("inf")
    for model_id, info in model_metrics.items():
        rmse = float(info["metrics"]["rmse"])
        if rmse < best_rmse:
            best_rmse = rmse
            best_id = model_id
    return best_id


def fit_production_bundle(
    df: pd.DataFrame,
    var_id: str,
    eval_res: Dict[str, Any],
    value_col: str = "display_value",
    time_col: str = "timestamp",
) -> Dict[str, Any]:
    """Fit all ladder models on the full available history for serving."""
    extractor = TimeSeriesFeatureExtractor()
    temp = df.copy()
    temp[time_col] = pd.to_datetime(temp[time_col])
    temp = temp.sort_values(time_col).reset_index(drop=True)
    y = temp[value_col]

    persistence = PersistenceModel()
    persistence.fit(y)
    seasonal = SeasonalNaiveModel(period=12)
    seasonal.fit(y)
    drift = LinearDriftModel()
    drift.fit(y)

    X_full, y_full, feature_names = extractor.create_features(
        temp, target_col=value_col, time_col=time_col
    )
    ridge = RidgeForecastModel(alpha=1.0)
    ridge.fit(X_full, y_full)
    forest = RandomForestForecastModel(n_estimators=100, max_depth=6)
    forest.fit(X_full, y_full)

    recommended = recommend_model_id(eval_res["models"])
    first_ts = temp[time_col].iloc[0].strftime("%Y-%m-%d")
    last_ts = temp[time_col].iloc[-1].strftime("%Y-%m-%d")

    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "variable_id": var_id,
        "region": str(temp.iloc[0].get("region", "Pakistan")),
        "fit_mode": "full_history_production",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "train_start": first_ts,
        "train_end": last_ts,
        "n_observations": int(len(temp)),
        "holdout_cutoff": "2022-12-01",
        "holdout_train_period": eval_res.get("train_period"),
        "holdout_test_period": eval_res.get("test_period"),
        "train_observations": eval_res.get("train_observations"),
        "test_observations": eval_res.get("test_observations"),
        "holdout_metrics": eval_res["models"],
        "recommended_model_id": recommended,
        "feature_names": feature_names,
        "feature_extractor": {
            "lags": extractor.lags,
            "rolling_windows": extractor.rolling_windows,
            "use_fourier": extractor.use_fourier,
            "use_time_trend": extractor.use_time_trend,
        },
        "estimators": {
            "persistence": persistence,
            "seasonal_naive": seasonal,
            "linear_drift": drift,
            "ridge_lag": ridge,
            "random_forest": forest,
        },
    }


class ModelRegistry:
    """Filesystem registry of per-variable joblib bundles and a JSON manifest."""

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = Path(models_dir) if models_dir else settings.MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.models_dir / "manifest.json"

    def artifact_path(self, variable_id: str) -> Path:
        return self.models_dir / f"{variable_id}.joblib"

    def exists(self, variable_id: str) -> bool:
        return self.artifact_path(variable_id).exists()

    def save_variable_bundle(self, variable_id: str, bundle: Dict[str, Any]) -> Path:
        path = self.artifact_path(variable_id)
        joblib.dump(bundle, path, compress=3)
        self._update_manifest(variable_id, bundle, path)
        return path

    def load_variable_bundle(self, variable_id: str) -> Dict[str, Any]:
        path = self.artifact_path(variable_id)
        if not path.exists():
            raise FileNotFoundError(
                f"No saved forecast artifact for '{variable_id}'. "
                "Run `python scripts/train_forecast_models.py` to persist models."
            )
        bundle = joblib.load(path)
        if bundle.get("schema_version") != ARTIFACT_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported artifact schema {bundle.get('schema_version')} for '{variable_id}'."
            )
        return bundle

    def load_manifest(self) -> Dict[str, Any]:
        if not self.manifest_path.exists():
            return {"schema_version": ARTIFACT_SCHEMA_VERSION, "variables": {}}
        with open(self.manifest_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def list_saved_variables(self) -> list[str]:
        return sorted(p.stem for p in self.models_dir.glob("*.joblib"))

    def _update_manifest(self, variable_id: str, bundle: Dict[str, Any], path: Path) -> None:
        manifest = self.load_manifest()
        manifest["schema_version"] = ARTIFACT_SCHEMA_VERSION
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        variables = manifest.setdefault("variables", {})
        variables[variable_id] = {
            "variable_id": variable_id,
            "artifact": path.name,
            "region": bundle.get("region"),
            "fit_mode": bundle.get("fit_mode"),
            "trained_at": bundle.get("trained_at"),
            "train_start": bundle.get("train_start"),
            "train_end": bundle.get("train_end"),
            "n_observations": bundle.get("n_observations"),
            "recommended_model_id": bundle.get("recommended_model_id"),
            "model_ids": list(SUPPORTED_MODEL_IDS),
            "model_names": MODEL_DISPLAY_NAMES,
            "holdout_train_period": bundle.get("holdout_train_period"),
            "holdout_test_period": bundle.get("holdout_test_period"),
            "train_observations": bundle.get("train_observations"),
            "test_observations": bundle.get("test_observations"),
            "holdout_metrics": {
                model_id: info["metrics"]
                for model_id, info in bundle.get("holdout_metrics", {}).items()
            },
        }
        with open(self.manifest_path, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2)
