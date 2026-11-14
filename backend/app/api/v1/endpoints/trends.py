"""Trend detection analysis API endpoint."""

import pandas as pd
from fastapi import APIRouter, HTTPException
from backend.app.core.config import settings
from backend.app.schemas.trend import TrendRequest, TrendResponse
from backend.analytics.trend_detection.engine import TrendAnalysisEngine

router = APIRouter()
engine = TrendAnalysisEngine()


@router.post("/analysis/trend", response_model=TrendResponse, tags=["Analysis"])
async def run_trend_analysis(req: TrendRequest) -> TrendResponse:
    """Execute parametric or non-parametric statistical trend test on an environmental variable."""
    var_id = req.variable_id
    file_path = settings.PROCESSED_DATA_DIR / f"{var_id}.parquet"
    if not file_path.exists():
        file_path = settings.PROCESSED_DATA_DIR / f"{var_id}.csv"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Processed dataset for '{var_id}' not found.")

    if file_path.suffix == ".parquet":
        df = pd.read_parquet(file_path)
    else:
        df = pd.read_csv(file_path)

    try:
        res = engine.analyze_trend(
            df=df,
            var_id=var_id,
            method=req.method,
            deseasonalize=req.deseasonalize,
            alpha=req.alpha,
            start_date=req.start_date,
            end_date=req.end_date,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Trend analysis failed: {str(e)}")
