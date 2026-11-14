"""Time series query endpoints serving canonical processed data."""

from pathlib import Path
from typing import Optional
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.timeseries import TimeSeriesResponse, TimeSeriesSummary, ObservationPoint
from backend.app.core.config import settings

router = APIRouter()


@router.get("/timeseries", response_model=TimeSeriesResponse, tags=["Time Series"])
async def get_timeseries(
    variable_id: str = Query(..., description="Variable identifier: t2m | ts | precipitation | evapotranspiration | soil_moisture_0_10cm | soil_moisture_10_40cm"),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
) -> TimeSeriesResponse:
    """Retrieve full or filtered observation history, anomalies, and summary statistics."""
    file_path = settings.PROCESSED_DATA_DIR / f"{variable_id}.parquet"
    if not file_path.exists():
        # Fallback to CSV if parquet not found
        file_path = settings.PROCESSED_DATA_DIR / f"{variable_id}.csv"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Processed dataset for '{variable_id}' not found.")

    if file_path.suffix == ".parquet":
        df = pd.read_parquet(file_path)
    else:
        df = pd.read_csv(file_path)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    if start_date:
        df = df[df["timestamp"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["timestamp"] <= pd.to_datetime(end_date)]

    if df.empty:
        raise HTTPException(status_code=400, detail="No observations match the specified date range.")

    df = df.sort_values("timestamp").reset_index(drop=True)

    summary = TimeSeriesSummary(
        count=int(df["display_value"].count()),
        mean=round(float(df["display_value"].mean()), 4),
        std=round(float(df["display_value"].std()), 4),
        min=round(float(df["display_value"].min()), 4),
        max=round(float(df["display_value"].max()), 4),
        median=round(float(df["display_value"].median()), 4),
    )

    data_points = [
        ObservationPoint(
            timestamp=row["timestamp"].strftime("%Y-%m-%d"),
            value=round(float(row["raw_value"]), 6),
            display_value=round(float(row["display_value"]), 4),
            anomaly=round(float(row["anomaly"]), 4) if pd.notna(row["anomaly"]) else None,
        )
        for _, row in df.iterrows()
    ]

    first_row = df.iloc[0]
    return TimeSeriesResponse(
        variable_id=variable_id,
        variable_name=variable_id.replace("_", " ").title(),
        unit=str(first_row["source_unit"]),
        display_unit=str(first_row["display_unit"]),
        region=str(first_row["region"]),
        start_date=df["timestamp"].min().strftime("%Y-%m-%d"),
        end_date=df["timestamp"].max().strftime("%Y-%m-%d"),
        summary=summary,
        data=data_points,
    )
