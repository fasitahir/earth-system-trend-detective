"""Read-only scientific report catalog (paths into docs/, not generated PDFs)."""

from fastapi import APIRouter, HTTPException

from backend.app.core.config import settings
from backend.app.schemas.catalog import ReportDetailResponse, ReportListResponse, ReportSummary

router = APIRouter()

REPORTS = {
    "data-quality": {
        "title": "Data Quality Report",
        "path": "docs/data-quality-report.md",
        "description": "Inventory, completeness, units, and provenance of supplied Giovanni extracts.",
    },
    "eda-findings": {
        "title": "Exploratory Data Analysis Findings",
        "path": "docs/eda-findings.md",
        "description": "Climatology, coupling, and extreme-anomaly diagnostics.",
    },
    "statistical-methodology": {
        "title": "Statistical Trend Methodology",
        "path": "docs/statistical-methodology.md",
        "description": "Mann-Kendall, Sen slope, Yue-Pilon prewhitening, and linear trend assumptions.",
    },
    "forecasting-methodology": {
        "title": "Forecasting Methodology",
        "path": "docs/forecasting-methodology.md",
        "description": "Model ladder, chronological holdout, prediction intervals, and limitations.",
    },
}


@router.get("/reports", response_model=ReportListResponse, tags=["Reports"])
async def list_reports() -> ReportListResponse:
    reports = [
        ReportSummary(report_id=report_id, **meta)
        for report_id, meta in REPORTS.items()
    ]
    return ReportListResponse(reports=reports)


@router.get("/reports/{report_id}", response_model=ReportDetailResponse, tags=["Reports"])
async def get_report(report_id: str) -> ReportDetailResponse:
    meta = REPORTS.get(report_id)
    if meta is None:
        raise HTTPException(status_code=404, detail=f"Unknown report_id '{report_id}'.")
    path = settings.BASE_DIR / meta["path"]
    excerpt = ""
    if path.exists():
        text = path.read_text(encoding="utf-8")
        excerpt = "\n".join(text.strip().splitlines()[:12])
    return ReportDetailResponse(
        report_id=report_id,
        title=meta["title"],
        path=meta["path"],
        description=meta["description"],
        excerpt=excerpt,
    )
