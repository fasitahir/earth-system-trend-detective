"""Catalog schemas for variables, regions, saved models, anomalies, and reports."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.schemas.dataset import VariableMeta
from backend.app.schemas.forecast import ModelEvaluationMetrics


class BoundingBox(BaseModel):
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float


class RegionMeta(BaseModel):
    id: str
    name: str
    spatial_representation: str
    bounding_coordinates: BoundingBox
    note: str
    variable_ids: List[str] = Field(default_factory=list)


class RegionListResponse(BaseModel):
    regions: List[RegionMeta]
    total_regions: int


class VariableListResponse(BaseModel):
    variables: List[VariableMeta]
    total_variables: int


class SavedModelSummary(BaseModel):
    model_id: str
    model_name: str
    is_baseline: bool
    variables: List[str]
    recommended_for: List[str] = Field(default_factory=list)


class ModelCatalogResponse(BaseModel):
    models: List[SavedModelSummary]
    saved_variables: List[str]
    artifact_dir: str


class ModelMetricsResponse(BaseModel):
    model_id: str
    model_name: str
    is_baseline: bool
    metrics_by_variable: Dict[str, ModelEvaluationMetrics]


class AnomalyRecord(BaseModel):
    timestamp: str
    value: float
    anomaly: float
    z_score: Optional[float] = None


class AnomalyRequest(BaseModel):
    variable_id: str
    top_n: int = Field(5, ge=1, le=25)
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class AnomalyResponse(BaseModel):
    variable_id: str
    unit: str
    display_unit: str
    region: str
    top_positive_anomalies: List[AnomalyRecord]
    top_negative_anomalies: List[AnomalyRecord]
    method: str = "standardized monthly anomaly vs 2001–2025 climatology"


class ReportSummary(BaseModel):
    report_id: str
    title: str
    path: str
    description: str


class ReportListResponse(BaseModel):
    reports: List[ReportSummary]


class ReportDetailResponse(BaseModel):
    report_id: str
    title: str
    path: str
    description: str
    excerpt: str
