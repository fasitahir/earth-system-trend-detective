"""Raw NASA Giovanni dataset loader.

Preserves raw source files strictly as read-only. Parses CSV header metadata,
standardizes timestamp indices, handles declared fill values explicitly,
and loads into standard pandas DataFrames.
"""

from io import StringIO
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


VARIABLE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "t2m": {
        "folder": "Air Temperature – NASA Giovanni (MERRA-2)",
        "csv_pattern": "*T2M*.csv",
        "var_name": "2-Meter Air Temperature",
        "raw_col_prefix": "mean_M2TMNXSLV",
        "source_unit": "K",
        "platform": "MERRA-2 Reanalysis (M2TMNXSLV v5.12.4)",
        "domain": "Atmosphere",
        "fill_value": 1e15,
    },
    "ts": {
        "folder": "Surface Skin Temperature – NASA Giovanni (MERRA-2)",
        "csv_pattern": "*TS*.csv",
        "var_name": "Surface Skin Temperature",
        "raw_col_prefix": "mean_M2TMNXSLV",
        "source_unit": "K",
        "platform": "MERRA-2 Reanalysis (M2TMNXSLV v5.12.4)",
        "domain": "Land Surface",
        "fill_value": 1e15,
    },
    "precipitation": {
        "folder": "Precipitation – NASA Giovanni (MERRA-2)",
        "csv_pattern": "*PRECTOTCORR*.csv",
        "var_name": "Bias-Corrected Total Precipitation",
        "raw_col_prefix": "mean_M2TMNXFLX",
        "source_unit": "kg m-2 s-1",
        "platform": "MERRA-2 Reanalysis (M2TMNXFLX v5.12.4)",
        "domain": "Atmosphere / Hydrology",
        "fill_value": 1e15,
    },
    "evapotranspiration": {
        "folder": "Total Evapotranspiration (Evap_tavg) — NASA Giovanni (GLDAS-2.1)",
        "csv_pattern": "*Evap_tavg*.csv",
        "var_name": "Total Evapotranspiration Flux",
        "raw_col_prefix": "mean_GLDAS_NOAH10",
        "source_unit": "kg m-2 s-1",
        "platform": "GLDAS Noah LSM L4 v2.1",
        "domain": "Hydrology / Land Surface",
        "fill_value": -9999.0,
    },
    "soil_moisture_0_10cm": {
        "folder": "Soil Moisture – NASA Giovanni (GLDAS)/0-10cm",
        "csv_pattern": "*SoilMoi0_10cm*.csv",
        "var_name": "Soil Moisture (0-10 cm)",
        "raw_col_prefix": "mean_GLDAS_NOAH10",
        "source_unit": "kg m-2",
        "platform": "GLDAS Noah LSM L4 v2.1",
        "domain": "Hydrology / Soil",
        "fill_value": -9999.0,
    },
    "soil_moisture_10_40cm": {
        "folder": "Soil Moisture – NASA Giovanni (GLDAS)/10-40cm",
        "csv_pattern": "*SoilMoi10_40cm*.csv",
        "var_name": "Soil Moisture (10-40 cm)",
        "raw_col_prefix": "GLDAS_NOAH10",
        "source_unit": "kg m-2",
        "platform": "GLDAS Noah LSM L4 v2.1",
        "domain": "Hydrology / Soil",
        "fill_value": -9999.0,
    },
}


def find_raw_file(base_raw_dir: Path, var_key: str) -> Path:
    """Locate the raw CSV file for a given variable key."""
    if var_key not in VARIABLE_CONFIGS:
        raise ValueError(f"Unknown variable key '{var_key}'. Supported: {list(VARIABLE_CONFIGS.keys())}")
    cfg = VARIABLE_CONFIGS[var_key]
    folder = base_raw_dir / cfg["folder"]
    matches = list(folder.glob(cfg["csv_pattern"]))
    if not matches:
        raise FileNotFoundError(f"No CSV matching {cfg['csv_pattern']} in {folder}")
    return matches[0]


def load_raw_giovanni_csv(filepath: Path, declared_fill: float = None) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """Load and parse NASA Giovanni CSV into metadata dictionary and sanitized DataFrame.
    
    Guarantees:
    - Raw file is opened read-only.
    - Declared fill values are mapped to np.nan (never 0).
    - Timestamp is normalized to first of the month YYYY-MM-01.
    - Duplicate timestamps are detected and rejected.
    """
    metadata: Dict[str, Any] = {}
    lines = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    header_end_idx = 0
    detected_fill = declared_fill

    for idx, line in enumerate(lines):
        line_str = line.strip()
        if not line_str:
            continue
        if line_str.startswith("time,"):
            header_end_idx = idx
            break
        elif line_str.startswith("Title:,"):
            metadata["title"] = line_str.split("Title:,", 1)[1].strip(' "')
        elif line_str.startswith("User Start Date:,"):
            metadata["user_start_date"] = line_str.split("User Start Date:,", 1)[1].strip()
        elif line_str.startswith("User End Date:,"):
            metadata["user_end_date"] = line_str.split("User End Date:,", 1)[1].strip()
        elif line_str.startswith("URL to Reproduce Results:,"):
            metadata["reproduce_url"] = line_str.split("URL to Reproduce Results:,", 1)[1].strip(' "')
        elif "Fill Value" in line_str:
            parts = line_str.split(":,")
            if len(parts) == 2:
                try:
                    detected_fill = float(parts[1].strip())
                    metadata["detected_fill_value"] = detected_fill
                except ValueError:
                    metadata["detected_fill_value"] = parts[1].strip()

    csv_data = "".join(lines[header_end_idx:])
    df = pd.read_csv(StringIO(csv_data))
    df.columns = [c.strip() for c in df.columns]

    time_col = df.columns[0]
    val_col = df.columns[1]

    # Convert timestamps
    df["timestamp"] = pd.to_datetime(df[time_col]).dt.to_period("M").dt.to_timestamp()
    
    # Sort chronologically
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Check for duplicate timestamps
    duplicates = df[df.duplicated(subset=["timestamp"], keep=False)]
    if not duplicates.empty:
        raise ValueError(f"Duplicate timestamps found in {filepath}: {duplicates['timestamp'].tolist()}")

    # Map fill values to NaN
    raw_vals = df[val_col].astype(float).copy()
    if detected_fill is not None:
        raw_vals = raw_vals.replace(detected_fill, np.nan)
        if detected_fill > 1e10:
            raw_vals = raw_vals.mask(raw_vals >= 1e10, np.nan)

    clean_df = pd.DataFrame({
        "timestamp": df["timestamp"],
        "raw_value": raw_vals,
    })

    return metadata, clean_df
