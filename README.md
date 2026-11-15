# EarthScope — Earth System Trend Intelligence

**NASA Space Apps Challenge 2026:** "Be an Earth System Trend Detective!"  
**Stage:** Stage 6 Complete (Backend API + persisted forecast artifacts)

> **Full project documentation:** [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md)
> This guide explains the problem, NASA data sources, preprocessing, pattern discovery, statistical methods, ML training and evaluation, API/frontend architecture, deployment, limitations, and reproducibility.

---

## 1. Mission Overview

**EarthScope** is a scientifically credible, competition-quality Earth-system trend intelligence platform. It enables researchers, policymakers, and the public to:
1. **Discover & Inspect** interconnected environmental datasets from NASA Earth-observing systems (MERRA-2 atmospheric reanalysis and GLDAS land data assimilation).
2. **Quantify Historical Trends** using defensible statistical methods (Mann-Kendall monotonic trend tests, Sen's robust slope estimator, linear regression, and seasonal cycle isolation).
3. **Generate Out-of-Sample Forecasts** using machine learning and time-series methods benchmarked against naive baselines with prediction intervals.
4. **Communicate Findings** with complete transparency into data provenance, statistical significance, physical units, and limitations.

---

## 2. Repository Architecture

```text
Earth-System-Trend-Detective/
├── backend/                             # Python FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/health.py  # Health check & system status
│   │   ├── core/config.py              # Pydantic Settings
│   │   ├── schemas/                    # Pydantic request/response contracts
│   │   └── main.py                     # FastAPI application entry point
│   ├── data_pipeline/                  # Ingestion, validation, preprocessing
│   ├── analytics/                      # EDA, trend detection, anomalies
│   ├── ml/                             # Features, training, inference
│   ├── tests/                          # Automated backend test suite
│   └── requirements.txt
├── datasets/                            # Supplied NASA Giovanni datasets (read-only)
├── frontend/                            # Next.js 14 / TypeScript / Tailwind CSS
│   ├── app/                            # App Router pages and layout
│   ├── lib/api.ts                      # Client for backend API
│   └── package.json
├── docs/                                # Living engineering & scientific docs
│   ├── PROJECT_DOCUMENTATION.md         # Complete project and implementation guide
│   ├── PROJECT_STATUS.md
│   ├── architecture.md
│   ├── requirements-and-acceptance.md
│   ├── assumptions-and-decisions.md
│   └── research-sources.md
├── pytest.ini                           # Pytest test configuration
├── .env.example                         # Environment template
└── README.md
```

---

## 3. Quick Start Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ (tested on Node.js 24)
- Git

### 3.1 Backend Setup & Execution

1. **Install Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Run Backend Automated Tests:**
   ```bash
   python -m pytest
   ```

3. **Start FastAPI Development Server:**
   ```bash
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   - OpenAPI Interactive Docs: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
   - Health Status: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

### 3.2 Frontend Setup & Execution

1. **Install Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run Frontend Smoke Tests:**
   ```bash
   npm test
   ```

3. **Start Next.js Development Server:**
   ```bash
   npm run dev
   ```
   - Application URL: [http://localhost:3000](http://localhost:3000)

---

## 4. Environment Variables

Copy `.env.example` to configure local variables:
```bash
cp .env.example .env
```
Key configuration keys:
- `HOST`: Server host (default `127.0.0.1`)
- `PORT`: Server port (default `8000`)
- `CORS_ORIGINS`: Allowed origins (e.g. `http://localhost:3000`)
- `NEXT_PUBLIC_API_URL`: Backend URL for frontend client (default `http://localhost:8000`)

### Render deployment

The repository includes [`render.yaml`](render.yaml), which defines the FastAPI
web service, health check, build command, and start command. To use it, create
a Render Blueprint from this repository. The included Blueprint allows all
origins for simple hackathon deployment. For a stricter production setup,
replace `CORS_ORIGINS` with a JSON array containing the exact public URL of
the deployed frontend, for example:

```text
["*"]
```

Restricted example:

```text
["https://your-frontend.vercel.app"]
```

---

## 5. Stage Progress & Next Steps

Follow the living stage-gate log in [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md):

- **Stages 0–5 (Architecture through forecasting):** `COMPLETE`
- **Stage 6 (Backend API services):** `COMPLETE`
- **Stage 7 (Frontend dashboard):** `NOT STARTED`

Train and persist forecast artifacts (required before serving production forecasts):

```bash
python scripts/train_forecast_models.py
```

Artifacts land in `data/models/{variable_id}.joblib` with a catalog at `data/models/manifest.json`.
