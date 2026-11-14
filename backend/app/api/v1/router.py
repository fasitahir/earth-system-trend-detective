"""API v1 master router."""

from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, datasets, timeseries, trends

api_router = APIRouter()
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(datasets.router, prefix="", tags=["Datasets"])
api_router.include_router(timeseries.router, prefix="", tags=["Time Series"])
api_router.include_router(trends.router, prefix="", tags=["Analysis"])
