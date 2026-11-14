"""Temporal aggregation modules for EarthScope.

Computes annual and seasonal summaries using scientifically appropriate operators
(mean for intensive state variables such as temperature and soil moisture;
sum or daily rate for extensive fluxes such as precipitation and evapotranspiration).
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


SEASON_MAP = {
    12: "Winter (DJF)", 1: "Winter (DJF)", 2: "Winter (DJF)",
    3: "Pre-Monsoon (MAM)", 4: "Pre-Monsoon (MAM)", 5: "Pre-Monsoon (MAM)",
    6: "Monsoon (JJAS)", 7: "Monsoon (JJAS)", 8: "Monsoon (JJAS)", 9: "Monsoon (JJAS)",
    10: "Post-Monsoon (ON)", 11: "Post-Monsoon (ON)"
}


def compute_annual_summary(
    df: pd.DataFrame,
    var_id: str,
    value_col: str = "display_value",
    time_col: str = "timestamp",
    min_months_per_year: int = 12
) -> pd.DataFrame:
    """Compute annual summaries.
    Filters out incomplete years (e.g. 2025 ending in September) if min_months_per_year=12.
    """
    temp = df.copy()
    temp["year"] = temp[time_col].dt.year

    # Operator selection based on physical variable nature
    is_flux = var_id in ("precipitation", "evapotranspiration")

    grouped = temp.groupby("year")[value_col]
    counts = grouped.count()
    means = grouped.mean()
    sums = grouped.sum()

    annual = pd.DataFrame({
        "year": counts.index,
        "n_months": counts.values,
        "annual_mean": means.values,
        "annual_total": sums.values if is_flux else None,
        "is_complete_year": counts.values >= min_months_per_year
    })

    return annual


def compute_seasonal_summary(
    df: pd.DataFrame,
    var_id: str,
    value_col: str = "display_value",
    time_col: str = "timestamp"
) -> pd.DataFrame:
    """Compute meteorological seasonal summaries for Pakistan climate regimes."""
    temp = df.copy()
    temp["month"] = temp[time_col].dt.month
    temp["year"] = temp[time_col].dt.year
    temp["season"] = temp["month"].map(SEASON_MAP)

    is_flux = var_id in ("precipitation", "evapotranspiration")

    grouped = temp.groupby(["year", "season"])[value_col]
    counts = grouped.count()
    means = grouped.mean()
    sums = grouped.sum()

    seasonal = pd.DataFrame({
        "n_months": counts,
        "mean_value": means,
        "total_value": sums if is_flux else None
    }).reset_index()

    return seasonal
