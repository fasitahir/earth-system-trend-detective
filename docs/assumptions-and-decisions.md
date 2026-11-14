# Assumptions and Decisions Record (ADR)

## ADR-001: Separation of Frontend and Backend
- **Date:** 2026-11-14
- **Status:** Accepted
- **Context:** The application requires both high-performance scientific data manipulation (Xarray, Pandas, SciPy, Scikit-learn) and a modern, accessible web dashboard.
- **Decision:** Build a decoupled Python FastAPI backend and a Next.js (TypeScript + Tailwind CSS) frontend.
- **Consequence:** Scientific calculations remain isolated in Python modules and testable via pytest. The frontend acts strictly as a presentation and interaction layer consuming structured REST endpoints.

---

## ADR-002: Evidence-Based Regional Scope (Pakistan Area-Averaged Series)
- **Date:** 2026-11-14
- **Status:** Accepted
- **Context:** Inspection of the supplied raw files in `datasets/` revealed they originate from NASA Giovanni queries over `shape=state_dept_countries_2017/shp_171`, which corresponds to **Pakistan** (`Shape Pakistan`, bounding coordinates lat 23.31°N–37.69°N, lon 60.39°E–77.73°E) for the monthly period 2001–2025.
- **Decision:** Explicitly model the geographic scope as **Pakistan** (national area-averaged time series across atmospheric and hydrological variables).
- **Rule:** Do not invent arbitrary global grid coordinates or claim sub-regional data where only area-averaged series are provided. Disclose this geographic scope in all UI and metadata responses.

---

## ADR-003: Core Environmental Variables in Supplied Datasets
- **Date:** 2026-11-14
- **Status:** Accepted
- **Context:** The supplied data contains 6 physical time series:
  1. `M2TMNXSLV_5_12_4_T2M`: 2-meter air temperature (MERRA-2, monthly, 2001-01 to 2025-12, K).
  2. `M2TMNXSLV_5_12_4_TS`: Surface skin temperature (MERRA-2, monthly, 2001-01 to 2025-12, K).
  3. `M2TMNXFLX_5_12_4_PRECTOTCORR`: Bias-corrected total surface precipitation (MERRA-2, monthly, 2001-01 to 2025-09, kg m-2 s-1).
  4. `GLDAS_NOAH10_M_2_1_Evap_tavg`: Total evapotranspiration (GLDAS-2.1, monthly, 2001-01 to 2025-12, kg m-2 s-1).
  5. `GLDAS_NOAH10_M_2_1_SoilMoi0_10cm_inst`: Soil moisture 0–10 cm (GLDAS-2.1, monthly, 2001-01 to 2025-09, kg m-2).
  6. `GLDAS_NOAH10_M_2_1_SoilMoi10_40cm_inst`: Soil moisture 10–40 cm (GLDAS-2.1, monthly, 2001-01 to 2025-09, kg m-2).
- **Decision:** Standardize these 6 variables as the EarthScope Core Hydrometeorological Suite for Pakistan, representing interconnected atmosphere, surface, and hydrological dynamics.

---

## ADR-004: Missing Value Handling
- **Date:** 2026-11-14
- **Status:** Accepted
- **Context:** In NASA Giovanni CSV and NetCDF files, fill values are specified (e.g. `1000000000000000` or `-9999`).
- **Decision:** Ingestion pipelines must identify declared fill values and map them to `NaN` or `None`. Under no circumstance will missing data be coerced to `0.0`.

---

## ADR-005: Persist Production Forecast Models Separately from Holdout Evaluation
- **Date:** 2026-11-14
- **Status:** Accepted
- **Context:** Stage 5 evaluated models honestly on a chronological holdout, but only serialized metrics JSON and plots. The forecast API then refit sklearn estimators on every request.
- **Decision:** After holdout evaluation, fit a **production** copy of each ladder model on the full available history and serialize it with joblib under `data/models/{variable_id}.joblib`. Serving loads those artifacts and reuses frozen holdout RMSE for prediction intervals.
- **Consequence:** Forecasts are reproducible without retraining. Holdout metrics remain an out-of-sample score, not a claim that production weights were trained only through 2022. If processed observations are extended, operators must re-run `python scripts/train_forecast_models.py`.
