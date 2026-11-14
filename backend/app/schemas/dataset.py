"""Dataset and variable metadata schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class VariableMeta(BaseModel):
    """Metadata schema for a scientific environmental variable."""
    id: str = Field(..., description="Unique variable identifier")
    name: str = Field(..., description="Human-readable variable name")
    source_variable_name: str = Field(..., description="Raw variable identifier in Giovanni/source dataset")
    category: str = Field(..., description="Earth system domain (e.g., Atmosphere, Hydrosphere, Biosphere)")
    unit: str = Field(..., description="Physical measurement unit (e.g., K, kg m-2 s-1, kg m-2)")
    display_unit: str = Field(..., description="User-friendly display unit (e.g., °C, mm/month)")
    mission_source: str = Field(..., description="Data source mission or model (e.g., MERRA-2, GLDAS-2.1)")
    description: str = Field(..., description="Detailed description of physical variable")
    frequency: str = Field("monthly", description="Temporal sampling frequency")
    start_date: str = Field(..., description="Start date of dataset (ISO format YYYY-MM-DD)")
    end_date: str = Field(..., description="End date of dataset (ISO format YYYY-MM-DD)")
    total_months: int = Field(..., description="Total observation count in months")
    region: str = Field("Pakistan", description="Geographic area of observations")


class DatasetMeta(BaseModel):
    """Metadata schema for a source dataset product."""
    id: str = Field(..., description="Dataset product identifier")
    title: str = Field(..., description="Dataset title")
    platform: str = Field(..., description="Platform / Earth science model")
    spatial_resolution: str = Field(..., description="Spatial resolution (e.g., 0.5 x 0.625 deg, 1 deg)")
    temporal_resolution: str = Field(..., description="Temporal resolution (e.g., Monthly)")
    variables: List[VariableMeta] = Field(default_factory=list, description="Variables included in this dataset")
    citation: str = Field(..., description="Official data citation and source attribution")
    giovanni_url: Optional[str] = Field(None, description="NASA Giovanni reproduction URL")


class DatasetListResponse(BaseModel):
    """Response schema listing all available datasets and variables."""
    datasets: List[DatasetMeta] = Field(default_factory=list)
    total_variables: int = Field(..., description="Total available environmental variables")
