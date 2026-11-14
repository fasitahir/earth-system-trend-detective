"""Model ladder implementations for EarthScope forecasting.

Includes:
- Baseline 1: Lag-1 Persistence
- Baseline 2: 12-Month Seasonal Naive
- Baseline 3: Linear Drift Trend
- Candidate 1: Lagged Ridge Regression with L2 regularization & Feature Scaling
- Candidate 2: Random Forest Time-Series Regressor
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


class PersistenceModel:
    """Benchmark Baseline: Forecasts the most recent historical observation forward."""
    
    def __init__(self):
        self.model_id = "persistence"
        self.model_name = "Lag-1 Persistence Baseline"
        self.is_baseline = True
        self.last_value = None

    def fit(self, y: pd.Series):
        self.last_value = float(y.iloc[-1])

    def predict(self, horizon: int) -> np.ndarray:
        if self.last_value is None:
            raise ValueError("Model must be fitted before predict.")
        return np.full(horizon, self.last_value)


class SeasonalNaiveModel:
    """Benchmark Baseline: Forecasts the value observed in the identical calendar month 1 year prior."""

    def __init__(self, period: int = 12):
        self.model_id = "seasonal_naive"
        self.model_name = "12-Month Seasonal Naive Baseline"
        self.is_baseline = True
        self.period = period
        self.last_year_values = None

    def fit(self, y: pd.Series):
        if len(y) < self.period:
            raise ValueError(f"Seasonal naive requires at least {self.period} observations.")
        self.last_year_values = y.iloc[-self.period:].values

    def predict(self, horizon: int) -> np.ndarray:
        if self.last_year_values is None:
            raise ValueError("Model must be fitted before predict.")
        preds = []
        for h in range(horizon):
            idx = h % self.period
            preds.append(self.last_year_values[idx])
        return np.array(preds)


class LinearDriftModel:
    """Benchmark Baseline: Fits linear trajectory over training history and extrapolates."""

    def __init__(self):
        self.model_id = "linear_drift"
        self.model_name = "Linear Drift Baseline"
        self.is_baseline = True
        self.slope = None
        self.intercept = None
        self.n_train = None

    def fit(self, y: pd.Series):
        n = len(y)
        self.n_train = n
        x = np.arange(n)
        poly = np.polyfit(x, y.values, deg=1)
        self.slope = float(poly[0])
        self.intercept = float(poly[1])

    def predict(self, horizon: int) -> np.ndarray:
        future_x = np.arange(self.n_train, self.n_train + horizon)
        return self.slope * future_x + self.intercept


class RidgeForecastModel:
    """Candidate Model: Regularized L2 Auto-Regressive Ridge Regressor with Feature Scaling."""

    def __init__(self, alpha: float = 1.0):
        self.model_id = "ridge_lag"
        self.model_name = "Regularized Lagged Ridge Regressor"
        self.is_baseline = False
        self.alpha = alpha
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("ridge", Ridge(alpha=alpha, random_state=42))
        ])

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.pipeline.fit(X, y)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict(X)


class RandomForestForecastModel:
    """Candidate Model: Non-linear Random Forest Ensemble Regressor."""

    def __init__(self, n_estimators: int = 100, max_depth: int = 6):
        self.model_id = "random_forest"
        self.model_name = "Random Forest Time-Series Regressor"
        self.is_baseline = False
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X)
