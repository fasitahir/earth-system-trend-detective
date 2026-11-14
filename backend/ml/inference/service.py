"""Inference and forward projection service for EarthScope forecasting."""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

from backend.app.core.catalog import NON_NEGATIVE_VARIABLES, SUPPORTED_MODEL_IDS
from backend.app.schemas.forecast import ForecastPoint, ForecastResponse, ModelEvaluationMetrics
from backend.ml.evaluation.validator import ChronologicalHoldoutEvaluator
from backend.ml.features.pipeline import TimeSeriesFeatureExtractor
from backend.ml.training.models import (
    LinearDriftModel,
    PersistenceModel,
    RandomForestForecastModel,
    RidgeForecastModel,
    SeasonalNaiveModel,
)
from backend.ml.training.persistence import ModelRegistry

LIMITATIONS_BY_MODEL: Dict[str, List[str]] = {
    "persistence": [
        "Assumes state variable remains static into the future",
        "Ignores annual seasonal cycle and long-term climate trends",
    ],
    "seasonal_naive": [
        "Assumes future years replicate historical 12-month calendar cycle exactly",
        "Does not account for multi-year warming or drying trends",
    ],
    "linear_drift": [
        "Assumes historical linear trajectory continues indefinitely without saturation or feedback",
        "Ignores seasonal variations",
    ],
    "ridge_lag": [
        "Linear assumption between engineered lag/harmonic features and target",
        "Autoregressive iterative projections experience error compounding over long horizons",
    ],
    "random_forest": [
        "Tree-based models cannot extrapolate values beyond the minimum and maximum seen in training",
        "Prediction intervals widen with horizon based on historical residual variance",
    ],
}


class ForecastInferenceService:
    """End-to-end forward projection service that prefers saved production artifacts."""

    def __init__(
        self,
        processed_dir=None,
        registry: Optional[ModelRegistry] = None,
        prefer_saved_models: bool = True,
    ):
        self.feature_extractor = TimeSeriesFeatureExtractor()
        self.evaluator = ChronologicalHoldoutEvaluator(
            cutoff_date="2022-12-01", feature_extractor=self.feature_extractor
        )
        self.registry = registry or ModelRegistry()
        self.prefer_saved_models = prefer_saved_models

    def generate_forecast(
        self,
        df: pd.DataFrame,
        var_id: str,
        horizon_months: int = 12,
        model_id: str = "ridge_lag",
        confidence_level: float = 0.95,
    ) -> ForecastResponse:
        """Project future months using a saved production model when available."""
        if model_id not in SUPPORTED_MODEL_IDS:
            raise ValueError(f"Unknown model_id '{model_id}'. Supported: {SUPPORTED_MODEL_IDS}")

        temp = df.copy()
        temp["timestamp"] = pd.to_datetime(temp["timestamp"])
        temp = temp.sort_values("timestamp").reset_index(drop=True)

        value_col = "display_value"
        last_date = temp["timestamp"].iloc[-1]
        forecast_origin = last_date.strftime("%Y-%m-%d")

        bundle = None
        if self.prefer_saved_models and self.registry.exists(var_id):
            bundle = self.registry.load_variable_bundle(var_id)

        if bundle is not None:
            selected_eval = bundle["holdout_metrics"][model_id]
            test_obs = bundle.get("test_observations") or self._test_obs_from_period(
                bundle.get("holdout_test_period")
            )
            metrics = ModelEvaluationMetrics(
                model_id=selected_eval["model_id"],
                model_name=selected_eval["model_name"],
                mae=selected_eval["metrics"]["mae"],
                rmse=selected_eval["metrics"]["rmse"],
                r2_score=selected_eval["metrics"]["r2_score"],
                test_observations=int(test_obs),
                is_baseline=selected_eval["is_baseline"],
            )
            extractor_cfg = bundle.get("feature_extractor") or {}
            feature_extractor = TimeSeriesFeatureExtractor(
                lags=extractor_cfg.get("lags", [1, 2, 3, 12, 24]),
                rolling_windows=extractor_cfg.get("rolling_windows", [3, 12]),
                use_fourier=extractor_cfg.get("use_fourier", True),
                use_time_trend=extractor_cfg.get("use_time_trend", True),
            )
            estimator = bundle["estimators"][model_id]
            artifact_loaded = True
            trained_on = bundle.get("fit_mode")
        else:
            eval_res = self.evaluator.evaluate_all_models(temp, var_id=var_id, value_col=value_col)
            selected_eval = eval_res["models"][model_id]
            metrics = ModelEvaluationMetrics(
                model_id=selected_eval["model_id"],
                model_name=selected_eval["model_name"],
                mae=selected_eval["metrics"]["mae"],
                rmse=selected_eval["metrics"]["rmse"],
                r2_score=selected_eval["metrics"]["r2_score"],
                test_observations=eval_res["test_observations"],
                is_baseline=selected_eval["is_baseline"],
            )
            feature_extractor = self.feature_extractor
            estimator = self._fit_ephemeral(temp, model_id, value_col, feature_extractor)
            artifact_loaded = False
            trained_on = "ephemeral_full_history"

        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=horizon_months,
            freq="MS",
        )
        point_preds = self._project(
            temp=temp,
            model_id=model_id,
            estimator=estimator,
            feature_extractor=feature_extractor,
            future_dates=future_dates,
            value_col=value_col,
            var_id=var_id,
        )

        rmse = metrics.rmse
        z_crit = float(stats.norm.ppf(1.0 - (1.0 - confidence_level) / 2.0))
        forecast_points = []
        for h, (dt, pred) in enumerate(zip(future_dates, point_preds)):
            sigma_h = rmse * np.sqrt(1.0 + h / 12.0)
            margin = z_crit * sigma_h
            lower = pred - margin
            upper = pred + margin
            if var_id in NON_NEGATIVE_VARIABLES:
                lower = max(0.0, lower)
            forecast_points.append(
                ForecastPoint(
                    timestamp=dt.strftime("%Y-%m-%d"),
                    predicted_value=round(float(pred), 4),
                    lower_bound=round(float(lower), 4),
                    upper_bound=round(float(upper), 4),
                )
            )

        limitations = list(LIMITATIONS_BY_MODEL.get(model_id, []))
        if artifact_loaded:
            limitations.append(
                f"Point forecasts use the persisted {trained_on} artifact; "
                "interval width is calibrated from chronological holdout RMSE, not a new fit."
            )
        else:
            limitations.append(
                "No saved artifact was found; this response fitted an ephemeral model. "
                "Run `python scripts/train_forecast_models.py` to persist estimators."
            )

        first_row = temp.iloc[0]
        return ForecastResponse(
            variable_id=var_id,
            unit=str(first_row.get("display_unit", "units")),
            region=str(first_row.get("region", "Pakistan")),
            forecast_origin=forecast_origin,
            horizon_months=horizon_months,
            model_id=model_id,
            model_name=selected_eval["model_name"],
            metrics=metrics,
            predictions=forecast_points,
            limitations=limitations,
            artifact_loaded=artifact_loaded,
            trained_on=trained_on,
        )

    @staticmethod
    def _test_obs_from_period(period: Optional[str]) -> int:
        if not period or " to " not in period:
            return 0
        start_s, end_s = period.split(" to ")
        start = pd.to_datetime(start_s)
        end = pd.to_datetime(end_s)
        return int(len(pd.date_range(start, end, freq="MS")))

    def _fit_ephemeral(self, temp, model_id, value_col, feature_extractor):
        if model_id == "persistence":
            model = PersistenceModel()
            model.fit(temp[value_col])
            return model
        if model_id == "seasonal_naive":
            model = SeasonalNaiveModel(period=12)
            model.fit(temp[value_col])
            return model
        if model_id == "linear_drift":
            model = LinearDriftModel()
            model.fit(temp[value_col])
            return model
        X_full, y_full, _ = feature_extractor.create_features(
            temp, target_col=value_col, time_col="timestamp"
        )
        if model_id == "ridge_lag":
            model = RidgeForecastModel(alpha=1.0)
        else:
            model = RandomForestForecastModel(n_estimators=100, max_depth=6)
        model.fit(X_full, y_full)
        return model

    def _project(self, temp, model_id, estimator, feature_extractor, future_dates, value_col, var_id):
        horizon_months = len(future_dates)
        if model_id in ("persistence", "seasonal_naive", "linear_drift"):
            return estimator.predict(horizon_months)

        history_series = temp[value_col].tolist()
        history_dates = temp["timestamp"].tolist()
        preds = []
        for d in future_dates:
            step_df = pd.DataFrame({"timestamp": history_dates, value_col: history_series})
            step_X, _, _ = feature_extractor.create_features(
                step_df, target_col=value_col, time_col="timestamp"
            )
            y_step = float(estimator.predict(step_X.iloc[[-1]])[0])
            if var_id in NON_NEGATIVE_VARIABLES:
                y_step = max(0.0, y_step)
            preds.append(y_step)
            history_series.append(y_step)
            history_dates.append(d)
        return np.array(preds)
