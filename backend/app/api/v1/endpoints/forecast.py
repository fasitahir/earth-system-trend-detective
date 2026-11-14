"""Forecasting and forward projection API endpoint."""

import pandas as pd
from fastapi import APIRouter, HTTPException
from backend.app.core.config import settings
from backend.app.schemas.forecast import ForecastRequest, ForecastResponse
from backend.ml.inference.service import ForecastInferenceService

router = APIRouter()
service = ForecastInferenceService()


@router.post("/forecast", response_model=ForecastResponse, tags=["Forecasting"])
async def run_forecast(req: ForecastRequest) -> ForecastResponse:
    """Generate out-of-sample evaluated forecasts with prediction uncertainty intervals."""
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
        res = service.generate_forecast(
            df=df,
            var_id=var_id,
            horizon_months=req.horizon_months,
            model_id=req.model_id,
            confidence_level=req.confidence_level,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Forecasting failed: {str(e)}")
