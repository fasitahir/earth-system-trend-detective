"""Trend detection engine translating statistical tests into standard TrendResponse objects."""

from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd

from backend.analytics.trend_detection.methods import (
    linear_regression_trend,
    mann_kendall_test,
    modified_mann_kendall_yue_pilon,
    seasonal_mann_kendall_test,
    diagnose_autocorrelation,
)
from backend.app.schemas.trend import TrendResponse, ConfidenceInterval


METHOD_ASSUMPTIONS: Dict[str, List[str]] = {
    "linear_regression": [
        "Linear relationship between elapsed time and target variable",
        "Normally distributed, homoscedastic residual errors",
        "Independent observations without strong serial autocorrelation"
    ],
    "mann_kendall": [
        "Monotonic trend direction (monotonic increasing or decreasing, not necessarily linear)",
        "Independent and identically distributed (i.i.d.) observations",
        "Continuous or ordinal measurements with ties handled"
    ],
    "seasonal_mann_kendall": [
        "Consistent annual seasonality (12-month period)",
        "Homogeneous trend direction across different seasons",
        "Independence between subsequent years within each individual month"
    ],
    "modified_mann_kendall_yue_pilon": [
        "First-order autoregressive AR(1) serial correlation process",
        "Monotonic trend removable via Sen's robust slope estimator before pre-whitening",
        "Residual white noise after trend-free pre-whitening"
    ],
}

METHOD_LIMITATIONS: Dict[str, List[str]] = {
    "linear_regression": [
        "Highly sensitive to single extreme outlier months (e.g. monsoon floods)",
        "Conflates seasonal variance if applied directly to unadjusted monthly series",
        "Underestimates standard errors when positive autocorrelation is present"
    ],
    "mann_kendall": [
        "Presence of strong positive autocorrelation inflates type-I error rate (false positive trend)",
        "Does not capture oscillating non-monotonic regimes or tipping points"
    ],
    "seasonal_mann_kendall": [
        "Requires full annual cycles (multiples of 12 months) for balanced pooling",
        "Less statistical power if trends move in opposite directions in different seasons"
    ],
    "modified_mann_kendall_yue_pilon": [
        "Assumes serial correlation is purely AR(1) rather than higher-order or long-memory processes"
    ],
}


class TrendAnalysisEngine:
    """High-level scientific trend analysis service."""

    def analyze_trend(
        self,
        df: pd.DataFrame,
        var_id: str,
        method: str = "mann_kendall",
        deseasonalize: bool = True,
        alpha: float = 0.05,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> TrendResponse:
        """Run statistical trend test on time-series DataFrame and return standardized TrendResponse."""
        work_df = df.copy()
        work_df["timestamp"] = pd.to_datetime(work_df["timestamp"])

        if start_date:
            work_df = work_df[work_df["timestamp"] >= pd.to_datetime(start_date)]
        if end_date:
            work_df = work_df[work_df["timestamp"] <= pd.to_datetime(end_date)]

        work_df = work_df.sort_values("timestamp").reset_index(drop=True)
        n_obs = len(work_df)
        if n_obs < 12:
            raise ValueError(f"Trend detection requires at least 12 monthly observations (got {n_obs}).")

        # Choose value column
        # If deseasonalize is True and anomaly column exists, use anomaly
        target_col = "anomaly" if deseasonalize and "anomaly" in work_df.columns else "display_value"
        y = work_df[target_col].values.astype(float)

        # Elapsed years from start
        t0 = work_df["timestamp"].iloc[0]
        x_years = (work_df["timestamp"] - t0).dt.days.values / 365.25

        # Check autocorrelation
        ac_diag = diagnose_autocorrelation(y)

        # Execute selected method
        slope_linear = None
        sen_slope = None
        p_val = None
        ci = ConfidenceInterval()
        direction = "no_detected_trend"

        if method == "linear_regression":
            lr = linear_regression_trend(x_years, y, alpha=alpha)
            slope_linear = round(lr["slope_per_year"], 6)
            p_val = round(lr["p_value"], 6)
            direction = lr["trend_direction"]
            ci = ConfidenceInterval(
                lower=round(lr["confidence_interval"]["lower"], 6),
                upper=round(lr["confidence_interval"]["upper"], 6),
            )

        elif method == "seasonal_mann_kendall":
            # For seasonal MK, we pass display_value (not anomaly) because seasonal MK operates per month
            smk_y = work_df["display_value"].values.astype(float)
            smk = seasonal_mann_kendall_test(smk_y, period=12, alpha=alpha)
            sen_slope = round(smk["sen_slope_per_year"], 6)
            p_val = round(smk["p_value"], 6)
            direction = smk["trend_direction"]
            ci = ConfidenceInterval(
                lower=round(smk["confidence_interval"]["lower"], 6),
                upper=round(smk["confidence_interval"]["upper"], 6),
            )

        elif method == "modified_mann_kendall" or (method == "mann_kendall" and ac_diag["is_autocorrelated"]):
            # If autocorrelation is significant, use Yue-Pilon TFPW
            mmk = modified_mann_kendall_yue_pilon(y, alpha=alpha)
            sen_slope = round(mmk["sen_slope_per_year"], 6)
            p_val = round(mmk["p_value"], 6)
            direction = mmk["trend_direction"]
            ci = ConfidenceInterval(
                lower=round(mmk["confidence_interval"]["lower"], 6),
                upper=round(mmk["confidence_interval"]["upper"], 6),
            )
            if method == "mann_kendall":
                method = "modified_mann_kendall_yue_pilon"

        else: # Standard mann_kendall
            mk = mann_kendall_test(y, alpha=alpha)
            sen_slope = round(mk["sen_slope_per_year"], 6)
            p_val = round(mk["p_value"], 6)
            direction = mk["trend_direction"]
            ci = ConfidenceInterval(
                lower=round(mk["confidence_interval"]["lower"], 6),
                upper=round(mk["confidence_interval"]["upper"], 6),
            )

        # Also compute OLS slope for comparison if not already computed
        if slope_linear is None:
            lr_comp = linear_regression_trend(x_years, y, alpha=alpha)
            slope_linear = round(lr_comp["slope_per_year"], 6)

        # Also compute Sen's slope if linear regression was the primary method
        if sen_slope is None:
            sen_comp = mann_kendall_test(y, alpha=alpha)
            sen_slope = round(sen_comp["sen_slope_per_year"], 6)

        assumptions = list(METHOD_ASSUMPTIONS.get(method, []))
        limitations = list(METHOD_LIMITATIONS.get(method, []))

        if ac_diag["is_autocorrelated"]:
            assumptions.append(f"Significant serial autocorrelation detected (lag-1 r = {ac_diag['lag1_autocorr']:.3f})")

        first_row = work_df.iloc[0]
        disp_unit = str(first_row.get("display_unit", "units"))
        rate_unit = f"{disp_unit}/year"

        return TrendResponse(
            dataset_id=str(first_row.get("dataset_id", "NASA Earth Science")),
            variable_id=var_id,
            unit=str(first_row.get("source_unit", "source_unit")),
            display_unit=rate_unit,
            region=str(first_row.get("region", "Pakistan")),
            period_start=work_df["timestamp"].min().strftime("%Y-%m-%d"),
            period_end=work_df["timestamp"].max().strftime("%Y-%m-%d"),
            n_observations=n_obs,
            method=method,
            trend_direction=direction,
            slope_per_year=slope_linear,
            sen_slope_per_year=sen_slope,
            p_value=p_val,
            confidence_interval=ci,
            significance_level=alpha,
            is_statistically_significant=bool(p_val < alpha if p_val is not None else False),
            multiple_testing_adjusted_p_value=None,
            assumptions=assumptions,
            limitations=limitations,
        )
