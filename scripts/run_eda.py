"""Comprehensive Exploratory Data Analysis execution script for EarthScope.

Generates summary statistics, correlation matrices, extreme anomaly logs,
and publication-ready visual diagnostics.
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg") # Non-interactive backend
import matplotlib.pyplot as plt

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.analytics.eda.analyzer import (
    compute_variable_descriptive_stats,
    compute_correlation_matrices,
    detect_top_extreme_anomalies,
    compute_seasonal_climatology_profile,
)

VARIABLES = [
    {"id": "t2m", "title": "2-Meter Air Temperature", "unit": "°C", "color": "#ef4444"},
    {"id": "ts", "title": "Surface Skin Temperature", "unit": "°C", "color": "#f97316"},
    {"id": "precipitation", "title": "Total Precipitation", "unit": "mm/month", "color": "#0284c7"},
    {"id": "evapotranspiration", "title": "Total Evapotranspiration", "unit": "mm/month", "color": "#10b981"},
    {"id": "soil_moisture_0_10cm", "title": "Topsoil Moisture (0-10 cm)", "unit": "kg/m²", "color": "#8b5cf6"},
    {"id": "soil_moisture_10_40cm", "title": "Rootzone Moisture (10-40 cm)", "unit": "kg/m²", "color": "#6366f1"},
]


def run_eda():
    processed_dir = Path("data/processed")
    metadata_dir = Path("data/metadata")
    figures_dir = Path("docs/figures")
    figures_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    print("=== Running EarthScope Exploratory Data Analysis ===")

    stats_dict = {}
    anomalies_dict = {}
    climatologies_dict = {}
    dfs = {}

    for var in VARIABLES:
        var_id = var["id"]
        parquet_file = processed_dir / f"{var_id}.parquet"
        df = pd.read_parquet(parquet_file)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        dfs[var_id] = df

        # 1. Descriptive stats
        st = compute_variable_descriptive_stats(df, value_col="display_value")
        st["display_unit"] = var["unit"]
        st["variable_title"] = var["title"]
        stats_dict[var_id] = st

        # 2. Extreme anomalies
        ext = detect_top_extreme_anomalies(df, var_id=var_id, top_n=5)
        anomalies_dict[var_id] = ext

        # 3. Monthly climatology profile
        clim_prof = compute_seasonal_climatology_profile(df, value_col="display_value")
        climatologies_dict[var_id] = clim_prof.to_dict(orient="records")

        print(f"Computed stats for {var['title']}: Mean = {st['mean']:.2f} {var['unit']}, Std = {st['std']:.2f}, Range = [{st['min']:.2f}, {st['max']:.2f}]")

    # Save stats JSON
    with open(metadata_dir / "eda_descriptive_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats_dict, f, indent=2)

    # Save extreme anomalies JSON
    with open(metadata_dir / "eda_extreme_anomalies.json", "w", encoding="utf-8") as f:
        json.dump(anomalies_dict, f, indent=2)

    # 4. Cross-variable correlations
    multi_file = processed_dir / "earth_system_pakistan_monthly.parquet"
    multi_df = pd.read_parquet(multi_file)
    multi_df["timestamp"] = pd.to_datetime(multi_df["timestamp"])

    corr_res = compute_correlation_matrices(multi_df, value_suffix="_value")
    with open(metadata_dir / "eda_correlations.json", "w", encoding="utf-8") as f:
        json.dump(corr_res, f, indent=2)

    print("\n=== Cross-Variable Pearson Correlation (Values) ===")
    pearson_df = pd.DataFrame(corr_res["raw_value_pearson"])
    print(pearson_df.round(3).to_string())

    print("\n=== Cross-Variable Pearson Correlation (Anomalies) ===")
    anomaly_pearson_df = pd.DataFrame(corr_res["anomaly_pearson"])
    print(anomaly_pearson_df.round(3).to_string())

    # 5. Visual Diagnostics Generation
    print("\nGenerating visual figures in docs/figures/...")

    # Plot 1: Historical Time Series (6-panel)
    fig, axes = plt.subplots(3, 2, figsize=(14, 11), sharex=True)
    axes = axes.flatten()

    for idx, var in enumerate(VARIABLES):
        ax = axes[idx]
        df = dfs[var["id"]]
        roll = df["display_value"].rolling(window=12, center=True).mean()

        ax.plot(df["timestamp"], df["display_value"], color=var["color"], alpha=0.55, linewidth=1.0, label="Monthly Observation")
        ax.plot(df["timestamp"], roll, color="black", linewidth=1.8, label="12-Month Moving Avg")

        ax.set_title(f"{var['title']} ({var['unit']})", fontsize=11, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper left", fontsize=8)

    plt.suptitle("EarthScope — 25-Year Historical Observations over Pakistan (2001–2025)", fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()
    hist_fig_path = figures_dir / "historical_timeseries_all.png"
    plt.savefig(hist_fig_path, dpi=200)
    plt.close()
    print(f"  ✓ Saved: {hist_fig_path}")

    # Plot 2: Seasonal Climatology Cycles (6-panel)
    fig, axes = plt.subplots(3, 2, figsize=(13, 10))
    axes = axes.flatten()
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for idx, var in enumerate(VARIABLES):
        ax = axes[idx]
        clim_data = pd.DataFrame(climatologies_dict[var["id"]])

        ax.plot(clim_data["month"], clim_data["mean"], color=var["color"], marker="o", linewidth=2.0, label="Climatological Mean")
        ax.fill_between(
            clim_data["month"],
            clim_data["mean"] - clim_data["std"],
            clim_data["mean"] + clim_data["std"],
            color=var["color"],
            alpha=0.2,
            label="±1σ Range"
        )
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(month_labels, fontsize=8)
        ax.set_title(f"{var['title']} Climatological Cycle", fontsize=10, fontweight="bold")
        ax.set_ylabel(var["unit"], fontsize=9)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="best", fontsize=8)

    plt.suptitle("EarthScope — Mean Annual Seasonal Cycle & Climatological Variability (2001–2020 Baseline)", fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout()
    clim_fig_path = figures_dir / "seasonal_climatology_all.png"
    plt.savefig(clim_fig_path, dpi=200)
    plt.close()
    print(f"  ✓ Saved: {clim_fig_path}")

    # Plot 3: Deseasonalized Monthly Anomalies (6-panel)
    fig, axes = plt.subplots(3, 2, figsize=(14, 11), sharex=True)
    axes = axes.flatten()

    for idx, var in enumerate(VARIABLES):
        ax = axes[idx]
        df = dfs[var["id"]]

        # Bar plot for anomalies
        pos_mask = df["anomaly"] >= 0
        neg_mask = df["anomaly"] < 0

        ax.bar(df.loc[pos_mask, "timestamp"], df.loc[pos_mask, "anomaly"], width=25, color="#ef4444" if "temp" in var["id"] or var["id"] in ("t2m", "ts") else "#0284c7", alpha=0.7, label="Positive Anomaly")
        ax.bar(df.loc[neg_mask, "timestamp"], df.loc[neg_mask, "anomaly"], width=25, color="#3b82f6" if "temp" in var["id"] or var["id"] in ("t2m", "ts") else "#f59e0b", alpha=0.7, label="Negative Anomaly")

        ax.axhline(0, color="black", linewidth=0.8, linestyle="-")
        ax.set_title(f"{var['title']} Monthly Anomaly ({var['unit']})", fontsize=10, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.4)

    plt.suptitle("EarthScope — Deseasonalized Monthly Anomalies (2001–2025)", fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()
    anom_fig_path = figures_dir / "anomaly_timeseries_all.png"
    plt.savefig(anom_fig_path, dpi=200)
    plt.close()
    print(f"  ✓ Saved: {anom_fig_path}")

    # Plot 4: Correlation Heatmap Matrix
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    var_labels = ["T2M", "TS", "Precip", "Evap", "SM 0-10cm", "SM 10-40cm"]
    p_mat = pd.DataFrame(corr_res["raw_value_pearson"]).values
    anom_mat = pd.DataFrame(corr_res["anomaly_pearson"]).values

    im1 = ax1.imshow(p_mat, cmap="coolwarm", vmin=-1, vmax=1)
    ax1.set_xticks(range(len(var_labels)))
    ax1.set_yticks(range(len(var_labels)))
    ax1.set_xticklabels(var_labels, rotation=45, ha="right", fontsize=9)
    ax1.set_yticklabels(var_labels, fontsize=9)
    ax1.set_title("Raw Observed Value Correlations (Pearson)", fontsize=11, fontweight="bold")
    for i in range(len(var_labels)):
        for j in range(len(var_labels)):
            ax1.text(j, i, f"{p_mat[i, j]:.2f}", ha="center", va="center", color="black" if abs(p_mat[i, j]) < 0.7 else "white", fontsize=8)

    im2 = ax2.imshow(anom_mat, cmap="coolwarm", vmin=-1, vmax=1)
    ax2.set_xticks(range(len(var_labels)))
    ax2.set_yticks(range(len(var_labels)))
    ax2.set_xticklabels(var_labels, rotation=45, ha="right", fontsize=9)
    ax2.set_yticklabels(var_labels, fontsize=9)
    ax2.set_title("Deseasonalized Anomaly Correlations (Pearson)", fontsize=11, fontweight="bold")
    for i in range(len(var_labels)):
        for j in range(len(var_labels)):
            ax2.text(j, i, f"{anom_mat[i, j]:.2f}", ha="center", va="center", color="black" if abs(anom_mat[i, j]) < 0.7 else "white", fontsize=8)

    fig.colorbar(im2, ax=[ax1, ax2], orientation="horizontal", fraction=0.06, pad=0.18, label="Pearson r")
    plt.suptitle("EarthScope — Cross-Variable Coupling Dynamics in Pakistan Earth System", fontsize=13, fontweight="bold")
    heatmap_path = figures_dir / "correlation_heatmaps.png"
    plt.savefig(heatmap_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Saved: {heatmap_path}")

    print("\n✓ EDA successfully finished.")


if __name__ == "__main__":
    run_eda()
