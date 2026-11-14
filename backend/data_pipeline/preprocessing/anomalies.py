"""Baseline climatology and anomaly decomposition for EarthScope."""

from typing import Dict, Tuple, Optional
import pandas as pd
import numpy as np


class ClimatologyEngine:
    """Computes monthly climatologies and anomalies against an explicit reference baseline."""

    def __init__(
        self,
        baseline_start: str = "2001-01-01",
        baseline_end: str = "2020-12-31"
    ):
        self.baseline_start = pd.to_datetime(baseline_start)
        self.baseline_end = pd.to_datetime(baseline_end)

    def fit_climatology(
        self,
        df: pd.DataFrame,
        value_col: str,
        time_col: str = "timestamp"
    ) -> pd.DataFrame:
        """Compute monthly mean and standard deviation over the reference baseline window."""
        baseline_mask = (df[time_col] >= self.baseline_start) & (df[time_col] <= self.baseline_end)
        baseline_df = df[baseline_mask]

        if baseline_df.empty:
            raise ValueError(
                f"No observations found within baseline range {self.baseline_start.date()} to {self.baseline_end.date()}"
            )

        monthly = baseline_df.groupby(baseline_df[time_col].dt.month)[value_col].agg(["mean", "std", "count"])
        monthly.columns = ["climatology_mean", "climatology_std", "climatology_n"]
        monthly.index.name = "month"
        return monthly

    def calculate_anomalies(
        self,
        df: pd.DataFrame,
        value_col: str,
        climatology: pd.DataFrame,
        time_col: str = "timestamp"
    ) -> pd.DataFrame:
        """Decompose time series into climatological expectation, anomaly, and standardized anomaly."""
        res = df.copy()
        res["month"] = res[time_col].dt.month

        # Merge monthly climatology
        res = res.merge(climatology[["climatology_mean", "climatology_std"]], on="month", how="left")

        res["anomaly"] = res[value_col] - res["climatology_mean"]
        # Standardized anomaly (z-score relative to monthly variance)
        res["standardized_anomaly"] = np.where(
            res["climatology_std"] > 1e-9,
            res["anomaly"] / res["climatology_std"],
            0.0
        )
        return res.drop(columns=["month"])
