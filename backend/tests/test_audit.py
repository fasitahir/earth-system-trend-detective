"""Automated tests validating dataset inventory and metadata integrity."""

import csv
import json
from pathlib import Path


def test_dataset_inventory_file_exists_and_valid():
    """Verify data/metadata/dataset_inventory.csv exists and has all 19 files."""
    inv_path = Path("data/metadata/dataset_inventory.csv")
    assert inv_path.exists(), "dataset_inventory.csv must exist"

    with open(inv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) >= 19, f"Expected at least 19 files in inventory, found {len(reader)}"

    for row in reader:
        assert row["file_name"]
        assert int(row["file_size_bytes"]) > 0
        assert len(row["sha256"]) == 64, f"Invalid SHA-256 for {row['file_name']}"


def test_dataset_metadata_json_structure():
    """Verify data/metadata/dataset_metadata.json conforms to EarthScope schema."""
    meta_path = Path("data/metadata/dataset_metadata.json")
    assert meta_path.exists(), "dataset_metadata.json must exist"

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["target_region"] == "Pakistan"
    assert meta["total_datasets"] == 6
    assert len(meta["datasets"]) == 6

    var_ids = {d["variable_id"] for d in meta["datasets"]}
    expected_vars = {
        "t2m",
        "precipitation",
        "soil_moisture_0_10cm",
        "soil_moisture_10_40cm",
        "ts",
        "evapotranspiration",
    }
    assert var_ids == expected_vars

    for d in meta["datasets"]:
        assert d["total_observations"] in (297, 300)
        assert d["missing_observations"] == 0
        assert d["interval_consistency"]["is_strictly_regular_monthly"] is True
        assert d["statistics"]["min"] is not None
        assert d["statistics"]["max"] is not None
