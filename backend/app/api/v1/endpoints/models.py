"""Saved forecasting model catalog and holdout metrics."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.app.core.catalog import MODEL_DISPLAY_NAMES, SUPPORTED_MODEL_IDS
from backend.app.core.config import settings
from backend.app.schemas.catalog import ModelCatalogResponse, ModelMetricsResponse, SavedModelSummary
from backend.app.schemas.forecast import ModelEvaluationMetrics
from backend.ml.training.persistence import ModelRegistry

router = APIRouter()
registry = ModelRegistry()

BASELINE_IDS = {"persistence", "seasonal_naive", "linear_drift"}


@router.get("/models", response_model=ModelCatalogResponse, tags=["Forecasting"])
async def list_models() -> ModelCatalogResponse:
    """List ladder models and which variables have persisted artifacts."""
    manifest = registry.load_manifest()
    variables = manifest.get("variables", {})
    saved_variables = sorted(variables.keys())

    models = []
    for model_id in SUPPORTED_MODEL_IDS:
        recommended_for = [
            var_id
            for var_id, meta in variables.items()
            if meta.get("recommended_model_id") == model_id
        ]
        models.append(
            SavedModelSummary(
                model_id=model_id,
                model_name=MODEL_DISPLAY_NAMES[model_id],
                is_baseline=model_id in BASELINE_IDS,
                variables=saved_variables,
                recommended_for=recommended_for,
            )
        )

    return ModelCatalogResponse(
        models=models,
        saved_variables=saved_variables,
        artifact_dir=str(settings.MODELS_DIR),
    )


@router.get("/models/{model_id}/metrics", response_model=ModelMetricsResponse, tags=["Forecasting"])
async def get_model_metrics(
    model_id: str,
    variable_id: Optional[str] = Query(None, description="Optional variable filter"),
) -> ModelMetricsResponse:
    """Return frozen chronological-holdout metrics for a saved model."""
    if model_id not in SUPPORTED_MODEL_IDS:
        raise HTTPException(status_code=404, detail=f"Unknown model_id '{model_id}'.")

    manifest = registry.load_manifest()
    variables = manifest.get("variables", {})
    if not variables:
        raise HTTPException(
            status_code=404,
            detail="No saved model artifacts. Run `python scripts/train_forecast_models.py`.",
        )

    if variable_id is not None and variable_id not in variables:
        raise HTTPException(status_code=404, detail=f"No saved artifact for variable '{variable_id}'.")

    selected = {variable_id: variables[variable_id]} if variable_id else variables
    metrics_by_variable = {}
    for var_id, meta in selected.items():
        holdout = meta.get("holdout_metrics", {}).get(model_id)
        if holdout is None:
            continue
        test_obs = int(meta.get("test_observations") or 0)
        metrics_by_variable[var_id] = ModelEvaluationMetrics(
            model_id=model_id,
            model_name=MODEL_DISPLAY_NAMES[model_id],
            mae=holdout["mae"],
            rmse=holdout["rmse"],
            r2_score=holdout.get("r2_score"),
            test_observations=test_obs,
            is_baseline=model_id in BASELINE_IDS,
        )

    if not metrics_by_variable:
        raise HTTPException(status_code=404, detail=f"No metrics stored for model '{model_id}'.")

    return ModelMetricsResponse(
        model_id=model_id,
        model_name=MODEL_DISPLAY_NAMES[model_id],
        is_baseline=model_id in BASELINE_IDS,
        metrics_by_variable=metrics_by_variable,
    )
