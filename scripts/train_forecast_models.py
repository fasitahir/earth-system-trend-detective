"""Comprehensive model ladder training, evaluation, and forward projection script."""

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

from backend.ml.evaluation.validator import ChronologicalHoldoutEvaluator
from backend.ml.inference.service import ForecastInferenceService

VARIABLES = [
    {"id": "t2m", "title": "2-Meter Air Temperature", "unit": "°C"},
    {"id": "ts", "title": "Surface Skin Temperature", "unit": "°C"},
    {"id": "precipitation", "title": "Total Precipitation", "unit": "mm/month"},
    {"id": "evapotranspiration", "title": "Total Evapotranspiration", "unit": "mm/month"},
    {"id": "soil_moisture_0_10cm", "title": "Topsoil Moisture (0-10 cm)", "unit": "kg/m²"},
    {"id": "soil_moisture_10_40cm", "title": "Rootzone Moisture (10-40 cm)", "unit": "kg/m²"},
]


def run_forecasting_pipeline():
    processed_dir = Path("data/processed")
    metadata_dir = Path("data/metadata")
    figures_dir = Path("docs/figures")
    figures_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    evaluator = ChronologicalHoldoutEvaluator(cutoff_date="2022-12-01")
    inference_service = ForecastInferenceService()

    all_evaluations = {}
    forward_forecasts = {}

    print("=== Training & Evaluating EarthScope Model Ladder (2001–2025) ===\n")

    for v in VARIABLES:
        var_id = v["id"]
        df = pd.read_parquet(processed_dir / f"{var_id}.parquet")

        # 1. Chronological Holdout Evaluation
        eval_res = evaluator.evaluate_all_models(df, var_id=var_id, value_col="display_value")
        all_evaluations[var_id] = eval_res

        # 2. 24-Month Forward Projection (using best-performing ML model or benchmark)
        best_model = "ridge_lag"
        fc_res = inference_service.generate_forecast(
            df=df, var_id=var_id, horizon_months=24, model_id=best_model, confidence_level=0.95
        )
        forward_forecasts[var_id] = fc_res.model_dump()

        print(f"[{v['title']}] Holdout Evaluation (Test: {eval_res['test_period']}, N={eval_res['test_observations']})")
        print(f"  {'Model':<35} | {'MAE':>8} | {'RMSE':>8} | {'R²':>8} | {'Skill vs Naive':>14}")
        print("  " + "-" * 75)
        for m_key, m_info in eval_res["models"].items():
            met = m_info["metrics"]
            skill_str = f"{met.get('skill_score_vs_seasonal_naive', 0):+.2%}"
            print(f"  {m_info['model_name']:<35} | {met['mae']:>8.2f} | {met['rmse']:>8.2f} | {met['r2_score']:>8.2f} | {skill_str:>14}")
        print()

    # Save metrics JSON
    metrics_path = metadata_dir / "model_evaluation_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(all_evaluations, f, indent=2)
    print(f"Saved evaluation metrics to: {metrics_path}")

    # Plot 1: Out-of-Sample Holdout Actual vs Predicted (6-panel)
    fig, axes = plt.subplots(3, 2, figsize=(14, 11), sharex=True)
    axes = axes.flatten()

    for idx, v in enumerate(VARIABLES):
        ax = axes[idx]
        ev = all_evaluations[v["id"]]
        preds = ev["holdout_predictions"]
        test_dates = pd.to_datetime(preds["test_timestamps"])

        ax.plot(test_dates, preds["actual"], color="black", linewidth=2.0, marker="o", markersize=4, label="Ground Truth (Actual)")
        ax.plot(test_dates, preds["seasonal_naive"], color="#94a3b8", linestyle="--", linewidth=1.5, label="Seasonal Naive Baseline")
        ax.plot(test_dates, preds["ridge_lag"], color="#0284c7", linewidth=2.0, label="Lagged Ridge Model")
        ax.plot(test_dates, preds["random_forest"], color="#10b981", linewidth=1.5, linestyle=":", label="Random Forest Model")

        ax.set_title(f"{v['title']} Holdout (2023–2025)", fontsize=10, fontweight="bold")
        ax.set_ylabel(v["unit"], fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper left", fontsize=7)

    plt.suptitle("EarthScope — Chronological Out-of-Sample Holdout Evaluation (2023–2025)", fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout()
    holdout_plot_path = figures_dir / "forecast_holdout_comparison.png"
    plt.savefig(holdout_plot_path, dpi=200)
    plt.close()
    print(f"Saved holdout figure to: {holdout_plot_path}")

    # Plot 2: 24-Month Forward Projections with 95% Confidence Intervals
    fig, axes = plt.subplots(3, 2, figsize=(14, 11))
    axes = axes.flatten()

    for idx, v in enumerate(VARIABLES):
        ax = axes[idx]
        df = pd.read_parquet(processed_dir / f"{v['id']}.parquet")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        recent_df = df.iloc[-36:].copy() # Last 3 years of observations

        fc = forward_forecasts[v["id"]]
        fc_pts = fc["predictions"]
        fc_dates = pd.to_datetime([p["timestamp"] for p in fc_pts])
        fc_vals = [p["predicted_value"] for p in fc_pts]
        fc_low = [p["lower_bound"] for p in fc_pts]
        fc_high = [p["upper_bound"] for p in fc_pts]

        # Observations
        ax.plot(recent_df["timestamp"], recent_df["display_value"], color="black", linewidth=1.8, label="Observed History")

        # Forecast line
        ax.plot(fc_dates, fc_vals, color="#0ea5e9", linewidth=2.2, label=f"Ridge Forecast (to {fc_dates[-1].strftime('%Y-%m')})")

        # Uncertainty band
        ax.fill_between(fc_dates, fc_low, fc_high, color="#0ea5e9", alpha=0.2, label="95% Prediction Interval")

        # Forecast origin line
        ax.axvline(recent_df["timestamp"].iloc[-1], color="#ef4444", linestyle="--", linewidth=1.2, label="Forecast Origin")

        ax.set_title(f"{v['title']} 24-Month Ahead Projection", fontsize=10, fontweight="bold")
        ax.set_ylabel(v["unit"], fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="upper left", fontsize=7)

    plt.suptitle("EarthScope — 24-Month Forward Predictions with Calibrated Uncertainty", fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout()
    forward_plot_path = figures_dir / "forecast_forward_24m.png"
    plt.savefig(forward_plot_path, dpi=200)
    plt.close()
    print(f"Saved 24m forward projection figure to: {forward_plot_path}")


if __name__ == "__main__":
    run_forecasting_pipeline()
