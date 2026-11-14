"""Forecasting and forward projection API endpoint."""

import logging

from fastapi import APIRouter, HTTPException

from backend.app.core.cache import response_cache
from backend.app.core.catalog import SUPPORTED_MODEL_IDS
from backend.app.core.io import load_processed_frame
from backend.app.schemas.forecast import ForecastRequest, ForecastResponse
from backend.ml.inference.service import ForecastInferenceService

logger = logging.getLogger("earthscope.api.forecast")
router = APIRouter()
service = ForecastInferenceService()


@router.post("/forecast", response_model=ForecastResponse, tags=["Forecasting"])
async def run_forecast(req: ForecastRequest) -> ForecastResponse:
    """Generate forecasts from persisted production artifacts with holdout-calibrated intervals."""
    if req.model_id not in SUPPORTED_MODEL_IDS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model_id '{req.model_id}'. Supported: {SUPPORTED_MODEL_IDS}",
        )

    cache_key = response_cache.make_key(
        endpoint="forecast",
        variable_id=req.variable_id,
        horizon_months=req.horizon_months,
        model_id=req.model_id,
        confidence_level=req.confidence_level,
    )
    cached = response_cache.get(cache_key)
    if cached is not None:
        return cached

    df = load_processed_frame(req.variable_id)
    try:
        res = service.generate_forecast(
            df=df,
            var_id=req.variable_id,
            horizon_months=req.horizon_months,
            model_id=req.model_id,
            confidence_level=req.confidence_level,
        )
        logger.info(
            "forecast variable=%s model=%s horizon=%s artifact_loaded=%s",
            req.variable_id,
            req.model_id,
            req.horizon_months,
            res.artifact_loaded,
        )
        response_cache.set(cache_key, res)
        return res
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Forecasting failed: {exc}") from exc
