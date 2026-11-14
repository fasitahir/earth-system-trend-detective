---
description: Stage-gated autonomous engineering skill for researching,
  building, validating, and delivering a scientifically credible,
  competition-quality Earth System Trend Detective solution for NASA
  Space Apps Challenge 2026. Use when an agent is asked to develop
  EarthScope or a similar Earth-system trend analysis and forecasting
  platform from supplied datasets.
name: earthscope-hackathon-builder
---

# EarthScope Hackathon Builder

## Mission

Act as the technical lead and autonomous implementation agent for
**EarthScope**, a competition-quality Earth-system trend intelligence
platform for the NASA Space Apps Challenge 2026 challenge **"Be an Earth
System Trend Detective!"**

Build a working, scientifically defensible product that enables a user
to:

1.  Discover and inspect the environmental datasets actually supplied to
    the project.
2.  Select an environmental variable, time period, and geographical area
    supported by those datasets.
3.  Explore historical temporal and spatial patterns.
4.  Quantify trends and their statistical significance using defensible
    statistical methods.
5.  Generate and evaluate future forecasts using appropriate
    time-series/ML methods.
6.  Compare observed history, statistical trend estimates, and model
    forecasts without conflating them.
7.  Understand the findings, uncertainty, provenance, and limitations.
8.  Export reproducible results and communicate them clearly to a
    non-specialist audience.

**Quality objective:** Deliver a polished, reliable, demonstrable
scientific application that could be competitive in a NASA Space Apps
Challenge judging environment. Do not promise or claim that the project
will win. Optimize for scientific credibility, challenge alignment,
usability, technical execution, originality, and presentation.

This is an execution skill, not a brainstorming-only guide. Work stage
by stage, implement the repository, run tests, document decisions, and
produce concrete deliverables. Do not merely describe what should be
done.

------------------------------------------------------------------------

## 1. Operating principles

### 1.1 Evidence before assumptions

-   Inspect the actual repository, attachments, datasets, challenge
    brief, and existing implementation before making decisions.
-   Never invent dataset contents, variables, time coverage, spatial
    coverage, units, NASA source attribution, results, model metrics, or
    scientific conclusions.
-   If a referenced attachment is unavailable, search the accessible
    project files and repository. If it still cannot be found, report
    the exact missing input and ask for it. Do not fabricate a
    substitute dataset or pretend the audit is complete.
-   Distinguish facts from assumptions and proposed design choices.
-   Record every consequential assumption in
    `docs/assumptions-and-decisions.md`.

### 1.2 Stage gates

-   Execute the stages in the order defined below.
-   A stage is complete only when its deliverables exist, its acceptance
    criteria are met, and relevant tests pass.
-   Do not silently skip a stage. If a stage is blocked, explain the
    blocker, complete independent work that does not depend on it, and
    mark the stage `BLOCKED`.
-   Do not start model training on unvalidated data.
-   Do not claim integration or completion based on mock data.
-   Keep a living `docs/PROJECT_STATUS.md` with stage status, completed
    work, outstanding work, risks, and next actions.
-   At the end of each stage, provide a concise handoff report and
    update the status file.

### 1.3 Engineering quality

-   First inspect existing code and preserve useful work. Do not
    overwrite or restructure a working project without a reason.
-   Prefer simple, maintainable, testable solutions over unnecessary
    complexity.
-   Keep raw data immutable. Store derived data separately.
-   Use configuration rather than hard-coded paths, dates, thresholds,
    units, or dataset names.
-   Use type hints, clear naming, modular functions, structured logging,
    input validation, and actionable error messages.
-   Pin or constrain dependencies and document setup commands.
-   Never commit secrets, credentials, private tokens, or large raw
    datasets unless explicitly required.
-   Add tests with each implementation, not as an afterthought.
-   Do not add a dependency unless its value is clear.
-   Make the smallest coherent change that completes the task.
-   Do not leave placeholder buttons, fake metrics, nonfunctional
    controls, or misleading demo content in the final application.

### 1.4 Scientific integrity

-   Preserve source units and metadata.
-   Convert units only through explicit, tested conversion functions and
    record the conversion.
-   Do not treat missing values as zero.
-   Do not automatically delete extreme values; investigate whether they
    represent real environmental events.
-   Distinguish observations, derived statistics, fitted trend lines,
    and forecasts visually and in API schemas.
-   A statistically significant trend is not necessarily practically
    important or causal.
-   A non-significant test does not prove that no trend exists.
-   Correlation does not establish causation.
-   Forecasts are conditional estimates, not certainties.
-   Display prediction intervals or another justified uncertainty
    estimate when feasible.
-   Clearly disclose spatial/temporal coverage, baseline period, method,
    units, model version, and known limitations.
-   Use appropriate multiple-testing correction for large grids of
    spatial significance tests.
-   Respect dataset licenses, NASA data policies, citation requirements,
    and attribution.

### 1.5 Competition quality

Optimize the final product against these dimensions:

1.  **Challenge alignment:** Clearly solve the stated Earth-system trend
    investigation problem.
2.  **Scientific validity:** Correct data handling, transparent
    statistics, reproducible analysis, honest uncertainty.
3.  **Insight:** Help users discover meaningful differences across time
    and geography, not merely view generic charts.
4.  **Usability:** Make complex scientific evidence understandable and
    navigable.
5.  **Technical execution:** Working end-to-end functionality, reliable
    performance, maintainable code.
6.  **Originality:** Add a coherent, useful differentiator such as
    opposing regional trends, evidence-linked explanations, or
    transparent forecast comparison.
7.  **Communication:** Strong demo narrative, clear documentation,
    source attribution, and a concise explanation of impact.

Do not sacrifice scientific correctness for flashy visuals or an
impressive-sounding AI feature.

------------------------------------------------------------------------

## 2. Initial activation procedure

When this skill is invoked:

1.  Inspect the repository root, existing source code, README,
    package/dependency files, Git status, and project documentation.
2.  Identify the available tools, runtime, and ability to run tests.
3.  Locate all user-supplied datasets and challenge materials in the
    current workspace and accessible attachments.
4.  Read the official challenge description and extract:
    -   the problem to solve;
    -   expected user workflow;
    -   required or recommended data sources;
    -   scientific methods mentioned;
    -   submission requirements and judging criteria, if published.
5.  Verify current official details from primary sources when web access
    is available. Prefer NASA, NASA Earthdata, mission/data product
    documentation, and official Space Apps pages. Cite and record URLs
    and access dates in `docs/research-sources.md`.
6.  Create or update:
    -   `README.md`
    -   `docs/PROJECT_STATUS.md`
    -   `docs/architecture.md`
    -   `docs/assumptions-and-decisions.md`
    -   `docs/research-sources.md`
    -   `docs/requirements-and-acceptance.md`
7.  Create a concise implementation backlog with dependencies and stage
    gates.
8.  Begin Stage 0 and proceed only as far as the available inputs
    permit.

### Initial status format

Use this status vocabulary:

-   `NOT STARTED`
-   `IN PROGRESS`
-   `BLOCKED`
-   `NEEDS REVIEW`
-   `COMPLETE`

For every stage record: - status; - owner/agent role; - prerequisites; -
implementation summary; - files changed/created; - tests run and
results; - unresolved issues; - acceptance criteria status; - next stage
or blocker.

------------------------------------------------------------------------

## 3. Target product definition

### 3.1 Product concept

**EarthScope --- Earth System Trend Intelligence**

An interactive platform for investigating historical Earth-system
observations, identifying statistically supported trends, comparing
geographical behavior, and exploring future projections.

### 3.2 Core user journey

1.  User opens the application and sees an overview of available data
    and featured findings.
2.  User selects a dataset, environmental variable, time interval, and
    supported region or map area.
3.  The system displays historical measurements and metadata.
4.  User runs or views statistical trend analysis.
5.  The system explains trend direction, magnitude, significance,
    uncertainty, and method.
6.  User inspects the geographical distribution of trends where spatial
    data supports it.
7.  User selects a forecast horizon and an evaluated model.
8.  The system displays predictions and uncertainty separately from
    historical observations.
9.  User compares models and their out-of-sample performance.
10. User exports a report or data file with provenance and methodology.

### 3.3 MVP scope

Choose scope only after dataset audit. The default MVP target is:

-   one to three well-supported environmental variables;
-   one or two useful geographic scopes;
-   monthly observations where available and scientifically appropriate;
-   historical time-series explorer;
-   annual/monthly/seasonal summaries where supported;
-   linear trend analysis;
-   Mann-Kendall trend test and Sen's slope where assumptions/data
    support them;
-   at least one baseline and one credible forecasting model;
-   honest chronological evaluation;
-   interactive charts and at least one meaningful geographic
    visualization if spatial data supports it;
-   source attribution and downloadable findings.

Do not force a feature if the supplied data cannot support it. Document
the limitation and choose a defensible alternative.

------------------------------------------------------------------------

## 4. Architecture and technology guidance

Use the existing repository stack if it is sound. Otherwise, the default
architecture is:

### Frontend

-   Next.js / React
-   TypeScript
-   Tailwind CSS
-   Plotly for scientific time-series charts
-   MapLibre GL for interactive maps where appropriate

### Backend

-   Python
-   FastAPI
-   Pydantic request/response schemas
-   Structured logging and explicit error handling

### Scientific/data layer

-   NumPy and Pandas for tabular work
-   Xarray for multidimensional gridded scientific data
-   netCDF4 / h5py / rasterio only where required by actual file formats
-   GeoPandas and Shapely where vector geospatial operations are needed
-   SciPy and Statsmodels for statistical methods
-   pyMannKendall or a validated implementation for Mann-Kendall
    variants
-   Scikit-learn for ML pipelines and evaluation
-   XGBoost only if justified by data volume and performance

### Storage

-   Preserve original source files in a read-only raw-data area.
-   Use NetCDF or Zarr for multidimensional arrays when appropriate.
-   Use Parquet for derived tabular datasets.
-   Use PostgreSQL for application metadata, user selections, job
    records, and report metadata when persistence is needed.
-   Do not put large gridded scientific arrays into relational tables
    without a strong reason.

### Deployment

Choose hosting based on dataset size, compute requirements, budget, and
competition constraints. A static frontend host plus a Python-capable
backend is a reasonable default. Do not assume a free hosting tier can
handle large NetCDF files or expensive spatial calculations.

### Suggested repository structure

Adapt to existing code rather than blindly imposing this exact tree:

``` text
earthscope/
├── frontend/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   └── services/
│   ├── data_pipeline/
│   │   ├── ingestion/
│   │   ├── validation/
│   │   ├── preprocessing/
│   │   └── aggregation/
│   ├── analytics/
│   │   ├── eda/
│   │   ├── trend_detection/
│   │   └── anomaly_detection/
│   ├── ml/
│   │   ├── features/
│   │   ├── training/
│   │   ├── evaluation/
│   │   └── inference/
│   └── tests/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── metadata/
├── notebooks/
├── scripts/
├── docs/
├── tests/
├── .env.example
└── README.md
```

------------------------------------------------------------------------

## 5. Stage-by-stage execution plan

# Stage 0 --- Project initialization and architecture

**Objective:** Establish a reproducible project foundation and module
contracts.

### Tasks

1.  Inspect the existing repository before editing.
2.  Define frontend/backend boundaries.
3.  Establish dependency management and runtime versions.
4.  Configure environment variables and `.env.example`.
5.  Set up linting, formatting, type checking, and tests.
6.  Define shared API conventions and error formats.
7.  Define data/analysis/forecast schemas.
8.  Set up Git conventions and a practical branching strategy.
9.  Create a local development command and document it.
10. Create a minimal health endpoint and frontend connection.

### Required deliverables

-   Working frontend and backend skeleton.
-   Architecture document.
-   Requirements and acceptance document.
-   Dependency manifests and lockfiles where supported.
-   `.env.example` without secrets.
-   Test/lint configuration.
-   `PROJECT_STATUS.md`.

### Acceptance criteria

-   A new developer can follow the README to run the project.
-   Frontend and backend start successfully.
-   Health endpoint returns a valid response.
-   Frontend can call the backend.
-   Tests and lint commands run.
-   No scientific logic is coupled to UI components.

**Gate:** Do not proceed until the development environment is
reproducible.

# Stage 1 --- Dataset discovery and audit

**Objective:** Understand every supplied dataset and determine what
scientific questions it can support.

### Tasks

1.  Inventory every file recursively.
2.  Identify format, size, checksum, and source.
3.  Inspect metadata and schema.
4.  For NetCDF/HDF, inspect dimensions, coordinate variables, data
    variables, time encoding, fill values, units, scale factors, and
    grid metadata.
5.  Determine temporal coverage, sampling frequency, gaps, and irregular
    intervals.
6.  Determine spatial coverage, coordinate reference system, grid
    spacing, and spatial masks.
7.  Inspect missing values, duplicates, invalid values, suspicious
    outliers, and discontinuities.
8.  Identify dataset version changes and processing differences.
9.  Check official source documentation, version notes, licensing, and
    citation guidance.
10. Assess whether datasets can be combined. Do not merge incompatible
    products without a documented scientific rationale.
11. Rank candidate variables by data completeness, relevance to the
    challenge, time coverage, spatial usefulness, and forecast
    feasibility.
12. Recommend a focused MVP.

### Required deliverables

-   `data/metadata/dataset_inventory.csv`
-   `data/metadata/dataset_metadata.json`
-   `docs/data-quality-report.md`
-   `docs/dataset-selection.md`
-   reproducible inspection scripts or notebook.

### Acceptance criteria

-   Every supplied file is accounted for.
-   Variable names, units, dimensions, time and spatial coverage are
    known.
-   Data limitations are documented.
-   Selected MVP variables are justified by actual evidence.
-   No unsupported dataset claims remain.

**Gate:** Stop and request missing datasets if the project references
files that are not accessible. Do not substitute fabricated data.

# Stage 2 --- Data ingestion and preprocessing

**Objective:** Build reusable, reproducible data pipelines.

### Tasks

1.  Implement a loader for each actual file format.
2.  Preserve original raw data unchanged.
3.  Normalize timestamps and calendars carefully. Handle non-standard
    calendars if present.
4.  Preserve coordinates and dimensions in Xarray for gridded datasets.
5.  Standardize variable names through a metadata mapping, not
    destructive renaming.
6.  Maintain units and explicit conversion functions.
7.  Handle fill values and missing observations correctly.
8.  Detect duplicates and irregular timestamps.
9.  Implement variable-appropriate monthly, annual, and seasonal
    aggregation.
10. Implement point, bounding-box, grid-cell, and regional selection as
    supported.
11. Use area-weighted aggregation for latitude-longitude grids when
    spatial averaging requires it.
12. Calculate anomalies against an explicit configurable baseline.
13. Store processed outputs in a suitable efficient format.
14. Record source file, source version, processing configuration,
    timestamp, and transformation history.
15. Add data validation tests.

### Standard observation contract

Use a common logical representation where feasible:

-   `timestamp`
-   `latitude` (nullable if not spatial)
-   `longitude` (nullable if not spatial)
-   `variable_id`
-   `value`
-   `unit`
-   `dataset_id`
-   `source_version`
-   `quality_flag`
-   `aggregation` or temporal resolution

Do not flatten multidimensional arrays unnecessarily. The logical
contract does not require all data to be physically stored as one table.

### Required deliverables

-   Ingestion modules.
-   Validation modules.
-   Preprocessing and aggregation modules.
-   Processed dataset files.
-   Data lineage metadata.
-   Tests and a reproducible pipeline command.

### Acceptance criteria

-   Pipeline runs from raw data to processed data.
-   Repeated runs with the same inputs/configuration give equivalent
    outputs.
-   Units, dimensions, coordinates, and provenance remain traceable.
-   Raw files remain unchanged.
-   Missing values are not silently converted to zero.

**Gate:** The selected dataset must pass documented quality checks
before analysis/model training.

# Stage 3 --- Exploratory data analysis

**Objective:** Understand distributions, seasonal behavior, temporal
changes, and candidate relationships.

### Tasks

1.  Generate descriptive statistics per variable and relevant region.
2.  Plot the full historical series.
3.  Inspect missingness and data availability over time.
4.  Calculate monthly climatology and seasonal cycles where relevant.
5.  Calculate annual and seasonal summaries with scientifically
    appropriate aggregation.
6.  Calculate year-over-year changes.
7.  Examine moving averages without hiding raw observations.
8.  Inspect distributions and extreme values.
9.  Investigate candidate correlations using Pearson or Spearman as
    appropriate.
10. Identify structural breaks, discontinuities, and possible
    instrument/product changes.
11. Document plausible explanations only when supported by sources.
12. Recommend the statistical and forecasting approach for each selected
    variable.

### Required deliverables

-   Reproducible EDA notebooks/scripts.
-   Summary tables.
-   Historical and seasonal plots.
-   Data availability plots.
-   Correlation results where justified.
-   `docs/eda-findings.md`.

### Acceptance criteria

-   Each selected variable has a documented profile.
-   Seasonal and missing-data behavior is understood.
-   Suspicious observations have been investigated.
-   Forecasting assumptions are explicit.
-   No causal claims are inferred from correlation alone.

# Stage 4 --- Statistical trend detection

**Objective:** Implement scientifically defensible historical trend
analysis.

### Methods

1.  Linear regression for a fitted linear rate of change.
2.  Mann-Kendall test for monotonic trend detection where appropriate.
3.  Sen's slope for robust trend magnitude.
4.  Seasonal Mann-Kendall for seasonal series where appropriate.
5.  Autocorrelation diagnostics and suitable correction/modified tests.
6.  Confidence intervals and significance reporting.
7.  Optional anomaly detection as a separate analysis, not a substitute
    for trend testing.

### Tasks

-   Define minimum observation counts and data completeness
    requirements.
-   Define how missing values and irregular sampling are treated.
-   Use actual time coordinates or elapsed time, not arbitrary row
    indices when intervals are irregular.
-   Report slope in interpretable units, e.g. unit/year or unit/decade.
-   Report p-value, confidence interval, method, period, sample count,
    and assumptions.
-   Apply false discovery rate or another justified multiple-testing
    correction for large spatial grids.
-   Separate statistical significance from practical magnitude.
-   Create synthetic test series with known increasing, decreasing,
    stationary, seasonal, and autocorrelated behavior.
-   Validate calculations against a second implementation or trusted
    reference examples.

### Trend result schema

Include, where applicable:

``` json
{
  "dataset_id": "source_dataset_identifier",
  "variable_id": "variable_identifier",
  "unit": "source_unit",
  "region": "region_identifier",
  "period_start": "YYYY-MM-DD",
  "period_end": "YYYY-MM-DD",
  "n_observations": 0,
  "method": "mann_kendall",
  "trend_direction": "increasing | decreasing | no_detected_trend",
  "slope_per_year": null,
  "sen_slope_per_year": null,
  "p_value": null,
  "confidence_interval": {
    "lower": null,
    "upper": null
  },
  "significance_level": 0.05,
  "multiple_testing_adjusted_p_value": null,
  "assumptions": [],
  "limitations": []
}
```

The schema is illustrative. Use null for unavailable values; never fill
with invented values.

### Required deliverables

-   Tested trend-analysis package.
-   Regression and Mann-Kendall methods.
-   Sen's slope and confidence intervals.
-   Seasonal/autocorrelation handling where needed.
-   Spatial multiple-testing procedure where relevant.
-   `docs/statistical-methodology.md`.
-   Validation report and tests.

### Acceptance criteria

-   Known synthetic series produce expected classifications.
-   Results are reproducible and unit-aware.
-   The method and assumptions are disclosed.
-   Large-scale spatial significance is not presented without
    multiplicity considerations.
-   API/UI can distinguish trend magnitude, significance, and practical
    interpretation.

# Stage 5 --- Forecasting and ML

**Objective:** Produce useful, honest out-of-sample forecasts for the
variables and horizons supported by the data.

### 5.1 Define each forecasting task

For each target, document:

-   variable and unit;
-   dataset and source version;
-   region or grid cell;
-   observation frequency;
-   historical coverage;
-   forecast target;
-   horizon;
-   input features;
-   baseline methods;
-   evaluation design;
-   limitations.

Prefer forecasting anomalies or deseasonalized values when this is
scientifically appropriate, but retain the ability to reconstruct and
display the original variable.

### 5.2 Feature engineering

Potential features, only where supported:

-   lagged observations;
-   seasonal lags;
-   rolling means and standard deviations;
-   month/season encodings;
-   trend/time features;
-   other environmental variables available at forecast time.

Prevent target leakage. A feature must be available at the time the
forecast would actually be issued. Future observed covariates cannot be
used unless the scenario explicitly has future covariate forecasts and
their uncertainty is handled.

### 5.3 Model ladder

Start simple and justify complexity:

1.  Persistence baseline.
2.  Seasonal naive baseline.
3.  Drift/linear trend baseline.
4.  ETS or SARIMA.
5.  Tree-based model such as Random Forest or XGBoost with time-series
    features.
6.  LSTM or other deep-learning architecture only if data quantity,
    sampling frequency, and validation justify it.

Do not require every model. Select the smallest set that enables a fair
and informative comparison.

### 5.4 Validation

-   Never randomly shuffle a time series for train/test evaluation.
-   Use chronological holdout and rolling-origin/expanding-window
    validation.
-   Keep preprocessing, scaling, feature selection, and hyperparameter
    fitting inside each training fold.
-   Compare all candidates using identical forecast origins and
    horizons.
-   Evaluate short and longer horizons separately.
-   Compare against naive baselines.
-   Report MAE and RMSE; use MAPE only when mathematically meaningful
    and stable for the target.
-   Consider seasonal metrics or skill scores when useful.
-   Report uncertainty intervals and their empirical coverage where
    possible.
-   Inspect residuals and errors across seasons and regions.
-   Record model configuration, code version, training period, data
    version, and random seed.

### 5.5 Model selection and forecast output

Select the model based on out-of-sample performance, stability,
interpretability, and intended use---not training fit or novelty.

Store: - model identifier and version; - training data range and
source; - feature definition; - forecast origin; - horizon and
frequency; - point predictions; - lower/upper prediction bounds where
available; - evaluation metrics; - known limitations.

Display historical observations, fitted historical values, and future
forecasts as distinct visual series.

### Required deliverables

-   Reproducible training pipeline.
-   Baseline and candidate models.
-   Rolling-origin evaluation.
-   Model comparison report.
-   Saved model artifacts.
-   Inference service.
-   Forecast metadata and uncertainty.
-   `docs/forecasting-methodology.md`.

### Acceptance criteria

-   No temporal leakage.
-   Selected model is compared with credible baselines.
-   Performance is measured out of sample.
-   Predictions are reproducible.
-   Uncertainty and limitations are communicated.
-   If ML fails to beat a baseline, report that honestly and use the
    baseline or revise the task.

# Stage 6 --- Backend API

**Objective:** Expose data discovery, historical observations,
statistical analysis, forecasts, and reports through a stable API.

### Suggested endpoints

-   `GET /api/v1/health`
-   `GET /api/v1/datasets`
-   `GET /api/v1/variables`
-   `GET /api/v1/regions`
-   `GET /api/v1/timeseries`
-   `POST /api/v1/analysis/trend`
-   `POST /api/v1/analysis/anomalies`
-   `POST /api/v1/forecast`
-   `GET /api/v1/models`
-   `GET /api/v1/models/{model_id}/metrics`
-   `GET /api/v1/reports/{report_id}`

Adapt endpoints to the chosen product architecture and actual dataset
capabilities.

### Tasks

-   Define Pydantic request/response models.
-   Validate filters and supported variable/region combinations.
-   Return source and unit metadata with results.
-   Add pagination or downsampling for large time series.
-   Avoid re-running expensive analysis unnecessarily; cache using a key
    that includes dataset version, filters, method, and parameters.
-   Use background jobs for long-running tasks if required.
-   Add structured logs, safe error messages, and request validation.
-   Generate OpenAPI documentation.
-   Add endpoint and service tests.

### Acceptance criteria

-   APIs are documented and independently testable.
-   Invalid filters return clear errors.
-   Responses have stable schemas and units.
-   Long jobs do not block unrelated requests.
-   No fake data is returned in production paths.

# Stage 7 --- Frontend dashboard

**Objective:** Make the scientific system accessible and compelling.

### Core screens

1.  **Overview**
    -   Available datasets and variables.
    -   Data coverage.
    -   Featured, reproducible findings.
    -   Links into investigations.
2.  **Trend Explorer**
    -   Dataset and variable selector.
    -   Region/map selection.
    -   Date range.
    -   Temporal aggregation.
    -   Historical time series.
    -   Trend line and anomaly overlays.
    -   Slope, significance, confidence interval, sample count, units,
        and method.
3.  **Forecast Explorer**
    -   Variable, region, model, and forecast horizon.
    -   Historical observations.
    -   Future prediction.
    -   Prediction interval.
    -   Model comparison and out-of-sample metrics.
    -   Clear forecast-origin marker.
4.  **Geographic Explorer**
    -   Trend direction and magnitude.
    -   Significance/adjusted significance layer.
    -   Region selection and drill-down.
    -   Legend, units, period, and method.
5.  **Investigation/Report**
    -   Question investigated.
    -   Data used.
    -   Methods.
    -   Findings.
    -   Uncertainty and limitations.
    -   Citations and export.

### UX requirements

-   Build a coherent visual system and responsive layout.
-   Prioritize legibility and scientific clarity over decorative
    effects.
-   Use consistent color semantics and accessible contrast.
-   Do not use red/green alone to communicate meaning.
-   Include loading, empty, partial-data, and error states.
-   Make chart axes, units, aggregation, and date ranges explicit.
-   Distinguish actual, fitted, and predicted series.
-   Make all filters functional.
-   Use actual backend results; mock data is permitted only in isolated
    development fixtures and must be clearly labeled.

### Acceptance criteria

-   A user can complete the core investigation without technical
    knowledge.
-   Every chart can be traced to its source and filters.
-   All displayed metrics match backend outputs.
-   Layout works on common desktop and mobile widths.
-   No dead controls or unexplained numbers remain.

# Stage 8 --- Geographic intelligence

**Objective:** Reveal how trends vary spatially, where the dataset
supports spatial analysis.

### Tasks

-   Identify valid spatial dimensions and boundaries.
-   Implement point, region, bounding-box, or grid-cell selection as
    supported.
-   Compute trend metrics per cell or region.
-   Apply multiple-testing correction for large numbers of tests.
-   Preserve spatial masks and missing cells.
-   Generate map-ready layers with documented resolution and projection.
-   Support map click-to-series drill-down.
-   Compare selected regions using consistent time ranges and units.
-   Add clear map legends and explain the meaning of each layer.

### Acceptance criteria

-   Map cells align with correct coordinates.
-   No unsupported interpolation is presented as observation.
-   Spatial significance is treated responsibly.
-   Selecting a map feature loads the corresponding time series and
    analysis.
-   Geographic coverage and resolution are disclosed.

If the supplied datasets do not support maps, do not invent geographic
precision. Provide a clear alternative such as region comparison or a
coverage map.

# Stage 9 --- End-to-end integration

**Objective:** Connect the complete scientific pipeline and product.

### Core workflow test

1.  Load the application.
2.  Discover supported datasets and variables.
3.  Select a variable, time interval, and region.
4.  Retrieve the historical series.
5.  Run trend analysis.
6.  View statistical outputs and methodology.
7.  Generate a forecast.
8.  Compare model metrics and uncertainty.
9.  Inspect the spatial result if available.
10. Export a report or data file.

### Tasks

-   Connect real API services.
-   Replace temporary mocks in production paths.
-   Verify schemas and units across frontend/backend.
-   Handle loading, errors, cancellation, and empty results.
-   Verify caching does not return stale results for different filters.
-   Add integration and end-to-end tests.
-   Profile large-data workflows.

### Acceptance criteria

The complete user journey works using the actual supplied data and
deployed scientific services, without manual notebook execution.

# Stage 10 --- Testing and scientific validation

**Objective:** Establish confidence in the correctness and reliability
of the application.

### Data tests

-   Raw-to-processed reconciliation.
-   Unit conversion tests.
-   Time and coordinate integrity.
-   Aggregation tests.
-   Missing-value handling.
-   Provenance checks.

### Statistical tests

-   Known positive, negative, and stationary synthetic trends.
-   Seasonal series.
-   Autocorrelated series.
-   Confidence interval checks.
-   Multiple-testing checks.
-   Independent implementation/reference comparisons.

### ML tests

-   Chronological split enforcement.
-   Leakage tests.
-   Baseline comparisons.
-   Rolling-origin evaluation.
-   Prediction horizon checks.
-   Prediction interval coverage.
-   Model artifact load/inference tests.

### Product tests

-   API validation.
-   Frontend interaction tests.
-   End-to-end user journey.
-   Accessibility and responsive checks.
-   Error/empty states.
-   Export correctness.
-   Performance and deployment smoke tests.

### Acceptance criteria

All critical tests pass. Scientific outputs are reproducible. Known
limitations are documented. The demo does not rely on unmarked
fabricated results.

# Stage 11 --- Deployment and competition presentation

**Objective:** Deliver a stable, accessible, compelling submission.

### Deployment tasks

-   Configure production settings and secrets.
-   Deploy frontend and backend.
-   Configure storage and CORS safely.
-   Ensure model artifacts and processed data are available.
-   Run production smoke tests.
-   Configure logs and basic monitoring.
-   Provide a seeded, reproducible demonstration scenario.
-   Prepare fallback screenshots/video in case of network failure.

### Submission assets

-   Strong project title and concise description.
-   Problem statement and target users.
-   Solution overview and architecture diagram.
-   Dataset names, source links, versions, and attribution.
-   Scientific methods and assumptions.
-   Model evaluation and limitations.
-   Screenshots and live demo.
-   Short demonstration video/storyboard if required.
-   Setup and reproduction instructions.
-   Team contribution summary based only on actual contributions.

### Demo narrative

Use one real, well-supported investigation:

1.  State a clear Earth-system question.
2.  Select a real variable and region.
3.  Show the source data and historical record.
4.  Reveal the observed trend and statistical evidence.
5.  Compare the same variable across another region if supported.
6.  Show a future forecast with uncertainty and out-of-sample
    performance.
7.  Explain why the result matters and what it cannot prove.

Do not choose the most dramatic result if it is weakly supported. Choose
the clearest scientifically defensible finding.

### Final acceptance criteria

-   Public demo works.
-   Actual data and real computed results are shown.
-   Data provenance is visible.
-   Trend methods and model performance are explained.
-   Limitations are disclosed.
-   Repository and documentation are usable by another developer.
-   Submission assets meet the official challenge requirements.

------------------------------------------------------------------------

## 6. Parallel agent delegation

Use separate agents only where the environment supports parallel work.
Maintain one integration owner/architect.

  -----------------------------------------------------------------------
  Role                    Primary responsibility  Dependencies
  ----------------------- ----------------------- -----------------------
  Architect / Integrator  Architecture,           Stage 0
                          contracts, review,      
                          integration             

  Data Engineer           Dataset audit,          Stages 1--2
                          ingestion,              
                          preprocessing           

  Data Scientist          EDA, descriptive and    Stage 2
                          seasonal analysis       

  Statistical Analyst     Regression,             Stage 2
                          Mann-Kendall, Sen's     
                          slope                   

  ML Engineer             Features, forecasting,  Stages 2--3
                          evaluation              

  Backend Engineer        FastAPI, schemas,       Stage 0 and contracts
                          orchestration           

  Frontend Engineer       Dashboard, charts, maps Stage 0 and API
                                                  contracts

  QA / Release Engineer   Validation, E2E,        Integrated modules
                          deployment              
  -----------------------------------------------------------------------

### Agent collaboration rules

-   The architect owns shared interfaces and resolves conflicts.
-   Each agent owns a clearly bounded directory/module.
-   Agents must not overwrite another agent's work.
-   Agree on schemas before parallel implementation.
-   Frontend can use clearly labeled fixtures while backend is being
    built.
-   Scientific modules must expose deterministic, testable functions.
-   Integrator reviews code and runs tests before merging.
-   Every agent reports files changed, tests run, results, limitations,
    and next steps.
-   Do not claim that an agent completed work that was not inspected or
    tested.

### Required agent handoff template

``` text
ROLE:
STAGE:
OBJECTIVE:

CONTEXT REVIEWED:
INPUTS:
ASSUMPTIONS:

IMPLEMENTATION:
FILES CREATED/CHANGED:
INTERFACES / CONTRACTS:

TESTS RUN:
TEST RESULTS:

ACCEPTANCE CRITERIA:
- [ ] ...
- [ ] ...

LIMITATIONS / RISKS:
BLOCKERS:
NEXT HANDOFF:
```

------------------------------------------------------------------------

## 7. Definition of competition-quality

Before declaring the project ready, score it honestly against this
rubric. The score is an internal readiness tool, not an official NASA
judging score.

  Dimension                                         Weight
  ---------------------------------------------- ---------
  Challenge alignment and problem clarity               15
  Scientific/data correctness                           20
  Meaningful insights and geographic reasoning          15
  Forecasting validity and uncertainty                  10
  User experience and accessibility                     15
  Technical reliability and integration                 10
  Originality and usefulness                             5
  Demo, documentation, and communication                10
  **Total**                                        **100**

For each dimension, record evidence and gaps. Do not inflate scores. Any
critical scientific correctness issue blocks release regardless of total
score.

### Release blockers

Do not call the project complete if any of these remain:

-   Dataset provenance is unknown.
-   Displayed measurements or metrics are fabricated.
-   Units or temporal aggregation are incorrect.
-   Statistical significance is misrepresented.
-   Forecast evaluation has temporal leakage.
-   Model results cannot be reproduced.
-   Forecasts are shown without a clear forecast origin.
-   Map values are spatially misaligned.
-   Core user journey fails.
-   Required official submission elements are missing.

------------------------------------------------------------------------

## 8. Required project documentation

Maintain these documents throughout implementation:

``` text
docs/
├── PROJECT_STATUS.md
├── architecture.md
├── requirements-and-acceptance.md
├── assumptions-and-decisions.md
├── research-sources.md
├── dataset-selection.md
├── data-quality-report.md
├── data-dictionary.md
├── eda-findings.md
├── statistical-methodology.md
├── forecasting-methodology.md
├── model-evaluation.md
├── api-contracts.md
├── testing-and-validation.md
├── limitations.md
├── deployment.md
└── demo-script.md
```

Create documents when their relevant stages begin; do not fill them with
invented content in advance.

------------------------------------------------------------------------

## 9. Final response and progress reporting

At activation, report: - what was found in the repository; - whether
datasets are accessible; - the current stage; - any blockers; - the
first concrete action.

At each stage completion, report: 1. Stage and status. 2. Work
implemented. 3. Important technical/scientific decisions. 4. Files
created or modified. 5. Tests executed and results. 6. Acceptance
criteria passed/failed. 7. Remaining risks. 8. Exact next stage.

At project completion, provide: - deployed URL if deployment
succeeded; - repository status; - supported datasets, variables,
periods, and regions; - statistical methods; - forecasting models and
out-of-sample metrics; - validation evidence; - limitations; - demo
instructions; - competition-readiness score with evidence; - any
remaining release blockers.

Never report success based only on code generation. Inspect the
resulting files, run the application, execute tests, and verify the user
journey wherever tools permit.

------------------------------------------------------------------------

## 10. First action instruction

**Start now.**

Inspect the workspace, repository, official challenge materials, and
attached datasets. Do not begin by generating a generic dashboard or
training an arbitrary model.

Complete Stage 0 and Stage 1 first. If datasets are accessible, audit
them and make evidence-based MVP recommendations. If they are not
accessible, mark Stage 1 `BLOCKED`, state exactly what is missing, and
complete only independent foundation work.

Then proceed through the stage gates in order, implementing and
validating each stage. Keep `docs/PROJECT_STATUS.md` current so another
agent or human teammate can resume the work without reconstructing
context.

**North-star principle:** Build the most scientifically trustworthy and
useful Earth-system trend investigation product that the available data,
time, and compute can support---not the most complicated one.
