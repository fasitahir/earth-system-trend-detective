"""Trend detection analysis API endpoint."""

import logging

from fastapi import APIRouter, HTTPException

from backend.analytics.trend_detection.engine import TrendAnalysisEngine
from backend.app.core.cache import response_cache
from backend.app.core.io import load_processed_frame
from backend.app.schemas.trend import TrendRequest, TrendResponse

logger = logging.getLogger("earthscope.api.trends")
router = APIRouter()
engine = TrendAnalysisEngine()


@router.post("/analysis/trend", response_model=TrendResponse, tags=["Analysis"])
async def run_trend_analysis(req: TrendRequest) -> TrendResponse:
    """Execute parametric or non-parametric statistical trend test on an environmental variable."""
    cache_key = response_cache.make_key(
        endpoint="trend",
        variable_id=req.variable_id,
        method=req.method,
        deseasonalize=req.deseasonalize,
        alpha=req.alpha,
        start_date=req.start_date,
        end_date=req.end_date,
    )
    cached = response_cache.get(cache_key)
    if cached is not None:
        return cached

    df = load_processed_frame(req.variable_id)
    try:
        res = engine.analyze_trend(
            df=df,
            var_id=req.variable_id,
            method=req.method,
            deseasonalize=req.deseasonalize,
            alpha=req.alpha,
            start_date=req.start_date,
            end_date=req.end_date,
        )
        logger.info("trend variable=%s method=%s significant=%s", req.variable_id, req.method, res.is_statistically_significant)
        response_cache.set(cache_key, res)
        return res
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Trend analysis failed: {exc}") from exc
