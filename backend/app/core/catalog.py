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
