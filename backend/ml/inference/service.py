"""Inference and forward projection service for EarthScope forecasting."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from scipy import stats

from backend.ml.features.pipeline import TimeSeriesFeatureExtractor
from backend.ml.training.models import (
    PersistenceModel,
    SeasonalNaiveModel,
    LinearDriftModel,
    RidgeForecastModel,
    RandomForestForecastModel,
)
from backend.ml.evaluation.validator import ChronologicalHoldoutEvaluator
from backend.app.schemas.forecast import (
    ForecastResponse,
    ForecastPoint,
    ModelEvaluationMetrics,
)


LIMITATIONS_BY_MODEL: Dict[str, List[str]] = {
    "persistence": [
        "Assumes state variable remains static into the future",
        "Ignores annual seasonal cycle and long-term climate trends"
    ],
    "seasonal_naive": [
        "Assumes future years replicate historical 12-month calendar cycle exactly",
        "Does not account for multi-year warming or drying trends"
    ],
    "linear_drift": [
        "Assumes historical linear trajectory continues indefinitely without saturation or feedback",
        "Ignores seasonal variations"
    ],
    "ridge_lag": [
        "Linear assumption between engineered lag/harmonic features and target",
        "Autoregressive iterative projections experience error compounding over long horizons"
    ],
    "random_forest": [
        "Tree-based models cannot extrapolate values beyond the minimum and maximum seen in training",
        "Prediction intervals widen with horizon based on historical residual variance"
    ],
}


class ForecastInferenceService:
    """End-to-end forward projection and evaluation service."""

    def __init__(self, processed_dir: Path = Path("data/processed")):
        self.processed_dir = processed_dir
        self.feature_extractor = TimeSeriesFeatureExtractor()
        self.evaluator = ChronologicalHoldoutEvaluator(cutoff_date="2022-12-01", feature_extractor=self.feature_extractor)

    def generate_forecast(
        self,
        df: pd.DataFrame,
        var_id: str,
        horizon_months: int = 12,
        model_id: str = "ridge_lag",
        confidence_level: float = 0.95,
    ) -> ForecastResponse:
        """Fit model, compute out-of-sample holdout metrics, and project future months with uncertainty."""
        temp = df.copy()
        temp["timestamp"] = pd.to_datetime(temp["timestamp"])
        temp = temp.sort_values("timestamp").reset_index(drop=True)

        value_col = "display_value"
        last_date = temp["timestamp"].iloc[-1]
        forecast_origin = last_date.strftime("%Y-%m-%d")

        # 1. Run out-of-sample holdout evaluation to obtain empirical metrics
        eval_res = self.evaluator.evaluate_all_models(temp, var_id=var_id, value_col=value_col)

        if model_id not in eval_res["models"]:
            valid_models = list(eval_res["models"].keys())
            raise ValueError(f"Unknown model_id '{model_id}'. Supported: {valid_models}")

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

        # 2. Future dates generation (monthly frequency)
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=horizon_months,
            freq="MS"
        )

        # 3. Fit on full available data and predict forward
        point_preds = []

        if model_id == "persistence":
            pers = PersistenceModel()
            pers.fit(temp[value_col])
            point_preds = pers.predict(horizon_months)

        elif model_id == "seasonal_naive":
            s_naive = SeasonalNaiveModel(period=12)
            s_naive.fit(temp[value_col])
            point_preds = s_naive.predict(horizon_months)

        elif model_id == "linear_drift":
            drift = LinearDriftModel()
            drift.fit(temp[value_col])
            point_preds = drift.predict(horizon_months)

        elif model_id in ("ridge_lag", "random_forest"):
            # Fit ML model on full history
            X_full, y_full, feat_names = self.feature_extractor.create_features(
                temp, target_col=value_col, time_col="timestamp"
            )

            if model_id == "ridge_lag":
                ml_model = RidgeForecastModel(alpha=1.0)
            else:
                ml_model = RandomForestForecastModel(n_estimators=100, max_depth=6)

            ml_model.fit(X_full, y_full)

            # Iterative multi-step projection
            history_series = temp[value_col].tolist()
            history_dates = temp["timestamp"].tolist()

            preds = []
            for d in future_dates:
                # Build feature vector at this step
                step_df = pd.DataFrame({"timestamp": history_dates, value_col: history_series})
                step_X, _, _ = self.feature_extractor.create_features(
                    step_df, target_col=value_col, time_col="timestamp"
                )
                step_feat = step_X.iloc[[-1]]
                y_step = float(ml_model.predict(step_feat)[0])

                # Clamp physical variables
                if var_id in ("precipitation", "evapotranspiration", "soil_moisture_0_10cm", "soil_moisture_10_40cm"):
                    y_step = max(0.0, y_step)

                preds.append(y_step)
                history_series.append(y_step)
                history_dates.append(d)

            point_preds = np.array(preds)

        # 4. Uncertainty Intervals Estimation
        # Use empirical holdout RMSE to calibrate prediction interval
        rmse = metrics.rmse
        z_crit = float(stats.norm.ppf(1.0 - (1.0 - confidence_level) / 2.0))

        forecast_points = []
        for h, (dt, pred) in enumerate(zip(future_dates, point_preds)):
            # Uncertainty expands slightly with horizon: sqrt(1 + (h-1)/12)
            sigma_h = rmse * np.sqrt(1.0 + h / 12.0)
            margin = z_crit * sigma_h
            lower = pred - margin
            upper = pred + margin

            # Non-negative clamping for physical fluxes and moisture
            if var_id in ("precipitation", "evapotranspiration", "soil_moisture_0_10cm", "soil_moisture_10_40cm"):
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
        )
