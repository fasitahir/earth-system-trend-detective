"""Geographic intelligence and spatial summary endpoint."""

import json
from typing import List

from fastapi import APIRouter, HTTPException

from backend.app.core.cache import response_cache
from backend.app.core.catalog import (
    ECOLOGICAL_ZONES,
    NATIVE_GRID_RESOLUTIONS,
    PAKISTAN_REGION,
)
from backend.app.core.config import settings
from backend.app.schemas.catalog import (
    BoundingBox,
    EcologicalZone,
    SpatialSummaryResponse,
    SpatialTrendLayer,
)

router = APIRouter()


def compute_fdr_adjusted_trends() -> List[SpatialTrendLayer]:
    """Compute Benjamini-Hochberg FDR multiple testing corrections across all variables."""
    results_path = settings.METADATA_DIR / "trend_analysis_results.json"
    if not results_path.exists():
        raise HTTPException(status_code=404, detail="Trend analysis metadata not found.")

    with open(results_path, "r", encoding="utf-8") as handle:
        trends_raw = json.load(handle)

    # Extract p-values for deseasonalized MK test
    parsed_items = []
    for item in trends_raw:
        var_id = item["variable_id"]
        var_title = item.get("variable_title", var_id)
        unit = item.get("rate_unit", "")
        deseas = item.get("deseasonalized_mk", {})
        sen_slope = deseas.get("sen_slope_per_decade", 0.0)
        p_val = deseas.get("p_value", 1.0)
        direction = deseas.get("direction", "no_detected_trend")

        parsed_items.append({
            "var_id": var_id,
            "title": var_title,
            "unit": unit,
            "sen_slope": sen_slope,
            "p_val": p_val,
            "direction": direction,
        })

    # Benjamini-Hochberg Procedure:
    # 1. Sort by ascending p-value
    # 2. Adjusted p-val = p * (m / rank)
    m = len(parsed_items)
    sorted_items = sorted(parsed_items, key=lambda x: x["p_val"])

    layers: List[SpatialTrendLayer] = []
    for rank, it in enumerate(sorted_items, start=1):
        raw_p = it["p_val"]
        # BH adjustment
        adjusted_p = min(1.0, raw_p * (m / rank))
        is_sig = adjusted_p < 0.05

        layers.append(
            SpatialTrendLayer(
                variable_id=it["var_id"],
                variable_name=it["title"],
                display_unit=it["unit"],
                sen_slope_per_decade=it["sen_slope"],
                p_value=raw_p,
                is_significant=is_sig,
                fdr_adjusted_p_value=round(adjusted_p, 6),
                trend_direction=it["direction"],
                spatial_scope="Pakistan National Area-Average (shp_171)",
            )
        )

    # Sort back by variable_id for predictable ordering
    layers.sort(key=lambda x: x.variable_id)
    return layers


@router.get("/spatial/summary", response_model=SpatialSummaryResponse, tags=["Geographic Intelligence"])
async def get_spatial_summary() -> SpatialSummaryResponse:
    """Return geospatial boundary, coordinates, ecological zones, and FDR-corrected trends."""
    cache_key = response_cache.make_key(endpoint="spatial_summary")
    cached = response_cache.get(cache_key)
    if cached is not None:
        return cached

    bbox = BoundingBox(
        lat_min=PAKISTAN_REGION["bounding_coordinates"]["lat_min"],
        lat_max=PAKISTAN_REGION["bounding_coordinates"]["lat_max"],
        lon_min=PAKISTAN_REGION["bounding_coordinates"]["lon_min"],
        lon_max=PAKISTAN_REGION["bounding_coordinates"]["lon_max"],
    )

    zones = [EcologicalZone(**z) for z in ECOLOGICAL_ZONES]
    trend_layers = compute_fdr_adjusted_trends()

    response = SpatialSummaryResponse(
        region_id=PAKISTAN_REGION["id"],
        region_name=PAKISTAN_REGION["name"],
        projection="EPSG:4326 (WGS 84)",
        spatial_representation=PAKISTAN_REGION["spatial_representation"],
        bounding_box=bbox,
        polygon_id="state_dept_countries_2017/shp_171",
        native_grid_resolutions=NATIVE_GRID_RESOLUTIONS,
        zones=zones,
        variable_trends=trend_layers,
        multiple_testing_correction="Benjamini-Hochberg False Discovery Rate (FDR) at alpha = 0.05 across all 6 Earth system variables",
        limitations=[
            "Supplied NASA Giovanni extracts are pre-computed area-averaged series over Pakistan country boundary (shp_171).",
            "Spatial variation is described via ecological zones; artificial pixel interpolation is strictly excluded to preserve observational integrity.",
            "MERRA-2 reanalysis (0.5°x0.625°) and GLDAS-2.1 (0.25°x0.25°) spatial resolutions are documented without synthetic downscaling.",
        ],
    )

    response_cache.set(cache_key, response)
    return response
