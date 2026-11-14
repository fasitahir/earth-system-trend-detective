"""Standard error schemas."""

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error object."""
    field: Optional[str] = Field(None, description="Request field that caused the error")
    message: str = Field(..., description="Actionable explanation of error")


class ErrorResponse(BaseModel):
    """Standard API error response schema."""
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error summary")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed validation or execution errors")
