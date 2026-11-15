# EarthScope: Complete Project Documentation

## 1. Project identity

**EarthScope** is an Earth-system trend intelligence platform built for the NASA Space Apps Challenge 2026 challenge, **“Be an Earth System Trend Detective!”**

The application examines monthly environmental records for Pakistan and helps users answer four practical questions:

1. What has changed over the historical record?
2. Which months were unusual?
3. What might happen over a user-selected future horizon?
4. Where do environmental patterns differ across Pakistan?

EarthScope combines NASA Earth-observation products, statistical trend analysis, anomaly detection, machine-learning forecasting, geographic summaries, and an accessible web interface.

The project is designed for both technical and non-technical audiences. A general user can explore plain-language results, while the underlying calculations, model metrics, data provenance, assumptions, and reports remain available for verification.

---

## 2. Problem statement

Climate and Earth-system data are abundant, but several barriers make them difficult to use:

- Environmental datasets contain multiple variables, units, spatial resolutions, and seasonal cycles.
- A raw increase in a variable may reflect the normal annual cycle rather than a long-term change.
- A few extreme months can distort ordinary linear trend estimates.
- Temperature, precipitation, soil moisture, and evapotranspiration are physically connected, but their relationships are difficult to see in isolated tables.
- Forecasts are often presented without a transparent historical test or an explanation of uncertainty.
- Scientific dashboards frequently expose method names before explaining what the result means.
- National averages can hide important differences between mountains, plains, deserts, and coastal regions.

The core problem is therefore not only “predict the next value.” It is:

> Turn complex, seasonal, multi-variable Earth-system records into evidence that people can inspect, understand, compare, and reproduce.

---

## 3. Our solution

EarthScope provides a single workflow from observation to interpretation:

```text
NASA datasets
    ↓
Validation and canonical monthly data
    ↓
Exploratory pattern discovery
    ↓
Seasonality and anomaly calculations
    ↓
Robust statistical trend detection
    ↓
Chronological model evaluation
    ↓
Persisted production forecasting artifacts
    ↓
FastAPI services
    ↓
Next.js interactive explorer
```

The product has five main user-facing areas:

| Area | Purpose |
|---|---|
| Home | Introduces the Pakistan climate record and routes users to the main questions |
| What changed | Shows historical series, anomalies, trend direction, significance, and graph modes |
| What comes next | Produces a forward forecast to a user-selected target year |
| Where | Shows Pakistan’s spatial domain, ecological zones, and variable-level geographic summaries |
| Sources | Provides reports, provenance, downloads, and methodological context |

The application uses real data and real saved evaluation metrics. It does not claim that one model has one universal “accuracy percentage.” Performance is reported per variable using out-of-sample metrics.

---

## 4. Scope and supported variables

EarthScope currently supports six monthly environmental variables:

| ID | Display name | Unit | Source family |
|---|---|---|---|
| `t2m` | 2-Meter Air Temperature | °C | NASA MERRA-2 |
| `ts` | Surface Skin Temperature | °C | NASA MERRA-2 |
| `precipitation` | Bias-Corrected Precipitation | mm/month | NASA MERRA-2 |
| `evapotranspiration` | Total Evapotranspiration | mm/month | NASA GLDAS-2.1 |
| `soil_moisture_0_10cm` | Topsoil Moisture (0–10 cm) | kg/m² | NASA GLDAS-2.1 |
| `soil_moisture_10_40cm` | Rootzone Moisture (10–40 cm) | kg/m² | NASA GLDAS-2.1 |

The records are area-averaged over Pakistan using the project’s documented national boundary. The primary period is 2001 through 2025, although individual variables may have slightly different final months depending on source availability.

The geographic domain is approximately:

- Latitude: 23.31°N to 37.69°N
- Longitude: 60.39°E to 77.73°E
- Projection metadata: WGS 84 / EPSG:4326

---

## 5. Data sources and data lifecycle

### 5.1 Source datasets

EarthScope uses:

- **MERRA-2** atmospheric reanalysis for air temperature, surface skin temperature, and corrected precipitation.
- **GLDAS-2.1 Noah Land Surface Model** for evapotranspiration and soil-moisture layers.

These are gridded Earth-system products. EarthScope converts them into canonical monthly records for the Pakistan study area.

### 5.2 Repository data locations

```text
datasets/              Raw or supplied source datasets
data/processed/        Canonical per-variable Parquet files
data/metadata/         Variable metadata, metrics, and catalogs
data/models/           Persisted joblib forecast bundles and manifest
docs/figures/          EDA, trend, and forecast diagnostic figures
```

The raw dataset directory is treated as read-only by the scientific pipeline. Processed data and generated artifacts are stored separately.

### 5.3 Canonical record shape

The API and analytical code operate on time-series records containing fields such as:

- `timestamp`
- `value`
- `display_value`
- `unit`
- `display_unit`
- `variable_id`
- `region`

The frontend does not perform scientific transformations. It requests structured responses from the backend and renders the supplied values and metadata.

### 5.4 Data quality controls

The project includes dataset auditing, validation, and testing scripts. The pipeline checks:

- Expected variable identifiers
- Date ordering and monthly cadence
- Missing values and valid numeric columns
- Unit and metadata consistency
- Spatial coverage and region identifiers
- Existence of processed files and model artifacts

Useful commands include:

```bash
python scripts/audit_datasets.py
python scripts/validate_scientific_integrity.py
python -m pytest
```

---

## 6. How patterns were identified from existing data

EarthScope does not begin by fitting a model blindly. The project first examines the historical record to understand its structure.

### 6.1 Descriptive profiles

For each variable, exploratory analysis calculates:

- Mean
- Median
- Standard deviation
- Minimum and maximum
- Skewness
- Kurtosis
- Monthly climatology
- Historical anomaly series
- Correlations with other variables

This identifies whether a variable is approximately symmetric, strongly seasonal, skewed, heavy-tailed, or persistent.

### 6.2 Seasonal cycle detection

All six variables show a strong annual rhythm. For example:

- Temperatures rise into late spring and summer.
- Precipitation peaks during the monsoon months.
- Topsoil and rootzone moisture respond after rainfall and retain water for longer.
- Evapotranspiration follows both available energy and water availability.

Because a large seasonal cycle can hide or imitate a long-term trend, EarthScope separates:

1. The expected calendar-month climatology.
2. The anomaly relative to that month’s climatology.

For a measurement \(y_t\) observed in calendar month \(m\), the anomaly is conceptually:

\[
a_t = y_t - \overline{y}_{m}
\]

where \(\overline{y}_{m}\) is the baseline mean for that calendar month.

The project’s documented climatology uses a 2001–2020 baseline for seasonal interpretation.

### 6.3 Distribution and outlier analysis

The distribution analysis showed that precipitation is highly non-normal:

- Strong positive skew
- Heavy tails
- Large monsoon extremes

This matters because ordinary least-squares regression can be pulled strongly by a few extreme observations. The analysis therefore uses robust non-parametric trend methods alongside linear regression.

### 6.4 Cross-variable relationships

The project compares both raw values and deseasonalized anomalies. This distinction is essential:

- Raw temperature and precipitation can appear positively related because both are higher during broad summer periods.
- After removing the normal seasonal cycle, unusually wet months are associated with cooler air and surface temperatures.
- Soil moisture anomalies show a strong positive relationship with evapotranspiration anomalies.
- Rootzone moisture responds more slowly than topsoil moisture, consistent with storage and drainage delay.

Documented exploratory findings include:

- Topsoil moisture versus evapotranspiration anomaly: approximately \(r = +0.896\)
- Rootzone moisture versus evapotranspiration anomaly: approximately \(r = +0.853\)
- Precipitation versus air-temperature anomaly: approximately \(r = -0.443\)
- Precipitation versus surface-temperature anomaly: approximately \(r = -0.517\)

These correlations are descriptive evidence, not proof of causation.

### 6.5 Historical event checks

The record reproduces recognizable events and conditions, including:

- The 2010 Indus flood period
- The 2001–2002 drought period
- The April 2022 heatwave signal
- The July–August 2022 extreme rainfall and flood period

These checks help verify that the processed series behaves physically and that anomalies correspond to meaningful historical events.

---

## 7. Statistical trend analysis

EarthScope uses multiple methods because each answers a different question.

### 7.1 Linear regression

The parametric baseline fits:

\[
y_t = \beta_0 + \beta_1t + \epsilon_t
\]

The slope \(\beta_1\) expresses a straight-line rate of change. It is useful for comparison, but it assumes conditions that may not hold for heavy-tailed precipitation or autocorrelated environmental data.

### 7.2 Mann–Kendall trend test

The Mann–Kendall test checks whether a series has a monotonic upward or downward tendency without requiring a normal distribution.

It is based on the signs of pairwise differences:

\[
S = \sum_{i=1}^{n-1}\sum_{j=i+1}^{n}\operatorname{sgn}(y_j-y_i)
\]

The result includes:

- Trend direction
- Test statistic
- p-value
- Significance decision

### 7.3 Sen’s slope

Sen’s slope is the median of all pairwise slopes:

\[
\beta_{\text{Sen}}
= \operatorname{median}\left(
\frac{y_j-y_i}{t_j-t_i}
\right)
\]

It is less sensitive to isolated extremes than ordinary least squares. This makes it especially useful for precipitation and flood-affected records.

### 7.4 Yue–Pilon pre-whitening

Monthly environmental data can be autocorrelated. For example, soil moisture in one month is related to soil moisture in the previous month.

Positive autocorrelation can make an apparent trend look more statistically certain than it really is. EarthScope uses trend-free pre-whitening based on the Yue–Pilon procedure:

1. Estimate the robust trend.
2. Remove the estimated trend.
3. Estimate serial autocorrelation.
4. Pre-whiten the residual series.
5. Add the trend back.
6. Apply the Mann–Kendall test to the adjusted series.

### 7.5 Seasonal Mann–Kendall

When the monthly seasonal structure must remain explicit, the seasonal test compares the same calendar month across years and aggregates the monthly statistics. This prevents January values from being compared directly with July values as if they belonged to the same seasonal regime.

### 7.6 Reported trend findings

The documented trend analysis reports the following approximate results for the 2001–2025 period:

| Variable | Sen slope per decade | 95% interval | p-value | Interpretation |
|---|---:|---:|---:|---|
| Precipitation | +7.29 mm/month | +5.25 to +9.49 | < 0.0001 | Increasing, significant |
| Evapotranspiration | +3.32 mm/month | +2.15 to +4.48 | < 0.0001 | Increasing, significant |
| Topsoil moisture | +1.06 kg/m² | +0.66 to +1.45 | < 0.0001 | Increasing, significant |
| Rootzone moisture | +1.97 kg/m² | +1.30 to +2.64 | < 0.0001 | Increasing, significant |
| Surface skin temperature | −0.255 °C | −0.446 to −0.066 | 0.0037 | Decreasing, significant |
| 2-meter air temperature | −0.158 °C | −0.330 to +0.008 | 0.0572 | No detected trend at 0.05 |

These are area-averaged results and should not be interpreted as every location in Pakistan experiencing the same trend.

---

## 8. Forecasting task

The forecast task is monthly multi-step prediction for each supported variable.

The standard evaluation design is:

| Partition | Period |
|---|---|
| Training history | 2001-01 through 2022-12 |
| Unseen holdout | 2023-01 through 2025-09 or 2025-12 |
| Evaluation style | Strict chronological split |
| Production fit | Full available history after evaluation |
| API horizon | 1 to 60 months, subject to schema validation |

The frontend converts a user-selected target year into the number of months needed from the latest observation. The backend then generates future monthly timestamps.

This is not a claim that the model knows the future with certainty. It is a forward projection based on historical dynamics, seasonality, lag structure, and the selected variable’s observed behavior.

---

## 9. Feature engineering

All machine-learning features are created using information available at or before the forecast origin.

### 9.1 Autoregressive lags

The feature extractor creates:

- 1-month lag
- 2-month lag
- 3-month lag
- 12-month lag
- 24-month lag

The 12-month lag helps capture the same calendar month in the previous year. Short lags capture recent persistence, while the 24-month lag captures longer seasonal recurrence.

### 9.2 Rolling statistics

The feature extractor creates shifted rolling features for:

- 3-month rolling mean
- 3-month rolling standard deviation
- 12-month rolling mean
- 12-month rolling standard deviation

The target is shifted by one month before rolling calculations. This prevents the current target value from leaking into its own features.

### 9.3 Fourier seasonality

The model receives harmonic calendar features:

\[
\sin(2\pi m/12),\quad \cos(2\pi m/12)
\]

\[
\sin(4\pi m/12),\quad \cos(4\pi m/12)
\]

These provide smooth annual and semi-annual seasonal structure without creating a separate one-hot variable for every month.

### 9.4 Time trend

The feature extractor includes elapsed time in normalized years. This allows models to represent gradual drift while retaining lag and seasonal information.

### 9.5 Leakage prevention

The evaluator:

- Splits the series chronologically.
- Fits models only on the training partition.
- Does not shuffle monthly observations.
- Applies scaling inside the Ridge pipeline.
- Uses shifted rolling features.
- Evaluates against future observations never used for fitting.

This is one of the most important safeguards in the project. Random train/test splitting would allow future-like patterns from the same time period to leak into training and would give an overly optimistic result.

---

## 10. Model ladder

EarthScope compares simple baselines with machine-learning candidates.

### 10.1 Persistence baseline

Predicts the most recent observed value for every future month.

This answers:

> How much can we achieve by assuming the latest level simply continues?

### 10.2 Seasonal naive baseline

Repeats the value from the same calendar month one year earlier.

This is a strong and important baseline for seasonal climate data.

### 10.3 Linear drift baseline

Fits one straight line over the training history and extrapolates it.

This tests whether a simple long-term drift is enough without autoregressive or seasonal features.

### 10.4 Regularized lagged Ridge regression

This is a linear machine-learning model with:

- StandardScaler feature normalization
- L2 regularization
- Lag features
- Rolling summaries
- Fourier seasonal terms
- Time trend

Ridge is useful because environmental predictors can be correlated. L2 regularization stabilizes coefficients and reduces overfitting.

### 10.5 Random Forest regression

The Random Forest candidate uses:

- 100 trees
- Maximum depth of 6
- Fixed random seed 42
- Parallel tree fitting

It can represent non-linear interactions and threshold effects that a linear Ridge model cannot.

---

## 11. How the model is selected

For each variable, every model in the ladder is evaluated on the same chronological holdout.

The production recommendation is selected by the lowest holdout RMSE:

```text
recommended_model = model with minimum chronological holdout RMSE
```

This selection is variable-specific. The model that is best for temperature does not have to be best for evapotranspiration or precipitation.

The current documented results show:

- Ridge is strongest for air temperature.
- Ridge is strongest for surface skin temperature.
- Ridge is strongest for precipitation.
- Random Forest is strongest for evapotranspiration.
- Ridge is strongest for topsoil moisture.
- Ridge is strongest for rootzone moisture.

The current public UI uses the recommended production model automatically so ordinary users do not need to choose among technical model names.

---

## 12. Model evaluation

### 12.1 Metrics

#### MAE

Mean Absolute Error is the average absolute difference between prediction and observation:

\[
\operatorname{MAE} = \frac{1}{n}\sum_{i=1}^{n}|y_i-\hat{y}_i|
\]

It is easy to interpret in the original unit.

#### RMSE

Root Mean Squared Error gives more weight to larger errors:

\[
\operatorname{RMSE}
= \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat{y}_i)^2}
\]

RMSE is the primary selection metric for the recommendation rule.

#### R²

R² compares the model with predicting the test-set mean:

\[
R^2 = 1 - \frac{\sum(y_i-\hat{y}_i)^2}
{\sum(y_i-\bar{y})^2}
\]

An R² near 1 indicates strong explanatory performance on the holdout. A negative R² means the model is worse than the mean baseline for that test period.

#### Skill score

EarthScope reports skill relative to the seasonal-naive baseline:

\[
\operatorname{Skill}
= 1 - \frac{\operatorname{RMSE}_{model}}
{\operatorname{RMSE}_{seasonal\ naive}}
\]

Positive skill means lower RMSE than the seasonal-naive reference.

### 12.2 Out-of-sample results

The saved evaluation metrics report the following recommended-model results:

| Variable | Recommended model | MAE | RMSE | R² | Skill vs seasonal naive |
|---|---|---:|---:|---:|---:|
| Air temperature | Ridge | 1.3177 °C | 1.5669 °C | 0.9539 | 29.04% |
| Surface temperature | Ridge | 1.41 °C | 1.64 °C | 0.96 | 36.24% |
| Precipitation | Ridge | 23.90 mm/month | 32.65 mm/month | 0.2767 | 54.45% |
| Evapotranspiration | Random Forest | 5.55 mm/month | 7.31 mm/month | 0.8383 | 43.02% |
| Topsoil moisture | Ridge | 1.83 kg/m² | 2.18 kg/m² | 0.4015 | 44.10% |
| Rootzone moisture | Ridge | 2.21 kg/m² | 2.89 kg/m² | 0.6314 | 54.31% |

These values explain why there is no single “accuracy” number for EarthScope. Temperature is highly predictable in this dataset, while precipitation is much more volatile. A precipitation R² of approximately 0.28 can still represent useful improvement over the seasonal-naive benchmark, but it should not be described as highly accurate.

### 12.3 Why precipitation is harder

Precipitation is driven by episodic weather systems and monsoon bursts. Its heavy-tailed distribution means:

- A few months can dominate the error.
- Repeating last year’s value may fail badly.
- A model can improve substantially over the baseline while still leaving considerable unexplained variability.

The interface should therefore communicate precipitation forecasts as an informed range, not a certain prediction.

---

## 13. Training and artifact persistence

The training pipeline is implemented in:

```text
scripts/train_forecast_models.py
```

The pipeline performs these steps for all six variables:

1. Load the processed Parquet file.
2. Evaluate all models using the 2022-12-01 chronological cutoff.
3. Select the lowest-RMSE model.
4. Fit production estimators on the full available history.
5. Save one joblib bundle for the variable.
6. Generate a 24-month forward diagnostic projection.
7. Write evaluation metrics JSON.
8. Write diagnostic figures.

Run it with:

```bash
python scripts/train_forecast_models.py
```

### 13.1 Saved files

```text
data/models/t2m.joblib
data/models/ts.joblib
data/models/precipitation.joblib
data/models/evapotranspiration.joblib
data/models/soil_moisture_0_10cm.joblib
data/models/soil_moisture_10_40cm.joblib
data/models/manifest.json
data/metadata/model_evaluation_metrics.json
```

### 13.2 Bundle contents

Each joblib bundle stores:

- Artifact schema version
- Variable identifier
- Region
- Training mode
- Training timestamp
- Full-history date range
- Holdout cutoff
- Holdout periods and metrics
- Recommended model ID
- Feature names
- Feature-extractor configuration
- Fitted persistence model
- Fitted seasonal-naive model
- Fitted linear-drift model
- Fitted Ridge estimator
- Fitted Random Forest estimator

This means the production API loads already-trained artifacts instead of retraining a model on every request.

---

## 14. Forecast inference and uncertainty

The FastAPI forecast endpoint accepts:

```text
POST /api/v1/forecast
```

The request includes:

- `variable_id`
- `horizon_months`
- `model_id`
- `confidence_level`

The public frontend uses the recommended model and a fixed 95% uncertainty level so normal users are not forced to choose technical parameters.

The inference service:

1. Loads the saved bundle.
2. Loads the processed historical frame.
3. Reconstructs future monthly features.
4. Forecasts recursively across the requested horizon.
5. Computes lower and upper prediction bounds.
6. Applies physical non-negative bounds where appropriate.
7. Returns predictions, intervals, model identity, metrics, and limitations.

Prediction intervals expand with the forecast horizon. A farther-away month should generally have more uncertainty than a near-term month.

The interval is not a guarantee that the true value will fall inside the band. It is a calibrated uncertainty representation based on historical holdout behavior and the selected confidence level.

---

## 15. Backend API

The backend is a FastAPI application mounted under:

```text
/api/v1
```

Available endpoint groups include:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Backend health and version |
| GET | `/api/v1/datasets` | Dataset catalog |
| GET | `/api/v1/variables` | Supported variable metadata |
| GET | `/api/v1/regions` | Region metadata |
| GET | `/api/v1/timeseries` | Historical monthly series |
| POST | `/api/v1/analysis/trend` | Statistical trend analysis |
| POST | `/api/v1/analysis/anomalies` | Historical anomaly and extreme-event analysis |
| POST | `/api/v1/forecast` | Multi-month forecast |
| GET | `/api/v1/models` | Model catalog |
| GET | `/api/v1/models/{model_id}/metrics` | Model metrics |
| GET | `/api/v1/reports` | Available reports |
| GET | `/api/v1/reports/{report_id}` | Report details |
| GET | `/api/v1/spatial/summary` | Geographic summary and zones |

OpenAPI documentation is available at:

```text
/api/v1/docs
```

The backend uses Pydantic response schemas to keep API contracts explicit and machine-readable.

### 15.1 Error handling

The backend returns structured validation errors for invalid requests. Forecast failures are reported as HTTP errors rather than silently returning a successful-looking response.

### 15.2 Caching

Forecast responses are cached using request parameters including:

- Endpoint
- Variable
- Horizon
- Model
- Confidence level

This reduces repeated computation for identical requests.

---

## 16. Frontend behavior

The frontend is a Next.js 14 App Router application.

Important files:

```text
frontend/app/page.tsx
frontend/app/layout.tsx
frontend/app/globals.css
frontend/components/Navbar.tsx
frontend/components/OverviewView.tsx
frontend/components/TrendExplorerView.tsx
frontend/components/ForecastExplorerView.tsx
frontend/components/GeographicView.tsx
frontend/components/ReportsView.tsx
frontend/components/ScientificChart.tsx
frontend/lib/api.ts
```

### 16.1 Home

The home screen explains the product in plain language and provides paths to:

- Historical changes
- Future projections
- Geographic comparisons

It also presents the six available signals and their units.

### 16.2 Trend Explorer

The Trend Explorer supports:

- Variable selection
- Observed record view
- Deseasonalized anomaly view
- Trend line graph
- Anomaly bar graph
- Seasonal monthly profile
- Month-specific anomaly filtering
- Interactive chart hover details
- Trend direction and slope
- Significance status
- Confidence interval for the trend slope
- Methodological assumptions and limitations

### 16.3 Forecast Explorer

The Forecast Explorer supports:

- Variable selection
- Custom target year
- Historical and future values in one chart
- Forecast origin marker
- Prediction interval
- Historical validation metrics
- Plain-language explanation of the forecast

The model and confidence controls were intentionally removed from the public interface. The backend still supports those parameters for programmatic and research use.

### 16.4 Geographic Explorer

The geographic view provides:

- Pakistan boundary representation
- Latitude and longitude context
- Ecological-zone markers
- Variable-layer selection
- Zone detail panel
- National trend summary
- FDR significance indicator
- Links back to the corresponding time-series view

The current map is a data-informed schematic representation rather than a full GIS tile map. Its purpose is to make the geographic scope and zone comparisons understandable within the application.

### 16.5 Sources and reports

The reports area exposes:

- Methodology documents
- Data provenance
- Source descriptions
- Report excerpts
- Download and inspection affordances where implemented

---

## 17. Technology stack

### Frontend

| Technology | Role |
|---|---|
| Next.js 14 | React application framework |
| React 18 | Component and state model |
| TypeScript | Static typing |
| Tailwind CSS | Layout and utility styling |
| Lucide React | Interface icons |
| Inline SVG | Accessible charts and map diagrams |

### Backend

| Technology | Role |
|---|---|
| Python | Scientific and service implementation |
| FastAPI | REST API framework |
| Pydantic v2 | Request and response validation |
| Uvicorn | ASGI server |
| Pydantic Settings | Environment configuration |

### Scientific and ML stack

| Technology | Role |
|---|---|
| Pandas | Tabular time-series processing |
| NumPy | Numeric computation |
| SciPy | Scientific statistics |
| scikit-learn | Ridge, Random Forest, scaling, metrics |
| PyMannKendall | Mann–Kendall trend testing |
| PyArrow | Parquet storage |
| Joblib | Model artifact persistence |
| Matplotlib | Offline diagnostic figures |

### Testing and quality

| Tool | Role |
|---|---|
| Pytest | Backend tests |
| pytest-asyncio | Async API test support |
| Node smoke scripts | Frontend and integration checks |
| TypeScript build checks | Frontend type safety |
| Hallmark render sweep | UI accessibility and visual quality checks |

---

## 18. Local development

### 18.1 Backend

From the repository root:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Start the API:

```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 18.2 Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

### 18.3 Environment variables

Create a local `.env` or frontend `.env.local` based on the example files.

Backend:

```text
HOST=127.0.0.1
PORT=8000
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

Frontend:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, `NEXT_PUBLIC_API_URL` must be the public HTTPS backend URL.

---

## 19. Testing and validation

### Backend tests

```bash
python -m pytest
```

The backend suite covers:

- Health endpoint
- API schemas
- Forecast behavior
- Trend methods
- Model registry
- Pipeline behavior
- Audit and integrity checks

### Frontend tests

```bash
cd frontend
npm test
```

The frontend test command runs the project’s health and end-to-end workflow scripts.

### Production build

```bash
cd frontend
npm run build
```

### Scientific validation

```bash
python scripts/validate_scientific_integrity.py
```

This project should be considered ready for a demo only after:

1. Backend tests pass.
2. Frontend production build passes.
3. Processed files and model artifacts exist.
4. The health endpoint responds.
5. The frontend can reach the backend through configured CORS.
6. Forecast and trend responses contain the expected variable IDs and units.

---

## 20. Deployment

The simplest free deployment is:

```text
Vercel Hobby       → Next.js frontend
Render Free        → FastAPI backend
```

### 20.1 Backend on Render

Build command:

```bash
pip install -r backend/requirements.txt
```

Start command:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Set:

```text
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

The repository’s `datasets/`, `data/processed/`, `data/metadata/`, and `data/models/` directories must be available to the backend deployment.

### 20.2 Frontend on Vercel

Set the project root to:

```text
frontend
```

Build command:

```bash
npm run build
```

Set:

```text
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### 20.3 Free-tier limitations

Free backend services may:

- Sleep after inactivity
- Take time to wake up
- Have limited memory
- Be slow for large data operations
- Time out during expensive calculations

For a hackathon demo, precomputed processed data and saved joblib artifacts should be deployed. Models should not be retrained during an HTTP request.

---

## 21. Reproducibility workflow

A complete reproduction sequence is:

```bash
pip install -r backend/requirements.txt
python scripts/audit_datasets.py
python scripts/run_pipeline.py
python scripts/run_eda.py
python scripts/run_trends.py
python scripts/train_forecast_models.py
python scripts/validate_scientific_integrity.py
python -m pytest
cd frontend
npm install
npm run build
```

The exact command sequence may depend on whether the supplied processed data already exists. The training script expects the canonical Parquet files under `data/processed/`.

Generated outputs include:

- Evaluation JSON
- Model bundles
- Model manifest
- Trend and anomaly reports
- Diagnostic figures

---

## 22. Limitations and responsible interpretation

EarthScope is an analytical and educational platform, not an operational early-warning system.

### Data limitations

- NASA reanalysis and land-surface products are modeled observations, not direct measurements at every location.
- National averages hide local extremes.
- Variables may have different final observation months.
- Spatial resolution differs between source products.

### Statistical limitations

- A statistically significant trend is not automatically causal.
- The result depends on the selected period and climatology baseline.
- Multiple testing and spatial aggregation require careful interpretation.
- Precipitation’s heavy tails make its trend and forecast uncertainty larger.

### Forecast limitations

- Forecasts are extrapolations from historical behavior.
- Long horizons accumulate uncertainty.
- Extreme regime changes may not be represented in the training history.
- Good historical R² does not guarantee future operational accuracy.
- Forecast intervals communicate uncertainty; they do not guarantee coverage.

### Product limitations

- The current geographic representation is a schematic map, not a full high-resolution GIS viewer.
- Offline frontend fallbacks are for presentation continuity and should not be confused with live backend data.
- The frontend’s plain-language summaries simplify technical concepts; the source reports remain the authoritative detail.

---

## 23. Future improvements

Potential next steps include:

1. Add automated CI for backend tests and frontend builds.
2. Add a deployment health check and smoke test against the live API.
3. Store dataset version hashes alongside model artifacts.
4. Add rolling-origin evaluation in addition to the single chronological holdout.
5. Add probabilistic calibration diagnostics for prediction intervals.
6. Add higher-resolution spatial tiles or GeoJSON layers.
7. Add user-selectable geographic regions where data supports them.
8. Add automated model retraining only through an explicit scheduled pipeline.
9. Add data freshness indicators for each variable.
10. Add exportable CSV and JSON results for charts and forecasts.
11. Add a model card for each recommended model.
12. Add uncertainty explanations directly beside forecast intervals.

---

## 24. Key project files

| File | Responsibility |
|---|---|
| `backend/app/main.py` | FastAPI application, CORS, error handling, router registration |
| `backend/app/api/v1/router.py` | API endpoint registration |
| `backend/app/core/config.py` | Environment and filesystem configuration |
| `backend/app/api/v1/endpoints/forecast.py` | Forecast request validation, caching, inference |
| `backend/ml/features/pipeline.py` | Leakage-safe time-series feature engineering |
| `backend/ml/training/models.py` | Baselines and ML model classes |
| `backend/ml/evaluation/validator.py` | Chronological holdout evaluation |
| `backend/ml/training/persistence.py` | Joblib bundles, manifests, recommendation rule |
| `backend/ml/inference/service.py` | Saved-model forecast generation and intervals |
| `scripts/train_forecast_models.py` | Evaluation, production fitting, persistence, figures |
| `data/metadata/model_evaluation_metrics.json` | Saved out-of-sample metrics |
| `frontend/lib/api.ts` | Typed frontend API client and verified fallbacks |
| `frontend/components/ScientificChart.tsx` | Interactive SVG line, bar, seasonal, and forecast charts |
| `frontend/components/TrendExplorerView.tsx` | Trend, anomaly, month-filter, and graph controls |
| `frontend/components/ForecastExplorerView.tsx` | Target-year forecast experience |
| `frontend/components/GeographicView.tsx` | Spatial summary and ecological-zone explorer |
| `docs/forecasting-methodology.md` | Detailed forecasting methodology |
| `docs/statistical-methodology.md` | Detailed trend methodology |
| `docs/eda-findings.md` | Exploratory pattern and physical interpretation findings |

---

## 25. Final summary

EarthScope is a complete evidence-to-explanation workflow:

1. It starts with monthly NASA Earth-system records for Pakistan.
2. It validates and standardizes those records.
3. It identifies seasonal cycles, anomalies, extremes, and cross-variable relationships.
4. It uses robust statistical methods to quantify long-term trends.
5. It compares forecasting models using an honest chronological holdout.
6. It selects a recommended model separately for each variable.
7. It fits production artifacts on the available history without retraining during API requests.
8. It exposes typed FastAPI endpoints.
9. It presents the results through a plain-language Next.js interface.
10. It keeps metrics, assumptions, data provenance, limitations, and source reports visible for verification.

The central design principle is simple:

> Show the evidence clearly, explain what it means, and make uncertainty visible instead of hiding it.
