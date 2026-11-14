"""Chronological out-of-sample holdout and rolling-origin model evaluator."""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from backend.ml.features.pipeline import TimeSeriesFeatureExtractor
from backend.ml.training.models import (
    PersistenceModel,
    SeasonalNaiveModel,
    LinearDriftModel,
    RidgeForecastModel,
    RandomForestForecastModel,
)


def evaluate_forecast_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate MAE, RMSE, and R2 on out-of-sample test arrays."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    
    # R2 can be negative if model performs worse than mean
    var_y = np.var(y_true)
    if var_y > 1e-9:
        r2 = float(r2_score(y_true, y_pred))
    else:
        r2 = 0.0

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2_score": round(r2, 4),
    }


class ChronologicalHoldoutEvaluator:
    """Evaluates the full model ladder using a strict chronological holdout split."""

    def __init__(
        self,
        cutoff_date: str = "2022-12-01",
        feature_extractor: Optional[TimeSeriesFeatureExtractor] = None,
    ):
        self.cutoff_date = pd.to_datetime(cutoff_date)
        self.feature_extractor = feature_extractor or TimeSeriesFeatureExtractor()

    def evaluate_all_models(
        self,
        df: pd.DataFrame,
        var_id: str,
        value_col: str = "display_value",
        time_col: str = "timestamp",
    ) -> Dict[str, Any]:
        """Train on history prior to cutoff, evaluate strictly on holdout test set."""
        temp = df.copy()
        temp[time_col] = pd.to_datetime(temp[time_col])
        temp = temp.sort_values(time_col).reset_index(drop=True)

        train_mask = temp[time_col] <= self.cutoff_date
        test_mask = temp[time_col] > self.cutoff_date

        train_df = temp[train_mask].reset_index(drop=True)
        test_df = temp[test_mask].reset_index(drop=True)

        if train_df.empty or test_df.empty:
            raise ValueError(f"Cutoff {self.cutoff_date} produces empty train or test partition.")

        horizon = len(test_df)
        y_test = test_df[value_col].values

        # 1. Baseline 1: Persistence
        pers = PersistenceModel()
        pers.fit(train_df[value_col])
        pred_pers = pers.predict(horizon)
        metrics_pers = evaluate_forecast_metrics(y_test, pred_pers)

        # 2. Baseline 2: Seasonal Naive
        s_naive = SeasonalNaiveModel(period=12)
        s_naive.fit(train_df[value_col])
        pred_s_naive = s_naive.predict(horizon)
        metrics_s_naive = evaluate_forecast_metrics(y_test, pred_s_naive)

        # 3. Baseline 3: Linear Drift
        drift = LinearDriftModel()
        drift.fit(train_df[value_col])
        pred_drift = drift.predict(horizon)
        metrics_drift = evaluate_forecast_metrics(y_test, pred_drift)

        # 4. Extract features for ML models (fit on train only)
        # To avoid leakage, feature extraction on full series is sliced strictly at split
        X_all, y_all, feat_names = self.feature_extractor.create_features(
            temp, target_col=value_col, time_col=time_col
        )
        # Re-align indices with original temp dataframe
        max_lag = max(self.feature_extractor.lags)
        train_len = len(train_df) - max_lag

        X_train = X_all.iloc[:train_len].copy()
        y_train = y_all.iloc[:train_len].copy()
        X_test = X_all.iloc[train_len:train_len + horizon].copy()

        # 5. Candidate 1: Lagged Ridge
        ridge = RidgeForecastModel(alpha=1.0)
        ridge.fit(X_train, y_train)
        pred_ridge = ridge.predict(X_test)
        metrics_ridge = evaluate_forecast_metrics(y_test, pred_ridge)

        # 6. Candidate 2: Random Forest
        rf = RandomForestForecastModel(n_estimators=100, max_depth=6)
        rf.fit(X_train, y_train)
        pred_rf = rf.predict(X_test)
        metrics_rf = evaluate_forecast_metrics(y_test, pred_rf)

        # Skill score relative to Seasonal Naive
        base_rmse = metrics_s_naive["rmse"]
        for m in [metrics_pers, metrics_s_naive, metrics_drift, metrics_ridge, metrics_rf]:
            m["skill_score_vs_seasonal_naive"] = round(1.0 - (m["rmse"] / base_rmse), 4) if base_rmse > 0 else 0.0

        model_results = {
            "variable_id": var_id,
            "train_observations": len(train_df),
            "test_observations": len(test_df),
            "train_period": f"{train_df[time_col].min().strftime('%Y-%m-%d')} to {train_df[time_col].max().strftime('%Y-%m-%d')}",
            "test_period": f"{test_df[time_col].min().strftime('%Y-%m-%d')} to {test_df[time_col].max().strftime('%Y-%m-%d')}",
            "models": {
                "persistence": {
                    "model_id": "persistence",
                    "model_name": "Lag-1 Persistence Baseline",
                    "is_baseline": True,
                    "metrics": metrics_pers,
                },
                "seasonal_naive": {
                    "model_id": "seasonal_naive",
                    "model_name": "12-Month Seasonal Naive Baseline",
                    "is_baseline": True,
                    "metrics": metrics_s_naive,
                },
                "linear_drift": {
                    "model_id": "linear_drift",
                    "model_name": "Linear Drift Baseline",
                    "is_baseline": True,
                    "metrics": metrics_drift,
                },
                "ridge_lag": {
                    "model_id": "ridge_lag",
                    "model_name": "Regularized Lagged Ridge Regressor",
                    "is_baseline": False,
                    "metrics": metrics_ridge,
                },
                "random_forest": {
                    "model_id": "random_forest",
                    "model_name": "Random Forest Time-Series Regressor",
                    "is_baseline": False,
                    "metrics": metrics_rf,
                },
            },
            "holdout_predictions": {
                "test_timestamps": test_df[time_col].dt.strftime("%Y-%m-%d").tolist(),
                "actual": [round(float(v), 4) for v in y_test],
                "seasonal_naive": [round(float(v), 4) for v in pred_s_naive],
                "ridge_lag": [round(float(v), 4) for v in pred_ridge],
                "random_forest": [round(float(v), 4) for v in pred_rf],
            }
        }

        return model_results
