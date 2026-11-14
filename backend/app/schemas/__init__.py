"""Pydantic schemas package."""

from backend.app.schemas.health import HealthResponse
from backend.app.schemas.dataset import VariableMeta, DatasetMeta, DatasetListResponse
from backend.app.schemas.timeseries import ObservationPoint, TimeSeriesSummary, TimeSeriesResponse
from backend.app.schemas.trend import TrendRequest, TrendResponse, ConfidenceInterval
from backend.app.schemas.forecast import ForecastRequest, ForecastResponse, ForecastPoint, ModelEvaluationMetrics
from backend.app.schemas.error import ErrorResponse, ErrorDetail
from backend.app.schemas.catalog import (
    VariableListResponse,
    RegionListResponse,
    ModelCatalogResponse,
    ModelMetricsResponse,
    AnomalyRequest,
    AnomalyResponse,
    ReportListResponse,
)

__all__ = [
    "HealthResponse",
    "VariableMeta",
    "DatasetMeta",
    "DatasetListResponse",
    "ObservationPoint",
    "TimeSeriesSummary",
    "TimeSeriesResponse",
    "TrendRequest",
    "TrendResponse",
    "ConfidenceInterval",
    "ForecastRequest",
    "ForecastResponse",
    "ForecastPoint",
    "ModelEvaluationMetrics",
    "ErrorResponse",
    "ErrorDetail",
    "VariableListResponse",
    "RegionListResponse",
    "ModelCatalogResponse",
    "ModelMetricsResponse",
    "AnomalyRequest",
    "AnomalyResponse",
    "ReportListResponse",
]
