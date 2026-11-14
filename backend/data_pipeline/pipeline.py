"""Master Data Pipeline Orchestrator for EarthScope.

Loads all raw NASA Giovanni datasets, executes unit conversions,
computes reference climatologies and anomalies, validates against physical constraints,
and outputs canonical processed datasets and lineage tracking.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np

from backend.data_pipeline.ingestion.loader import (
    VARIABLE_CONFIGS,
    find_raw_file,
    load_raw_giovanni_csv,
)
from backend.data_pipeline.preprocessing.units import convert_variable_to_display_unit
from backend.data_pipeline.preprocessing.anomalies import ClimatologyEngine
from backend.data_pipeline.validation.validator import validate_processed_dataframe


class EarthScopePipeline:
    """End-to-end reproducible pipeline for EarthScope."""

    def __init__(
        self,
        raw_dir: Path = Path("datasets"),
        processed_dir: Path = Path("data/processed"),
        metadata_dir: Path = Path("data/metadata"),
        baseline_start: str = "2001-01-01",
        baseline_end: str = "2020-12-31",
    ):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.metadata_dir = metadata_dir
        self.baseline_start = baseline_start
        self.baseline_end = baseline_end
        self.climatology_engine = ClimatologyEngine(baseline_start, baseline_end)

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def process_variable(self, var_id: str) -> Tuple_Pipeline:
        """Execute full transformation and validation pipeline for a single variable."""
        cfg = VARIABLE_CONFIGS[var_id]
        raw_file = find_raw_file(self.raw_dir, var_id)

        # 1. Load raw CSV
        meta, df = load_raw_giovanni_csv(raw_file, declared_fill=cfg.get("fill_value"))

        # 2. Convert to display units
        disp_vals, disp_unit = convert_variable_to_display_unit(var_id, df["raw_value"], df["timestamp"])
        df["display_value"] = disp_vals
        df["display_unit"] = disp_unit
        df["source_unit"] = cfg["source_unit"]
        df["variable_id"] = var_id
        df["region"] = "Pakistan"
        df["dataset_id"] = cfg["platform"]

        # 3. Compute climatology and anomalies on display_value
        clim = self.climatology_engine.fit_climatology(df, value_col="display_value", time_col="timestamp")
        decomp_df = self.climatology_engine.calculate_anomalies(
            df, value_col="display_value", climatology=clim, time_col="timestamp"
        )

        # 4. Standard observation order
        cols = [
            "timestamp",
            "variable_id",
            "region",
            "dataset_id",
            "raw_value",
            "source_unit",
            "display_value",
            "display_unit",
            "climatology_mean",
            "climatology_std",
            "anomaly",
            "standardized_anomaly",
        ]
        final_df = decomp_df[cols].copy()

        # 5. Validation
        is_valid, errors = validate_processed_dataframe(final_df, var_id)
        if not is_valid:
            raise ValueError(f"Validation failed for variable {var_id}: {errors}")

        # 6. Save individual outputs
        parquet_path = self.processed_dir / f"{var_id}.parquet"
        csv_path = self.processed_dir / f"{var_id}.csv"
        final_df.to_parquet(parquet_path, index=False)
        final_df.to_csv(csv_path, index=False)

        # Save monthly climatology lookup
        clim_path = self.processed_dir / f"{var_id}_climatology.csv"
        clim.to_csv(clim_path)

        lineage_entry = {
            "variable_id": var_id,
            "raw_file": str(raw_file.as_posix()),
            "output_parquet": str(parquet_path.as_posix()),
            "output_csv": str(csv_path.as_posix()),
            "total_records": len(final_df),
            "period_start": final_df["timestamp"].min().strftime("%Y-%m-%d"),
            "period_end": final_df["timestamp"].max().strftime("%Y-%m-%d"),
            "display_unit": disp_unit,
            "baseline_period": f"{self.baseline_start} to {self.baseline_end}",
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

        return final_df, lineage_entry

    def run_all(self) -> Dict[str, Any]:
        """Run pipeline across all configured variables and create merged Earth-system dataset."""
        print(f"=== Running EarthScope Data Pipeline ===")
        lineage_entries = []
        dfs = {}

        for var_id in VARIABLE_CONFIGS:
            print(f"Processing variable: {var_id}...")
            df, lineage = self.process_variable(var_id)
            dfs[var_id] = df
            lineage_entries.append(lineage)
            print(f"  ✓ {var_id}: {len(df)} records ({lineage['period_start']} to {lineage['period_end']}) saved.")

        # Create combined wide dataset aligned on timestamp
        print("\nBuilding multi-variable coupled dataset...")
        base_df = None
        for var_id, df in dfs.items():
            sub = df[["timestamp", "display_value", "anomaly"]].copy()
            sub.columns = ["timestamp", f"{var_id}_value", f"{var_id}_anomaly"]
            if base_df is None:
                base_df = sub
            else:
                base_df = base_df.merge(sub, on="timestamp", how="inner")

        base_df = base_df.sort_values("timestamp").reset_index(drop=True)
        wide_parquet = self.processed_dir / "earth_system_pakistan_monthly.parquet"
        wide_csv = self.processed_dir / "earth_system_pakistan_monthly.csv"
        base_df.to_parquet(wide_parquet, index=False)
        base_df.to_csv(wide_csv, index=False)
        print(f"  ✓ Multi-variable dataset saved: {len(base_df)} aligned months ({base_df['timestamp'].min().strftime('%Y-%m-%d')} to {base_df['timestamp'].max().strftime('%Y-%m-%d')})")

        # Save lineage metadata
        lineage_doc = {
            "pipeline_name": "EarthScope Ingestion & Preprocessing Pipeline",
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
            "target_region": "Pakistan",
            "baseline_period": f"{self.baseline_start} to {self.baseline_end}",
            "variables_processed": len(lineage_entries),
            "multi_variable_aligned_months": len(base_df),
            "lineage": lineage_entries,
        }

        lineage_path = self.metadata_dir / "data_lineage.json"
        with open(lineage_path, "w", encoding="utf-8") as f:
            json.dump(lineage_doc, f, indent=2)
        print(f"Lineage metadata written to: {lineage_path}")

        return lineage_doc


from typing import Tuple as Tuple_Pipeline
