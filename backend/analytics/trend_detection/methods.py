"""Statistical trend detection implementations.

Provides:
- Parametric Ordinary Least Squares (OLS) regression
- Non-parametric Mann-Kendall test
- Sen's slope estimator with exact non-parametric confidence intervals
- Yue-Pilon Pre-whitened Modified Mann-Kendall for autocorrelated series
- Seasonal Mann-Kendall (Hirsch et al. 1982)
- Serial autocorrelation diagnostics
"""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import pandas as pd
from scipy import stats


def diagnose_autocorrelation(y: np.ndarray, max_lag: int = 12) -> Dict[str, Any]:
    """Compute autocorrelation coefficients up to max_lag and lag-1 significance."""
    n = len(y)
    if n < max_lag + 2:
        max_lag = max(1, n - 2)

    mean_y = np.mean(y)
    var_y = np.var(y)
    if var_y < 1e-12:
        return {"lag1_autocorr": 0.0, "is_autocorrelated": False, "acf": [1.0] + [0.0] * max_lag}

    acf = []
    for lag in range(max_lag + 1):
        if lag == 0:
            acf.append(1.0)
        else:
            c_k = np.sum((y[:-lag] - mean_y) * (y[lag:] - mean_y)) / (n * var_y)
            acf.append(float(c_k))

    r1 = acf[1] if len(acf) > 1 else 0.0
    # Two-sided 95% critical bound for white noise: ± 1.96 / sqrt(n)
    crit = 1.96 / np.sqrt(n)
    is_sig = abs(r1) > crit

    return {
        "lag1_autocorr": float(r1),
        "critical_bound_95": float(crit),
        "is_autocorrelated": bool(is_sig),
        "acf": [float(x) for x in acf],
    }


def linear_regression_trend(
    x_years: np.ndarray,
    y: np.ndarray,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """Fit OLS linear regression: y = slope * x_years + intercept.
    
    Returns slope in unit/year, p-value, R-squared, standard error,
    and 100*(1-alpha)% confidence interval for slope.
    """
    n = len(y)
    if n < 3:
        raise ValueError("Linear regression requires at least 3 points.")

    res = stats.linregress(x_years, y)
    t_crit = stats.t.ppf(1 - alpha / 2.0, df=n - 2)
    ci_lower = float(res.slope - t_crit * res.stderr)
    ci_upper = float(res.slope + t_crit * res.stderr)

    direction = "no_detected_trend"
    if res.pvalue < alpha:
        direction = "increasing" if res.slope > 0 else "decreasing"

    return {
        "method": "linear_regression",
        "slope_per_year": float(res.slope),
        "slope_per_decade": float(res.slope * 10.0),
        "intercept": float(res.intercept),
        "p_value": float(res.pvalue),
        "r_squared": float(res.rvalue ** 2),
        "std_err": float(res.stderr),
        "confidence_interval": {
            "lower": ci_lower,
            "upper": ci_upper,
        },
        "trend_direction": direction,
        "is_statistically_significant": bool(res.pvalue < alpha),
    }


def sens_slope_estimator(
    y: np.ndarray,
    x_years: Optional[np.ndarray] = None,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """Calculate Sen's robust slope estimator and exact non-parametric confidence interval.
    
    Sen's slope is the median of all pairwise slopes: (y[j] - y[i]) / (x[j] - x[i]) for j > i.
    If x_years is not provided, defaults to elapsed step / 12 for monthly intervals (unit/year).
    """
    n = len(y)
    if n < 3:
        raise ValueError("Sen's slope requires at least 3 observations.")

    if x_years is None:
        # Default step is 1/12 year (monthly)
        x_years = np.arange(n) / 12.0

    slopes = []
    for i in range(n - 1):
        dx = x_years[i + 1:] - x_years[i]
        dy = y[i + 1:] - y[i]
        # Ignore identical x coordinates if any
        valid = dx != 0
        slopes.extend((dy[valid] / dx[valid]).tolist())

    slopes = np.sort(np.array(slopes))
    n_slopes = len(slopes)
    median_slope = float(np.median(slopes))

    # Variance of Mann-Kendall S statistic for CI calculation
    # Ties in y
    _, tie_counts = np.unique(y, return_counts=True)
    tie_term = np.sum(tie_counts * (tie_counts - 1) * (2 * tie_counts + 5))
    var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0

    z_crit = stats.norm.ppf(1 - alpha / 2.0)
    c_alpha = z_crit * np.sqrt(var_s)

    m1 = int(np.floor((n_slopes - c_alpha) / 2.0))
    m2 = int(np.ceil((n_slopes + c_alpha) / 2.0))

    m1 = max(0, min(m1, n_slopes - 1))
    m2 = max(0, min(m2, n_slopes - 1))

    ci_lower = float(slopes[m1])
    ci_upper = float(slopes[m2])

    return {
        "sen_slope_per_year": median_slope,
        "sen_slope_per_decade": median_slope * 10.0,
        "confidence_interval": {
            "lower": ci_lower,
            "upper": ci_upper,
        },
    }


def mann_kendall_test(
    y: np.ndarray,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """Standard non-parametric Mann-Kendall test for monotonic trends."""
    n = len(y)
    if n < 4:
        raise ValueError("Mann-Kendall requires at least 4 observations.")

    # Calculate Mann-Kendall S statistic
    # S = sum(sgn(y[j] - y[i])) for j > i
    s = 0
    for i in range(n - 1):
        diff = y[i + 1:] - y[i]
        s += int(np.sum(np.sign(diff)))

    # Ties in y
    _, tie_counts = np.unique(y, return_counts=True)
    tie_term = np.sum(tie_counts * (tie_counts - 1) * (2 * tie_counts + 5))
    var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0

    # Continuity correction
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0.0

    # Two-tailed p-value
    p_val = float(2.0 * (1.0 - stats.norm.cdf(abs(z))))

    direction = "no_detected_trend"
    if p_val < alpha:
        direction = "increasing" if s > 0 else "decreasing"

    # Compute Sen's slope
    sen = sens_slope_estimator(y, alpha=alpha)

    return {
        "method": "mann_kendall",
        "s_statistic": int(s),
        "z_statistic": float(z),
        "p_value": p_val,
        "trend_direction": direction,
        "is_statistically_significant": bool(p_val < alpha),
        "sen_slope_per_year": sen["sen_slope_per_year"],
        "sen_slope_per_decade": sen["sen_slope_per_decade"],
        "confidence_interval": sen["confidence_interval"],
    }


def modified_mann_kendall_yue_pilon(
    y: np.ndarray,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """Modified Mann-Kendall test with Yue-Pilon (2002) Trend-Free Pre-Whitening (TFPW).
    
    Removes lag-1 serial autocorrelation before testing monotonic trend significance,
    preventing spurious false-positive trend detection in autocorrelated series.
    """
    n = len(y)
    sen = sens_slope_estimator(y, alpha=alpha)
    slope = sen["sen_slope_per_year"] / 12.0 # monthly step slope

    # 1. Remove Sen's linear trend
    detrended = y - slope * np.arange(n)

    # 2. Estimate lag-1 autocorrelation r1
    r1 = diagnose_autocorrelation(detrended)["lag1_autocorr"]

    # 3. Pre-whiten residual series if r1 is significant
    if abs(r1) > 0.05:
        prewhitened = detrended[1:] - r1 * detrended[:-1]
        # 4. Blend trend back in
        blended = prewhitened + slope * np.arange(1, n)
    else:
        blended = y

    # 5. Run Mann-Kendall on blended series
    mk_res = mann_kendall_test(blended, alpha=alpha)
    mk_res["method"] = "modified_mann_kendall_yue_pilon"
    mk_res["lag1_autocorr_removed"] = float(r1)
    # Restore original un-whitened Sen's slope for true real-world magnitude
    mk_res["sen_slope_per_year"] = sen["sen_slope_per_year"]
    mk_res["sen_slope_per_decade"] = sen["sen_slope_per_decade"]
    mk_res["confidence_interval"] = sen["confidence_interval"]

    return mk_res


def seasonal_mann_kendall_test(
    y: np.ndarray,
    period: int = 12,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """Seasonal Mann-Kendall test (Hirsch, Slack, and Smith, 1982).
    
    Computes Mann-Kendall test across each of the 12 individual months independently
    and pools their S statistics and variances, eliminating seasonal cycle distortions.
    """
    n = len(y)
    n_years = n // period
    if n_years < 3:
        raise ValueError(f"Seasonal Mann-Kendall requires at least 3 full years (got {n_years}).")

    s_total = 0
    var_s_total = 0.0
    season_slopes = []

    for m in range(period):
        season_vals = y[m::period]
        k = len(season_vals)
        if k < 2:
            continue

        # Season S
        s_m = 0
        for i in range(k - 1):
            s_m += int(np.sum(np.sign(season_vals[i + 1:] - season_vals[i])))
        s_total += s_m

        # Season Var(S)
        _, tie_counts = np.unique(season_vals, return_counts=True)
        tie_term = np.sum(tie_counts * (tie_counts - 1) * (2 * tie_counts + 5))
        var_s_m = (k * (k - 1) * (2 * k + 5) - tie_term) / 18.0
        var_s_total += var_s_m

        # Pairwise slopes for this season (dt = 1 year)
        for i in range(k - 1):
            dy = season_vals[i + 1:] - season_vals[i]
            dt = np.arange(1, k - i)
            season_slopes.extend((dy / dt).tolist())

    if var_s_total == 0:
        z = 0.0
    elif s_total > 0:
        z = (s_total - 1) / np.sqrt(var_s_total)
    elif s_total < 0:
        z = (s_total + 1) / np.sqrt(var_s_total)
    else:
        z = 0.0

    p_val = float(2.0 * (1.0 - stats.norm.cdf(abs(z))))
    direction = "no_detected_trend"
    if p_val < alpha:
        direction = "increasing" if s_total > 0 else "decreasing"

    median_slope = float(np.median(season_slopes)) if season_slopes else 0.0

    # Confidence interval on pooled seasonal slopes
    season_slopes = np.sort(np.array(season_slopes))
    n_slopes = len(season_slopes)
    z_crit = stats.norm.ppf(1 - alpha / 2.0)
    c_alpha = z_crit * np.sqrt(var_s_total)

    m1 = max(0, min(int(np.floor((n_slopes - c_alpha) / 2.0)), n_slopes - 1))
    m2 = max(0, min(int(np.ceil((n_slopes + c_alpha) / 2.0)), n_slopes - 1))

    return {
        "method": "seasonal_mann_kendall",
        "s_statistic": int(s_total),
        "z_statistic": float(z),
        "p_value": p_val,
        "trend_direction": direction,
        "is_statistically_significant": bool(p_val < alpha),
        "sen_slope_per_year": median_slope,
        "sen_slope_per_decade": median_slope * 10.0,
        "confidence_interval": {
            "lower": float(season_slopes[m1]),
            "upper": float(season_slopes[m2]),
        },
    }
