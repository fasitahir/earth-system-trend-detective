"""Extreme-anomaly forensic endpoint."""

import pandas as pd
from fastapi import APIRouter, HTTPException

from backend.analytics.eda.analyzer import detect_top_extreme_anomalies
from backend.app.core.cache import response_cache
from backend.app.core.io import load_processed_frame
from backend.app.schemas.catalog import AnomalyRecord, AnomalyRequest, AnomalyResponse

router = APIRouter()


@router.post("/analysis/anomalies", response_model=AnomalyResponse, tags=["Analysis"])
async def run_anomaly_analysis(req: AnomalyRequest) -> AnomalyResponse:
    """Return the largest positive and negative climatology anomalies for a variable."""
    cache_key = response_cache.make_key(
        endpoint="anomalies",
        variable_id=req.variable_id,
        top_n=req.top_n,
        start_date=req.start_date,
        end_date=req.end_date,
    )
    cached = response_cache.get(cache_key)
    if cached is not None:
        return cached

    df = load_processed_frame(req.variable_id)
    if req.start_date:
        df = df[df["timestamp"] >= pd.to_datetime(req.start_date)]
    if req.end_date:
        df = df[df["timestamp"] <= pd.to_datetime(req.end_date)]
    if df.empty:
        raise HTTPException(status_code=400, detail="No observations match the specified date range.")

    payload = detect_top_extreme_anomalies(df, var_id=req.variable_id, top_n=req.top_n)
    first_row = df.iloc[0]

    def to_records(rows) -> list[AnomalyRecord]:
        records = []
        for row in rows:
            records.append(
                AnomalyRecord(
                    timestamp=str(row["timestamp"])[:10],
                    value=round(float(row["value"]), 4),
                    anomaly=round(float(row["anomaly"]), 4),
                    z_score=round(float(row["z_score"]), 4) if row.get("z_score") is not None else None,
                )
            )
        return records

    response = AnomalyResponse(
        variable_id=req.variable_id,
        unit=str(first_row.get("source_unit", "")),
        display_unit=str(first_row.get("display_unit", "")),
        region=str(first_row.get("region", "Pakistan")),
        top_positive_anomalies=to_records(payload["top_positive_anomalies"]),
        top_negative_anomalies=to_records(payload["top_negative_anomalies"]),
    )
    response_cache.set(cache_key, response)
    return response
