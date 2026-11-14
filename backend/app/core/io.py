"""Shared loaders for processed observations."""

from typing import Optional

import pandas as pd
from fastapi import HTTPException

from backend.app.core.catalog import SUPPORTED_VARIABLES
from backend.app.core.config import settings


def load_processed_frame(variable_id: str) -> pd.DataFrame:
    """Load canonical processed parquet/CSV for a supported variable."""
    if variable_id not in SUPPORTED_VARIABLES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown variable_id '{variable_id}'. Supported: {SUPPORTED_VARIABLES}",
        )

    file_path = settings.PROCESSED_DATA_DIR / f"{variable_id}.parquet"
    if not file_path.exists():
        file_path = settings.PROCESSED_DATA_DIR / f"{variable_id}.csv"
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Processed dataset for '{variable_id}' not found. Run the ingestion pipeline first.",
            )

    if file_path.suffix == ".parquet":
        df = pd.read_parquet(file_path)
    else:
        df = pd.read_csv(file_path)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp").reset_index(drop=True)


def downsample_frame(df: pd.DataFrame, max_points: Optional[int]) -> tuple[pd.DataFrame, bool, int]:
    """Evenly sample a monthly series, always retaining the first and last rows."""
    if max_points is None or max_points <= 0 or len(df) <= max_points:
        return df, False, 1

    n = len(df)
    stride = max(1, int(round((n - 1) / (max_points - 1))))
    indices = list(range(0, n, stride))
    if indices[-1] != n - 1:
        indices.append(n - 1)
    sampled = df.iloc[indices].reset_index(drop=True)
    return sampled, True, stride
