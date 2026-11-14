"""Data quality and physical bound validation for EarthScope observation tables."""

from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np


PHYSICAL_BOUNDS: Dict[str, Dict[str, float]] = {
    "t2m": {
        "raw_min": 220.0,     # Kelvin
        "raw_max": 340.0,
        "display_min": -50.0, # Celsius
        "display_max": 65.0,
    },
    "ts": {
        "raw_min": 220.0,
        "raw_max": 345.0,
        "display_min": -50.0,
        "display_max": 70.0,
    },
    "precipitation": {
        "raw_min": 0.0,
        "raw_max": 0.001,     # kg m-2 s-1 (corresponds to ~86 mm/day)
        "display_min": 0.0,
        "display_max": 2500.0,# mm/month
    },
    "evapotranspiration": {
        "raw_min": 0.0,
        "raw_max": 0.0005,
        "display_min": 0.0,
        "display_max": 600.0, # mm/month
    },
    "soil_moisture_0_10cm": {
        "raw_min": 0.0,
        "raw_max": 100.0,     # kg m-2
        "display_min": 0.0,
        "display_max": 100.0,
    },
    "soil_moisture_10_40cm": {
        "raw_min": 0.0,
        "raw_max": 300.0,     # kg m-2
        "display_min": 0.0,
        "display_max": 300.0,
    },
}

REQUIRED_COLUMNS = [
    "timestamp",
    "variable_id",
    "raw_value",
    "source_unit",
    "display_value",
    "display_unit",
    "anomaly",
    "standardized_anomaly",
    "region",
    "dataset_id",
]


def validate_processed_dataframe(df: pd.DataFrame, var_id: str) -> Tuple[bool, List[str]]:
    """Validate processed canonical dataframe against physical bounds and standard contract."""
    errors = []

    # 1. Required columns
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    if errors:
        return False, errors

    # 2. Chronological order
    if not df["timestamp"].is_monotonic_increasing:
        errors.append("Timestamps are not monotonically increasing")

    # 3. No duplicates
    if df["timestamp"].duplicated().any():
        errors.append("Duplicate timestamps detected in processed dataframe")

    # 4. Null checks
    null_counts = df[["raw_value", "display_value", "anomaly"]].isna().sum()
    if null_counts.any():
        errors.append(f"Unexpected null values found: {null_counts.to_dict()}")

    # 5. Physical bounds
    if var_id in PHYSICAL_BOUNDS:
        b = PHYSICAL_BOUNDS[var_id]
        if (df["raw_value"] < b["raw_min"]).any() or (df["raw_value"] > b["raw_max"]).any():
            errors.append(
                f"Raw values exceed bounds [{b['raw_min']}, {b['raw_max']}]: min={df['raw_value'].min()}, max={df['raw_value'].max()}"
            )
        if (df["display_value"] < b["display_min"]).any() or (df["display_value"] > b["display_max"]).any():
            errors.append(
                f"Display values exceed bounds [{b['display_min']}, {b['display_max']}]: min={df['display_value'].min()}, max={df['display_value'].max()}"
            )

    return len(errors) == 0, errors
