"""Feature engineering pipeline for EarthScope time-series forecasting.

Strictly prevents target leakage by extracting features using only historical
observations available at the forecast origin.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd


class TimeSeriesFeatureExtractor:
    """Extracts lag, rolling, seasonal harmonic, and cross-variable features."""

    def __init__(
        self,
        lags: List[int] = [1, 2, 3, 12, 24],
        rolling_windows: List[int] = [3, 12],
        use_fourier: bool = True,
        use_time_trend: bool = True,
    ):
        self.lags = lags
        self.rolling_windows = rolling_windows
        self.use_fourier = use_fourier
        self.use_time_trend = use_time_trend

    def create_features(
        self,
        df: pd.DataFrame,
        target_col: str = "display_value",
        time_col: str = "timestamp",
        covariate_cols: Optional[List[str]] = None,
    ) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """Construct feature matrix X and target vector y.
        
        All rolling and lag statistics are calculated without looking ahead.
        """
        temp = df.copy()
        temp[time_col] = pd.to_datetime(temp[time_col])
        temp = temp.sort_values(time_col).reset_index(drop=True)

        feature_names = []

        # 1. Autoregressive Lags
        for lag in self.lags:
            col_name = f"lag_{lag}"
            temp[col_name] = temp[target_col].shift(lag)
            feature_names.append(col_name)

        # 2. Rolling Statistics (shifted by 1 to prevent contemporary leakage)
        shifted_target = temp[target_col].shift(1)
        for w in self.rolling_windows:
            mean_col = f"rolling_mean_{w}"
            std_col = f"rolling_std_{w}"
            temp[mean_col] = shifted_target.rolling(window=w, min_periods=1).mean()
            temp[std_col] = shifted_target.rolling(window=w, min_periods=1).std().fillna(0.0)
            feature_names.extend([mean_col, std_col])

        # 3. Seasonal Harmonic Fourier terms
        months = temp[time_col].dt.month.values
        if self.use_fourier:
            temp["sin_month_1"] = np.sin(2.0 * np.pi * months / 12.0)
            temp["cos_month_1"] = np.cos(2.0 * np.pi * months / 12.0)
            temp["sin_month_2"] = np.sin(4.0 * np.pi * months / 12.0)
            temp["cos_month_2"] = np.cos(4.0 * np.pi * months / 12.0)
            feature_names.extend(["sin_month_1", "cos_month_1", "sin_month_2", "cos_month_2"])

        # 4. Normalized Linear Time Trend
        if self.use_time_trend:
            t0 = temp[time_col].iloc[0]
            temp["time_trend"] = (temp[time_col] - t0).dt.days / 365.25
            feature_names.append("time_trend")

        # 5. Cross-Variable Lagged Covariates
        if covariate_cols:
            for c in covariate_cols:
                if c in temp.columns:
                    col_name = f"{c}_lag1"
                    temp[col_name] = temp[c].shift(1)
                    feature_names.append(col_name)

        # Drop initial rows containing NaN from maximum lag
        max_lag = max(self.lags) if self.lags else 0
        valid_mask = temp.index >= max_lag

        X = temp.loc[valid_mask, feature_names].copy().reset_index(drop=True)
        y = temp.loc[valid_mask, target_col].copy().reset_index(drop=True)

        return X, y, feature_names
