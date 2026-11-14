"""Time series query endpoints serving canonical processed data."""

from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from backend.app.core.cache import response_cache
from backend.app.core.io import downsample_frame, load_processed_frame
from backend.app.schemas.timeseries import ObservationPoint, TimeSeriesResponse, TimeSeriesSummary

router = APIRouter()


@router.get("/timeseries", response_model=TimeSeriesResponse, tags=["Time Series"])
async def get_timeseries(
    variable_id: str = Query(..., description="Variable identifier"),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    max_points: Optional[int] = Query(
        None,
        ge=12,
        le=2000,
        description="Optional downsample cap for chart payloads. Summary uses the filtered series before sampling.",
    ),
) -> TimeSeriesResponse:
    """Retrieve observation history, anomalies, and summary statistics."""
    cache_key = response_cache.make_key(
        endpoint="timeseries",
        variable_id=variable_id,
        start_date=start_date,
        end_date=end_date,
        max_points=max_points,
    )
    cached = response_cache.get(cache_key)
    if cached is not None:
        return cached

    df = load_processed_frame(variable_id)

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

    sampled, downsampled, stride = downsample_frame(df, max_points)

    data_points = [
        ObservationPoint(
            timestamp=row["timestamp"].strftime("%Y-%m-%d"),
            value=round(float(row["raw_value"]), 6),
            display_value=round(float(row["display_value"]), 4),
            anomaly=round(float(row["anomaly"]), 4) if pd.notna(row["anomaly"]) else None,
        )
        for _, row in sampled.iterrows()
    ]

    first_row = df.iloc[0]
    response = TimeSeriesResponse(
        variable_id=variable_id,
        variable_name=variable_id.replace("_", " ").title(),
        unit=str(first_row["source_unit"]),
        display_unit=str(first_row["display_unit"]),
        region=str(first_row["region"]),
        start_date=df["timestamp"].min().strftime("%Y-%m-%d"),
        end_date=df["timestamp"].max().strftime("%Y-%m-%d"),
        summary=summary,
        data=data_points,
        downsampled=downsampled,
        stride=stride,
    )
    response_cache.set(cache_key, response)
    return response
