"""Run complete trend analysis across all 6 Earth-system variables for Pakistan."""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.analytics.trend_detection.engine import TrendAnalysisEngine

VARIABLES = [
    {"id": "t2m", "title": "2-Meter Air Temperature", "unit": "°C"},
    {"id": "ts", "title": "Surface Skin Temperature", "unit": "°C"},
    {"id": "precipitation", "title": "Total Precipitation", "unit": "mm/month"},
    {"id": "evapotranspiration", "title": "Total Evapotranspiration", "unit": "mm/month"},
    {"id": "soil_moisture_0_10cm", "title": "Topsoil Moisture (0-10 cm)", "unit": "kg/m²"},
    {"id": "soil_moisture_10_40cm", "title": "Rootzone Moisture (10-40 cm)", "unit": "kg/m²"},
]


def run_trend_suite():
    processed_dir = Path("data/processed")
    metadata_dir = Path("data/metadata")
    figures_dir = Path("docs/figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    engine = TrendAnalysisEngine()
    results = []

    print("=== Executing EarthScope Trend Analysis Suite (2001–2025) ===\n")

    for v in VARIABLES:
        var_id = v["id"]
        df = pd.read_parquet(processed_dir / f"{var_id}.parquet")

        # 1. Non-parametric Seasonal Mann-Kendall
        smk_res = engine.analyze_trend(df, var_id, method="seasonal_mann_kendall", deseasonalize=False)

        # 2. Deseasonalized Mann-Kendall / Modified MK
        mk_res = engine.analyze_trend(df, var_id, method="mann_kendall", deseasonalize=True)

        # 3. Parametric Linear Regression
        ols_res = engine.analyze_trend(df, var_id, method="linear_regression", deseasonalize=True)

        res_entry = {
            "variable_id": var_id,
            "variable_title": v["title"],
            "unit": v["unit"],
            "rate_unit": f"{v['unit']}/decade",
            "n_observations": mk_res.n_observations,
            "period": f"{mk_res.period_start} to {mk_res.period_end}",
            "seasonal_mk": {
                "direction": smk_res.trend_direction,
                "sen_slope_per_decade": round(smk_res.sen_slope_per_year * 10.0, 4) if smk_res.sen_slope_per_year else None,
                "p_value": smk_res.p_value,
                "is_significant": smk_res.is_statistically_significant,
            },
            "deseasonalized_mk": {
                "method_applied": mk_res.method,
                "direction": mk_res.trend_direction,
                "sen_slope_per_decade": round(mk_res.sen_slope_per_year * 10.0, 4) if mk_res.sen_slope_per_year else None,
                "ci_lower_decade": round(mk_res.confidence_interval.lower * 10.0, 4) if mk_res.confidence_interval.lower else None,
                "ci_upper_decade": round(mk_res.confidence_interval.upper * 10.0, 4) if mk_res.confidence_interval.upper else None,
                "p_value": mk_res.p_value,
                "is_significant": mk_res.is_statistically_significant,
            },
            "ols_linear": {
                "direction": ols_res.trend_direction,
                "slope_per_decade": round(ols_res.slope_per_year * 10.0, 4) if ols_res.slope_per_year else None,
                "p_value": ols_res.p_value,
                "is_significant": ols_res.is_statistically_significant,
            },
        }
        results.append(res_entry)

        print(f"[{v['title']}]")
        print(f"  Sen's Slope (Deseasonalized): {res_entry['deseasonalized_mk']['sen_slope_per_decade']} {v['unit']}/decade (p = {res_entry['deseasonalized_mk']['p_value']}, {res_entry['deseasonalized_mk']['direction']})")
        print(f"  95% CI: [{res_entry['deseasonalized_mk']['ci_lower_decade']}, {res_entry['deseasonalized_mk']['ci_upper_decade']}]")
        print(f"  OLS Slope: {res_entry['ols_linear']['slope_per_decade']} {v['unit']}/decade (p = {res_entry['ols_linear']['p_value']})\n")

    # Save JSON results
    json_path = metadata_dir / "trend_analysis_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved trend results to: {json_path}")

    # Generate 6-panel trend plot
    fig, axes = plt.subplots(3, 2, figsize=(14, 11), sharex=True)
    axes = axes.flatten()

    for idx, (v, res) in enumerate(zip(VARIABLES, results)):
        ax = axes[idx]
        df = pd.read_parquet(processed_dir / f"{v['id']}.parquet")
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        t0 = df["timestamp"].iloc[0]
        x_years = (df["timestamp"] - t0).dt.days.values / 365.25

        # Plot anomaly
        ax.plot(df["timestamp"], df["anomaly"], color="#94a3b8", alpha=0.5, label="Observed Monthly Anomaly")

        # Fitted Sen's trend line on anomaly
        sen_per_yr = res["deseasonalized_mk"]["sen_slope_per_decade"] / 10.0
        # Fit intercept so line passes through median anomaly
        intercept = np.median(df["anomaly"]) - sen_per_yr * np.median(x_years)
        y_trend = intercept + sen_per_yr * x_years

        color = "#ef4444" if res["deseasonalized_mk"]["direction"] == "increasing" else ("#0284c7" if res["deseasonalized_mk"]["direction"] == "decreasing" else "#64748b")
        trend_label = f"Sen's Slope: {res['deseasonalized_mk']['sen_slope_per_decade']:+.3f} {v['unit']}/decade (p={res['deseasonalized_mk']['p_value']:.4f})"
        ax.plot(df["timestamp"], y_trend, color=color, linewidth=2.0, label=trend_label)

        ax.axhline(0, color="black", linestyle=":", alpha=0.4)
        ax.set_title(f"{v['title']} Trend ({v['unit']})", fontsize=11, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="upper left", fontsize=8)

    plt.suptitle("EarthScope — Statistical Trend Detection over Pakistan (2001–2025)", fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout()
    trend_plot_path = figures_dir / "trend_fitted_plots.png"
    plt.savefig(trend_plot_path, dpi=200)
    plt.close()
    print(f"Saved trend figures to: {trend_plot_path}")


if __name__ == "__main__":
    run_trend_suite()
