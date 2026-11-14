"""Canonical identifiers for variables, models, and the supported region."""

from typing import Dict, List

SUPPORTED_VARIABLES: List[str] = [
    "t2m",
    "ts",
    "precipitation",
    "evapotranspiration",
    "soil_moisture_0_10cm",
    "soil_moisture_10_40cm",
]

SUPPORTED_MODEL_IDS: List[str] = [
    "persistence",
    "seasonal_naive",
    "linear_drift",
    "ridge_lag",
    "random_forest",
]

MODEL_DISPLAY_NAMES: Dict[str, str] = {
    "persistence": "Lag-1 Persistence Baseline",
    "seasonal_naive": "12-Month Seasonal Naive Baseline",
    "linear_drift": "Linear Drift Baseline",
    "ridge_lag": "Regularized Lagged Ridge Regressor",
    "random_forest": "Random Forest Time-Series Regressor",
}

NON_NEGATIVE_VARIABLES = {
    "precipitation",
    "evapotranspiration",
    "soil_moisture_0_10cm",
    "soil_moisture_10_40cm",
}

PAKISTAN_REGION = {
    "id": "pakistan",
    "name": "Pakistan",
    "spatial_representation": "Area-averaged country polygon (State Dept 2017 shp_171)",
    "bounding_coordinates": {
        "lat_min": 23.3125,
        "lat_max": 37.6875,
        "lon_min": 60.390625,
        "lon_max": 77.734375,
    },
    "note": "All supplied Giovanni extracts are national area-averaged monthly series. Sub-national grids are not available.",
}

ECOLOGICAL_ZONES = [
    {
        "id": "northern_highlands",
        "name": "Northern Highlands & Glacial Basins",
        "description": "Glaciated alpine headwaters of the Indus River basin encompassing Karakoram, Himalayas, and Hindu Kush.",
        "climate_classification": "Alpine Tundra / Glacial (ET / EF)",
        "lat_center": 35.8,
        "lon_center": 74.8,
        "approx_elevation_m": "2,000 – 8,611 m",
        "vulnerability_profile": "Accelerated cryosphere retreat, glacial lake outburst floods (GLOFs), and snowline shifts.",
    },
    {
        "id": "upper_indus",
        "name": "Upper Indus Agricultural Plain",
        "description": "Alluvial agricultural heartland of Punjab with dense canal irrigation networks and high biomass productivity.",
        "climate_classification": "Semi-Arid Subtropical (BSh / Cwa)",
        "lat_center": 31.5,
        "lon_center": 73.2,
        "approx_elevation_m": "150 – 350 m",
        "vulnerability_profile": "Evaporative demand stress, intense pre-monsoon heatwaves, and seasonal aquifer overdraft.",
    },
    {
        "id": "lower_indus",
        "name": "Lower Indus Basin & Delta",
        "description": "Flat alluvial basin terminating in the Indus Delta and Arabian Sea coastal lagoons in Sindh.",
        "climate_classification": "Hyper-Arid Lowland (BWh)",
        "lat_center": 26.2,
        "lon_center": 68.6,
        "approx_elevation_m": "10 – 150 m",
        "vulnerability_profile": "Monsoon pluvial inundation (e.g. 2022 catastrophe), coastal saltwater intrusion, and soil waterlogging.",
    },
    {
        "id": "western_plateau",
        "name": "Western Arid Plateaus & Ranges",
        "description": "Rugged highland plateaus and desert basins across Balochistan and Sulaiman mountain ranges.",
        "climate_classification": "Cold / Hot Arid Desert (BWk / BWh)",
        "lat_center": 28.6,
        "lon_center": 65.4,
        "approx_elevation_m": "500 – 2,200 m",
        "vulnerability_profile": "Protracted meteorological droughts, depleted karez/groundwater reserves, and flash floods.",
    },
    {
        "id": "coastal_zone",
        "name": "Arabian Sea Coastal Belt",
        "description": "Marine-coastal littoral interface stretching 1,050 km along Makran and Sindh shorelines.",
        "climate_classification": "Coastal Semi-Arid / Marine (BSh)",
        "lat_center": 24.8,
        "lon_center": 66.8,
        "approx_elevation_m": "0 – 50 m",
        "vulnerability_profile": "Tropical cyclonic storm surges, extreme wet-bulb temperatures, and coastal sea-level rise.",
    },
]

NATIVE_GRID_RESOLUTIONS = {
    "MERRA-2 Atmospheric Reanalysis": "0.5° latitude × 0.625° longitude (~50 km × 60 km)",
    "GLDAS-2.1 Noah Land Surface Model": "0.25° latitude × 0.25° longitude (~25 km × 25 km)",
}

