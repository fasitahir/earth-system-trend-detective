# EarthScope Project Status

**Challenge:** NASA Space Apps Challenge 2026 — "Be an Earth System Trend Detective!"  
**Project:** EarthScope (Earth System Trend Intelligence)  
**Last Updated:** 2026-11-14  

---

## 1. Executive Summary

EarthScope is an interactive scientific platform for investigating historical Earth-system observations, quantifying monotonic and seasonal trends with rigorous statistical tests (Mann-Kendall, Sen's slope), and producing honest out-of-sample forecasts.

The project operates under a stage-gated autonomous engineering protocol:
- **Stage 0 (Project Initialization & Architecture):** `COMPLETE`
- **Stage 1 (Dataset Discovery & Audit):** `COMPLETE`
- **Stage 2 (Data Ingestion & Preprocessing):** `COMPLETE`
- **Stage 3 (Exploratory Data Analysis):** `COMPLETE`
- **Stage 4 (Statistical Trend Detection):** `COMPLETE`
- **Stage 5 (Forecasting & Machine Learning):** `COMPLETE`

---

## 2. Stage Progress Overview

| Stage | Name | Status | Owner | Gate Passed |
|---|---|---|---|---|
| **Stage 0** | Project Initialization & Architecture | **COMPLETE** | Architect / Integrator | Yes |
| **Stage 1** | Dataset Discovery & Audit | **COMPLETE** | Data Engineer | Yes |
| **Stage 2** | Data Ingestion & Preprocessing | **COMPLETE** | Data Engineer | Yes |
| **Stage 3** | Exploratory Data Analysis | **COMPLETE** | Data Scientist | Yes |
| **Stage 4** | Statistical Trend Detection | **COMPLETE** | Statistical Analyst | Yes |
| **Stage 5** | Forecasting & Machine Learning | **COMPLETE** | ML Engineer | Yes |
| **Stage 6** | Backend API Services | **IN PROGRESS** | Backend Engineer | Partial (Core Endpoints Live) |
| **Stage 7** | Frontend Dashboard | **NOT STARTED** | Frontend Engineer | Pending |
| **Stage 8** | Geographic Intelligence | **NOT STARTED** | Data Engineer / GIS | Pending |
| **Stage 9** | End-to-End Integration | **NOT STARTED** | Architect / Integrator | Pending |
| **Stage 10** | Testing & Scientific Validation | **NOT STARTED** | QA / Scientific Validator | Pending |
| **Stage 11** | Competition Presentation & Release | **NOT STARTED** | Lead Author / Presenter | Pending |

---

## 3. Detailed Stage Reports

### Stage 0 — Project Initialization and Architecture
- **Status:** `COMPLETE`
- **Acceptance Criteria:** All passed.

### Stage 1 — Dataset Discovery and Audit
- **Status:** `COMPLETE`
- **Acceptance Criteria:** All passed.

### Stage 2 — Data Ingestion and Preprocessing
- **Status:** `COMPLETE`
- **Acceptance Criteria:** All passed.

### Stage 3 — Exploratory Data Analysis (EDA)
- **Status:** `COMPLETE`
- **Acceptance Criteria:** All passed.

### Stage 4 — Statistical Trend Detection
- **Status:** `COMPLETE`
- **Acceptance Criteria:** All passed.

### Stage 5 — Forecasting & Machine Learning
- **Status:** `COMPLETE`
- **Owner / Agent Role:** ML Engineer
- **Prerequisites:** Stages 1–4 complete.
- **Implementation Summary:**
  - Designed strict chronological holdout evaluation protocol (2001–2022 train, 2023–2025 holdout test, 0 temporal data leakage).
  - Built leakage-free feature extractor (`backend/ml/features/pipeline.py`):
    - Lags 1, 2, 3, 12, 24
    - Rolling 3-month and 12-month mean & standard deviation (shifted by 1)
    - Harmonic Fourier seasonal terms ($\sin, \cos$ at annual and semi-annual frequencies)
    - Linear time trend
  - Built comprehensive model ladder (`backend/ml/training/models.py`):
    - Baseline 1: Lag-1 Persistence
    - Baseline 2: 12-Month Seasonal Naive
    - Baseline 3: Linear Drift Baseline
    - Candidate 1: Regularized Lagged Ridge Regressor (L2 + Feature Scaling)
    - Candidate 2: Random Forest Time-Series Regressor
  - Implemented chronological holdout validator (`backend/ml/evaluation/validator.py`) reporting MAE, RMSE, $R^2$, and Skill Score vs Seasonal Naive.
  - Implemented forward projection inference service (`backend/ml/inference/service.py`) generating point predictions and calibrated $95\%$ prediction intervals ($\sigma_h = \text{RMSE} \cdot \sqrt{1 + h/12}$).
  - Exposed REST endpoint: `POST /api/v1/forecast` matching `ForecastResponse` schema.
  - Created execution script (`scripts/train_forecast_models.py`) saving:
    - `data/metadata/model_evaluation_metrics.json`
    - `docs/figures/forecast_holdout_comparison.png`
    - `docs/figures/forecast_forward_24m.png`
  - Authored comprehensive documentation: `docs/forecasting-methodology.md`.
  - Added automated test suite: `backend/tests/test_forecast.py`.
- **Key Empirical Results (Holdout 2023–2025):**
  - **2m Air Temp (`t2m`):** Ridge MAE $1.32^\circ\text{C}$, RMSE $1.57^\circ\text{C}$, $R^2 = 0.95$ (**+29.04% skill score gain** over Seasonal Naive).
  - **Surface Skin Temp (`ts`):** Ridge MAE $1.41^\circ\text{C}$, RMSE $1.64^\circ\text{C}$, $R^2 = 0.96$ (**+36.24% skill score gain**).
  - **Total Precipitation:** Ridge MAE $23.90\text{ mm/mo}$, RMSE $32.65\text{ mm/mo}$, $R^2 = 0.28$ (**+54.45% skill score gain** over Seasonal Naive's $71.67\text{ mm/mo}$ error).
  - **Total Evapotranspiration:** Random Forest MAE $5.55\text{ mm/mo}$, RMSE $7.31\text{ mm/mo}$, $R^2 = 0.84$ (**+43.02% skill score gain**).
  - **Topsoil Moisture (0–10cm):** Ridge MAE $1.83\text{ kg/m²}$, RMSE $2.18\text{ kg/m²}$, $R^2 = 0.40$ (**+44.10% skill score gain**).
  - **Rootzone Moisture (10–40cm):** Ridge MAE $2.21\text{ kg/m²}$, RMSE $2.89\text{ kg/m²}$, $R^2 = 0.63$ (**+54.31% skill score gain**).
- **Tests Run & Results:**
  - Pytest suite: 31 passed in 8.04s (100% pass rate).
- **Acceptance Criteria Verification:**
  - [x] Zero temporal data leakage (all features and scalers constructed strictly on historical fold).
  - [x] Evaluated against credible naive benchmarks (Persistence, Seasonal Naive, Drift).
  - [x] Out-of-sample metrics reported honestly (MAE, RMSE, $R^2$).
  - [x] Predictions are deterministic and reproducible.
  - [x] Uncertainty intervals and model caveats are communicated.
  - [x] Live API endpoint `POST /api/v1/forecast` is operational.
- **Gate Passed:** Yes. Forecasting models and inference services are validated.
- **Next Stage:** Stage 6 — Backend API Completion & Optimization.

---

## 4. Current Work and Next Actions

1. Proceed to **Stage 6**: Backend API Completion & Optimization:
   - Finalize any auxiliary analytical endpoints (e.g. `GET /api/v1/regions`, `GET /api/v1/models`, `GET /api/v1/models/{model_id}/metrics`).
   - Add response caching and request downsampling utilities where needed.
   - Verify complete OpenAPI schema documentation at `/api/v1/docs`.
   - Ensure backend API is fully integrated before connecting into the Stage 7 frontend dashboard.
