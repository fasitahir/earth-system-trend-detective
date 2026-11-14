"""API v1 master router."""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    anomalies,
    datasets,
    forecast,
    health,
    models,
    reports,
    timeseries,
    trends,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(datasets.router, prefix="", tags=["Datasets"])
api_router.include_router(timeseries.router, prefix="", tags=["Time Series"])
api_router.include_router(trends.router, prefix="", tags=["Analysis"])
api_router.include_router(anomalies.router, prefix="", tags=["Analysis"])
api_router.include_router(forecast.router, prefix="", tags=["Forecasting"])
api_router.include_router(models.router, prefix="", tags=["Forecasting"])
api_router.include_router(reports.router, prefix="", tags=["Reports"])
