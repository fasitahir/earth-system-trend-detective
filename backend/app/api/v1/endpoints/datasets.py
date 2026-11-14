"""Datasets and variables discovery endpoints."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.app.schemas.dataset import DatasetListResponse, DatasetMeta, VariableMeta
from backend.app.core.config import settings

router = APIRouter()


@router.get("/datasets", response_model=DatasetListResponse, tags=["Datasets"])
async def list_datasets() -> DatasetListResponse:
    """Return catalog of all supported NASA Earth-system datasets and variables."""
    meta_path = settings.METADATA_DIR / "dataset_metadata.json"
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Dataset metadata catalog not found. Run pipeline first.")

    with open(meta_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    # Group variables into datasets
    grouped_datasets = {}
    for entry in catalog.get("datasets", []):
        plat = entry["platform"]
        var_meta = VariableMeta(
            id=entry["variable_id"],
            name=entry["variable_name"],
            source_variable_name=entry["raw_column_name"],
            category=entry["domain"],
            unit=entry["unit"],
            display_unit=entry["display_unit"],
            mission_source=plat,
            description=entry["title"],
            frequency=entry["temporal_frequency"].lower(),
            start_date=entry["start_observation"],
            end_date=entry["end_observation"],
            total_months=entry["valid_observations"],
            region=entry["region"]
        )

        if plat not in grouped_datasets:
            grouped_datasets[plat] = DatasetMeta(
                id=plat.split()[0].lower(),
                title=f"{plat} Earth Observations",
                platform=plat,
                spatial_resolution="0.5°x0.625° or 1.0°",
                temporal_resolution="Monthly",
                variables=[],
                citation=entry["citation"],
                giovanni_url=entry.get("giovanni_reproduce_url")
            )
        grouped_datasets[plat].variables.append(var_meta)

    return DatasetListResponse(
        datasets=list(grouped_datasets.values()),
        total_variables=catalog.get("total_datasets", 0)
    )
