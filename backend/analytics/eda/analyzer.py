"""Exploratory Data Analysis (EDA) engine for EarthScope.

Computes comprehensive statistical distributions, seasonal climatologies,
inter-variable correlations, and extreme anomalies across the coupled Earth-system suite.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def compute_variable_descriptive_stats(df: pd.DataFrame, value_col: str = "display_value") -> Dict[str, Any]:
    """Compute parametric and non-parametric descriptive statistics for a time series."""
    vals = df[value_col].dropna().values
    if len(vals) == 0:
        raise ValueError("Cannot compute descriptive statistics on empty series.")

    q25, q50, q75 = np.percentile(vals, [25, 50, 75])
    iqr = q75 - q25

    return {
        "count": int(len(vals)),
        "mean": float(np.mean(vals)),
        "std": float(np.std(vals, ddof=1)),
        "variance": float(np.var(vals, ddof=1)),
        "min": float(np.min(vals)),
        "max": float(np.max(vals)),
        "range": float(np.max(vals) - np.min(vals)),
        "median": float(q50),
        "q25": float(q25),
        "q75": float(q75),
        "iqr": float(iqr),
        "skewness": float(stats.skew(vals)),
        "kurtosis": float(stats.kurtosis(vals)),
    }


def compute_correlation_matrices(wide_df: pd.DataFrame, value_suffix: str = "_value") -> Dict[str, Any]:
    """Compute Pearson and Spearman cross-variable correlation matrices on clean values and anomalies."""
    val_cols = [c for c in wide_df.columns if c.endswith(value_suffix)]
    clean_names = [c.replace(value_suffix, "") for c in val_cols]

    sub_df = wide_df[val_cols].copy()
    sub_df.columns = clean_names

    pearson_corr = sub_df.corr(method="pearson").round(4).to_dict()
    spearman_corr = sub_df.corr(method="spearman").round(4).to_dict()

    # Also compute on anomalies if available
    anomaly_cols = [c for c in wide_df.columns if c.endswith("_anomaly")]
    anomaly_names = [c.replace("_anomaly", "") for c in anomaly_cols]
    anomaly_sub = wide_df[anomaly_cols].copy()
    anomaly_sub.columns = anomaly_names
    anomaly_pearson = anomaly_sub.corr(method="pearson").round(4).to_dict()
    anomaly_spearman = anomaly_sub.corr(method="spearman").round(4).to_dict()

    return {
        "raw_value_pearson": pearson_corr,
        "raw_value_spearman": spearman_corr,
        "anomaly_pearson": anomaly_pearson,
        "anomaly_spearman": anomaly_spearman,
        "variables": clean_names,
    }


def detect_top_extreme_anomalies(
    df: pd.DataFrame,
    var_id: str,
    top_n: int = 5,
    value_col: str = "display_value",
    anomaly_col: str = "anomaly",
    std_anomaly_col: str = "standardized_anomaly"
) -> Dict[str, Any]:
    """Identify top positive and negative monthly anomalies representing extreme environmental events."""
    sorted_pos = df.sort_values(by=anomaly_col, ascending=False).head(top_n)
    sorted_neg = df.sort_values(by=anomaly_col, ascending=True).head(top_n)

    def format_records(subset: pd.DataFrame) -> List[Dict[str, Any]]:
        return [
            {
                "timestamp": row["timestamp"].strftime("%Y-%m-%d"),
                "value": round(float(row[value_col]), 4),
                "anomaly": round(float(row[anomaly_col]), 4),
                "z_score": round(float(row[std_anomaly_col]), 2) if std_anomaly_col in row else None,
            }
            for _, row in subset.iterrows()
        ]

    return {
        "variable_id": var_id,
        "top_positive_anomalies": format_records(sorted_pos),
        "top_negative_anomalies": format_records(sorted_neg),
    }


def compute_seasonal_climatology_profile(
    df: pd.DataFrame,
    value_col: str = "display_value",
    time_col: str = "timestamp"
) -> pd.DataFrame:
    """Compute 12-month annual climatological cycle with mean, std, min, and max."""
    temp = df.copy()
    temp["month"] = temp[time_col].dt.month

    monthly = temp.groupby("month")[value_col].agg(
        mean="mean",
        std="std",
        median="median",
        min="min",
        max="max",
        count="count"
    ).reset_index()

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly["month_name"] = monthly["month"].map(lambda m: month_names[m - 1])
    return monthly
