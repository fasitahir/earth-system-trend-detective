"""Datasets, variables, and region discovery endpoints."""

import json
from typing import List

from fastapi import APIRouter, HTTPException

from backend.app.core.cache import response_cache
from backend.app.core.catalog import PAKISTAN_REGION, SUPPORTED_VARIABLES
from backend.app.core.config import settings
from backend.app.schemas.catalog import RegionListResponse, RegionMeta, VariableListResponse
from backend.app.schemas.dataset import DatasetListResponse, DatasetMeta, VariableMeta

router = APIRouter()


def load_variable_entries() -> List[dict]:
    meta_path = settings.METADATA_DIR / "dataset_metadata.json"
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Dataset metadata catalog not found. Run pipeline first.")
    with open(meta_path, "r", encoding="utf-8") as handle:
        catalog = json.load(handle)
    return catalog.get("datasets", [])


def to_variable_meta(entry: dict) -> VariableMeta:
    return VariableMeta(
        id=entry["variable_id"],
        name=entry["variable_name"],
        source_variable_name=entry["raw_column_name"],
        category=entry["domain"],
        unit=entry["unit"],
        display_unit=entry["display_unit"],
        mission_source=entry["platform"],
        description=entry["title"],
        frequency=entry["temporal_frequency"].lower(),
        start_date=entry["start_observation"],
        end_date=entry["end_observation"],
        total_months=entry["valid_observations"],
        region=entry["region"],
    )


@router.get("/datasets", response_model=DatasetListResponse, tags=["Datasets"])
async def list_datasets() -> DatasetListResponse:
    """Return catalog of all supported NASA Earth-system datasets and variables."""
    cache_key = response_cache.make_key(endpoint="datasets")
    cached = response_cache.get(cache_key)
    if cached is not None:
        return cached

    entries = load_variable_entries()
    grouped_datasets = {}
    for entry in entries:
        plat = entry["platform"]
        var_meta = to_variable_meta(entry)
        if plat not in grouped_datasets:
            grouped_datasets[plat] = DatasetMeta(
                id=plat.split()[0].lower(),
                title=f"{plat} Earth Observations",
                platform=plat,
                spatial_resolution="0.5°x0.625° or 1.0°",
                temporal_resolution="Monthly",
                variables=[],
                citation=entry["citation"],
                giovanni_url=entry.get("giovanni_reproduce_url"),
            )
        grouped_datasets[plat].variables.append(var_meta)

    response = DatasetListResponse(
        datasets=list(grouped_datasets.values()),
        total_variables=len(entries),
    )
    response_cache.set(cache_key, response)
    return response


@router.get("/variables", response_model=VariableListResponse, tags=["Datasets"])
async def list_variables() -> VariableListResponse:
    """Flattened variable catalog used by dashboard selectors."""
    entries = load_variable_entries()
    variables = [to_variable_meta(entry) for entry in entries]
    return VariableListResponse(variables=variables, total_variables=len(variables))


@router.get("/regions", response_model=RegionListResponse, tags=["Datasets"])
async def list_regions() -> RegionListResponse:
    """Return supported geographic scopes. Currently Pakistan area-averaged series only."""
    region = RegionMeta(
        id=PAKISTAN_REGION["id"],
        name=PAKISTAN_REGION["name"],
        spatial_representation=PAKISTAN_REGION["spatial_representation"],
        bounding_coordinates=PAKISTAN_REGION["bounding_coordinates"],
        note=PAKISTAN_REGION["note"],
        variable_ids=list(SUPPORTED_VARIABLES),
    )
    return RegionListResponse(regions=[region], total_regions=1)
