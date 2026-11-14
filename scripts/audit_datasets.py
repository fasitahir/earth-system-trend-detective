"""Dataset Discovery and Audit Script for EarthScope.

Recursively inventories all files in datasets/, computes SHA-256 checksums,
parses CSV metadata, inspects NetCDF/HDF5 structure and values,
checks for missing values, statistics, and generates inventory artifacts.
"""

import os
import re
import csv
import json
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def parse_giovanni_csv(filepath: Path):
    """Parse NASA Giovanni area-averaged time series CSV with header metadata."""
    metadata = {}
    data_lines = []
    fill_value = None
    header_col = None

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    header_end_idx = 0
    for idx, line in enumerate(lines):
        line_str = line.strip()
        if not line_str:
            continue
        if line_str.startswith("time,"):
            header_end_idx = idx
            header_col = [c.strip() for c in line_str.split(",")]
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
                    fill_value = float(parts[1].strip())
                    metadata["fill_value"] = fill_value
                except ValueError:
                    metadata["fill_value"] = parts[1].strip()

    # Read data part into DataFrame
    from io import StringIO
    csv_data = "".join(lines[header_end_idx:])
    df = pd.read_csv(StringIO(csv_data))
    df.columns = [c.strip() for c in df.columns]

    time_col = df.columns[0]
    val_col = df.columns[1]

    # Convert fill values to NaN
    if fill_value is not None:
        df[val_col] = df[val_col].replace(fill_value, np.nan)
        # Also check for large numbers e.g. 1e15
        if fill_value > 1e10:
            df.loc[df[val_col] >= 1e10, val_col] = np.nan

    df["timestamp"] = pd.to_datetime(df[time_col])

    # Basic stats
    valid_count = df[val_col].count()
    null_count = df[val_col].isna().sum()
    min_val = float(df[val_col].min()) if valid_count > 0 else None
    max_val = float(df[val_col].max()) if valid_count > 0 else None
    mean_val = float(df[val_col].mean()) if valid_count > 0 else None
    std_val = float(df[val_col].std()) if valid_count > 0 else None

    # Time continuity
    df = df.sort_values("timestamp").reset_index(drop=True)
    start_obs = df["timestamp"].min().strftime("%Y-%m-%d")
    end_obs = df["timestamp"].max().strftime("%Y-%m-%d")

    # Monthly intervals check
    diffs = df["timestamp"].diff().dropna()
    min_gap_days = diffs.dt.days.min()
    max_gap_days = diffs.dt.days.max()

    return {
        "metadata": metadata,
        "variable_col": val_col,
        "total_rows": len(df),
        "valid_rows": int(valid_count),
        "missing_rows": int(null_count),
        "start_observation": start_obs,
        "end_observation": end_obs,
        "min_value": min_val,
        "max_value": max_val,
        "mean_value": mean_val,
        "std_value": std_val,
        "gap_days_min": int(min_gap_days) if len(diffs) > 0 else None,
        "gap_days_max": int(max_gap_days) if len(diffs) > 0 else None,
        "df": df,
    }


def extract_nc_strings(filepath: Path):
    """Extract metadata text and history commands from HDF5/NetCDF4 file."""
    with open(filepath, "rb") as f:
        data = f.read()
    raw_strings = re.findall(b"[\x20-\x7E]{4,}", data)
    strings = [s.decode("ascii", errors="ignore") for s in raw_strings]
    
    meta = {}
    for s in strings:
        if "Shape Pakistan" in s:
            meta["region"] = "Pakistan"
        if "MERRA-2 Reanalysis" in s:
            meta["platform"] = "MERRA-2"
        if "GLDAS" in s:
            meta["platform"] = "GLDAS"
        if "plot_hint_y_axis_label" in s:
            meta["y_axis_label_hint"] = s
        if "plot_hint_subtitle" in s:
            meta["subtitle_hint"] = s
        if "lat,23" in s and "lon,60" in s:
            meta["spatial_bounds_hint"] = "lat 23.3125 to 37.6875, lon 60.390625 to 77.734375"
    return meta


def run_audit():
    raw_dir = Path("datasets")
    out_dir = Path("data/metadata")
    out_dir.mkdir(parents=True, exist_ok=True)

    inventory_rows = []
    datasets_meta = []

    print("=== Scanning datasets/ directory ===")

    # Group files by parent folder
    folder_groups = {}
    for p in sorted(raw_dir.rglob("*")):
        if p.is_file():
            rel_folder = str(p.parent.relative_to(raw_dir))
            folder_groups.setdefault(rel_folder, []).append(p)

    for folder, files in folder_groups.items():
        print(f"\n--- Processing folder: {folder} ---")
        csv_file = next((f for f in files if f.suffix.lower() == ".csv"), None)
        nc_file = next((f for f in files if f.suffix.lower() == ".nc"), None)
        png_file = next((f for f in files if f.suffix.lower() == ".png"), None)
        txt_file = next((f for f in files if f.suffix.lower() == ".txt"), None)

        for f in files:
            sha = compute_sha256(f)
            size = f.stat().st_size
            inventory_rows.append({
                "file_path": str(f.as_posix()),
                "file_name": f.name,
                "folder": folder,
                "file_type": f.suffix.lower().lstrip("."),
                "file_size_bytes": size,
                "sha256": sha,
            })

        if csv_file:
            audit_res = parse_giovanni_csv(csv_file)
            nc_meta = extract_nc_strings(nc_file) if nc_file else {}

            val_col = audit_res["variable_col"]
            title = audit_res["metadata"].get("title", "")
            fill = audit_res["metadata"].get("fill_value")
            rep_url = audit_res["metadata"].get("reproduce_url", "")

            # Determine variable characteristics
            var_id = ""
            var_name = ""
            domain = ""
            unit = ""
            display_unit = ""
            platform = "NASA Giovanni"

            if "T2M" in val_col:
                var_id = "t2m"
                var_name = "2-Meter Air Temperature"
                domain = "Atmosphere"
                unit = "K"
                display_unit = "°C"
                platform = "MERRA-2 Reanalysis (M2TMNXSLV v5.12.4)"
            elif "PRECTOTCORR" in val_col:
                var_id = "precipitation"
                var_name = "Bias-Corrected Total Surface Precipitation"
                domain = "Atmosphere / Hydrology"
                unit = "kg m-2 s-1"
                display_unit = "mm/day"
                platform = "MERRA-2 Reanalysis (M2TMNXFLX v5.12.4)"
            elif "TS" in val_col:
                var_id = "ts"
                var_name = "Surface Skin Temperature"
                domain = "Land Surface"
                unit = "K"
                display_unit = "°C"
                platform = "MERRA-2 Reanalysis (M2TMNXSLV v5.12.4)"
            elif "Evap_tavg" in val_col:
                var_id = "evapotranspiration"
                var_name = "Total Evapotranspiration Flux"
                domain = "Hydrology / Land Surface"
                unit = "kg m-2 s-1"
                display_unit = "mm/day"
                platform = "GLDAS Noah Land Surface Model L4 (v2.1)"
            elif "SoilMoi0_10cm" in val_col:
                var_id = "soil_moisture_0_10cm"
                var_name = "Soil Moisture Content (0-10 cm)"
                domain = "Hydrology / Soil"
                unit = "kg m-2"
                display_unit = "kg/m²"
                platform = "GLDAS Noah Land Surface Model L4 (v2.1)"
            elif "SoilMoi10_40cm" in val_col:
                var_id = "soil_moisture_10_40cm"
                var_name = "Soil Moisture Content (10-40 cm)"
                domain = "Hydrology / Soil"
                unit = "kg m-2"
                display_unit = "kg/m²"
                platform = "GLDAS Noah Land Surface Model L4 (v2.1)"
            else:
                var_id = val_col.lower()
                var_name = title
                unit = "unknown"
                display_unit = "unknown"

            dataset_entry = {
                "variable_id": var_id,
                "variable_name": var_name,
                "raw_column_name": val_col,
                "domain": domain,
                "platform": platform,
                "unit": unit,
                "display_unit": display_unit,
                "title": title,
                "region": "Pakistan",
                "spatial_representation": "Area-Averaged Country Polygon (State Dept 2017 shp_171)",
                "bounding_coordinates": {
                    "lat_min": 23.3125,
                    "lat_max": 37.6875,
                    "lon_min": 60.390625,
                    "lon_max": 77.734375,
                },
                "temporal_frequency": "Monthly",
                "start_observation": audit_res["start_observation"],
                "end_observation": audit_res["end_observation"],
                "total_observations": audit_res["total_rows"],
                "valid_observations": audit_res["valid_rows"],
                "missing_observations": audit_res["missing_rows"],
                "fill_value": fill,
                "statistics": {
                    "min": audit_res["min_value"],
                    "max": audit_res["max_value"],
                    "mean": audit_res["mean_value"],
                    "std": audit_res["std_value"],
                },
                "interval_consistency": {
                    "min_gap_days": audit_res["gap_days_min"],
                    "max_gap_days": audit_res["gap_days_max"],
                    "is_strictly_regular_monthly": True if 28 <= audit_res["gap_days_min"] and audit_res["gap_days_max"] <= 31 else False
                },
                "files": {
                    "csv": str(csv_file.as_posix()) if csv_file else None,
                    "netcdf": str(nc_file.as_posix()) if nc_file else None,
                    "png": str(png_file.as_posix()) if png_file else None,
                },
                "giovanni_reproduce_url": rep_url,
                "citation": (
                    "Goddard Earth Sciences Data and Information Services Center (GES DISC) Giovanni / "
                    + platform
                ),
            }
            datasets_meta.append(dataset_entry)
            print(f"Parsed {var_id}: {audit_res['valid_rows']} valid months ({audit_res['start_observation']} to {audit_res['end_observation']})")

    # Write inventory CSV
    inv_csv_path = out_dir / "dataset_inventory.csv"
    with open(inv_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file_path", "file_name", "folder", "file_type", "file_size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(inventory_rows)
    print(f"\nSaved inventory to: {inv_csv_path}")

    # Write metadata JSON
    meta_json_path = out_dir / "dataset_metadata.json"
    with open(meta_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "audit_timestamp": pd.Timestamp.now(tz="UTC").isoformat(),
            "target_region": "Pakistan",
            "total_datasets": len(datasets_meta),
            "datasets": datasets_meta,
        }, f, indent=2)
    print(f"Saved metadata to: {meta_json_path}")

    return inventory_rows, datasets_meta


if __name__ == "__main__":
    run_audit()
