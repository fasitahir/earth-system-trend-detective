/**
 * EarthScope API Client & Types
 *
 * Provides typed methods to interact with the EarthScope FastAPI backend.
 * Includes graceful fallback fixtures from audited dataset metadata if the
 * local API server is temporarily unreachable.
 */

export interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy" | "disconnected";
  project_name: string;
  version: string;
  environment: string;
  timestamp: string;
  components?: Record<string, any>;
}

export interface VariableMeta {
  id: string;
  name: string;
  source_variable_name: string;
  category: string;
  unit: string;
  display_unit: string;
  mission_source: string;
  description: string;
  frequency: string;
  start_date: string;
  end_date: string;
  total_months: number;
  region: string;
}

export interface DatasetMeta {
  id: string;
  title: string;
  platform: string;
  spatial_resolution: string;
  temporal_resolution: string;
  variables: VariableMeta[];
  citation: string;
  giovanni_url?: string | null;
}

export interface ObservationPoint {
  timestamp: string;
  value: number;
  display_value?: number;
  anomaly?: number;
}

export interface TimeSeriesSummary {
  count: number;
  mean: number;
  std: number;
  min: number;
  max: number;
  median: number;
}

export interface TimeSeriesResponse {
  variable_id: string;
  variable_name: string;
  unit: string;
  display_unit: string;
  region: string;
  start_date: string;
  end_date: string;
  summary: TimeSeriesSummary;
  data: ObservationPoint[];
  downsampled: boolean;
  stride: number;
}

export interface ConfidenceInterval {
  lower?: number | null;
  upper?: number | null;
}

export interface TrendResponse {
  dataset_id: string;
  variable_id: string;
  unit: string;
  display_unit: string;
  region: string;
  period_start: string;
  period_end: string;
  n_observations: number;
  method: string;
  trend_direction: "increasing" | "decreasing" | "no_detected_trend";
  slope_per_year?: number | null;
  sen_slope_per_year?: number | null;
  p_value?: number | null;
  confidence_interval: ConfidenceInterval;
  significance_level: number;
  is_statistically_significant: boolean;
  multiple_testing_adjusted_p_value?: number | null;
  assumptions: string[];
  limitations: string[];
}

export interface ForecastPoint {
  timestamp: string;
  predicted_value: number;
  lower_bound?: number | null;
  upper_bound?: number | null;
}

export interface ModelEvaluationMetrics {
  model_id: string;
  model_name: string;
  mae: number;
  rmse: number;
  r2_score?: number | null;
  test_observations: number;
  is_baseline: boolean;
  skill_score_vs_seasonal_naive?: number | null;
}

export interface ForecastResponse {
  variable_id: string;
  unit: string;
  region: string;
  forecast_origin: string;
  horizon_months: number;
  model_id: string;
  model_name: string;
  metrics: ModelEvaluationMetrics;
  predictions: ForecastPoint[];
  limitations: string[];
  artifact_loaded: boolean;
  trained_on?: string | null;
}

export interface SavedModelSummary {
  model_id: string;
  model_name: string;
  is_baseline: boolean;
  variables: string[];
  recommended_for: string[];
}

export interface ModelCatalogResponse {
  models: SavedModelSummary[];
  saved_variables: string[];
  artifact_dir: string;
}

export interface AnomalyRecord {
  timestamp: string;
  value: number;
  anomaly: number;
  z_score?: number | null;
}

export interface AnomalyResponse {
  variable_id: string;
  unit: string;
  display_unit: string;
  region: string;
  top_positive_anomalies: AnomalyRecord[];
  top_negative_anomalies: AnomalyRecord[];
  method: string;
}

export interface ReportSummary {
  report_id: string;
  title: string;
  path: string;
  description: string;
}

export interface ReportDetailResponse extends ReportSummary {
  excerpt: string;
}

export interface BoundingBox {
  lat_min: number;
  lat_max: number;
  lon_min: number;
  lon_max: number;
}

export interface RegionMeta {
  id: string;
  name: string;
  spatial_representation: string;
  bounding_coordinates: BoundingBox;
  note: string;
  variable_ids: string[];
}

export interface EcologicalZone {
  id: string;
  name: string;
  description: string;
  climate_classification: string;
  lat_center: number;
  lon_center: number;
  approx_elevation_m: string;
  vulnerability_profile: string;
}

export interface SpatialTrendLayer {
  variable_id: string;
  variable_name: string;
  display_unit: string;
  sen_slope_per_decade: number;
  p_value: number;
  is_significant: boolean;
  fdr_adjusted_p_value: number;
  trend_direction: string;
  spatial_scope: string;
}

export interface SpatialSummaryResponse {
  region_id: string;
  region_name: string;
  projection: string;
  spatial_representation: string;
  bounding_box: BoundingBox;
  polygon_id: string;
  native_grid_resolutions: Record<string, string>;
  zones: EcologicalZone[];
  variable_trends: SpatialTrendLayer[];
  multiple_testing_correction: string;
  limitations: string[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Fallback metadata fixtures based on audited datasets
export const FALLBACK_VARIABLES: VariableMeta[] = [
  {
    id: "t2m",
    name: "2-Meter Air Temperature",
    source_variable_name: "mean_M2TMNXSLV_5_12_4_T2M",
    category: "Atmosphere",
    unit: "K",
    display_unit: "°C",
    mission_source: "NASA MERRA-2 (M2TMNXSLV v5.12.4)",
    description: "Monthly area-averaged 2-meter air temperature over Pakistan.",
    frequency: "monthly",
    start_date: "2001-01-01",
    end_date: "2025-12-01",
    total_months: 300,
    region: "Pakistan",
  },
  {
    id: "ts",
    name: "Surface Skin Temperature",
    source_variable_name: "mean_M2TMNXSLV_5_12_4_TS",
    category: "Atmosphere / Land Surface",
    unit: "K",
    display_unit: "°C",
    mission_source: "NASA MERRA-2 (M2TMNXSLV v5.12.4)",
    description: "Monthly area-averaged land surface skin temperature.",
    frequency: "monthly",
    start_date: "2001-01-01",
    end_date: "2025-12-01",
    total_months: 300,
    region: "Pakistan",
  },
  {
    id: "precipitation",
    name: "Bias-Corrected Precipitation",
    source_variable_name: "mean_M2TMNXFLX_5_12_4_PRECTOTCORR",
    category: "Hydrology",
    unit: "kg m-2 s-1",
    display_unit: "mm/month",
    mission_source: "NASA MERRA-2 (M2TMNXFLX v5.12.4)",
    description: "Monthly total bias-corrected surface precipitation.",
    frequency: "monthly",
    start_date: "2001-01-01",
    end_date: "2025-09-01",
    total_months: 297,
    region: "Pakistan",
  },
  {
    id: "evapotranspiration",
    name: "Total Evapotranspiration",
    source_variable_name: "mean_GLDAS_NOAH025_M_2_1_Evap_tavg",
    category: "Hydrosphere / Land Surface",
    unit: "kg m-2 s-1",
    display_unit: "mm/month",
    mission_source: "NASA GLDAS-2.1 Noah",
    description: "Monthly area-averaged total evapotranspiration flux.",
    frequency: "monthly",
    start_date: "2001-01-01",
    end_date: "2025-12-01",
    total_months: 300,
    region: "Pakistan",
  },
  {
    id: "soil_moisture_0_10cm",
    name: "Topsoil Moisture (0-10 cm)",
    source_variable_name: "mean_GLDAS_NOAH025_M_2_1_SoilMoi0_10cm_tavg",
    category: "Hydrosphere",
    unit: "kg m-2",
    display_unit: "kg/m²",
    mission_source: "NASA GLDAS-2.1 Noah",
    description: "Volumetric topsoil layer moisture content.",
    frequency: "monthly",
    start_date: "2001-01-01",
    end_date: "2025-09-01",
    total_months: 297,
    region: "Pakistan",
  },
  {
    id: "soil_moisture_10_40cm",
    name: "Rootzone Soil Moisture (10-40 cm)",
    source_variable_name: "mean_GLDAS_NOAH025_M_2_1_SoilMoi10_40cm_tavg",
    category: "Hydrosphere",
    unit: "kg m-2",
    display_unit: "kg/m²",
    mission_source: "NASA GLDAS-2.1 Noah",
    description: "Subsurface root-zone moisture reservoir.",
    frequency: "monthly",
    start_date: "2001-01-01",
    end_date: "2025-09-01",
    total_months: 297,
    region: "Pakistan",
  },
];

export const FALLBACK_TRENDS: Record<string, Partial<TrendResponse>> = {
  t2m: {
    variable_id: "t2m",
    unit: "°C",
    display_unit: "°C/decade",
    region: "Pakistan",
    n_observations: 300,
    period_start: "2001-01-01",
    period_end: "2025-12-01",
    method: "modified_mann_kendall_yue_pilon",
    trend_direction: "no_detected_trend",
    sen_slope_per_year: -0.0158,
    p_value: 0.057,
    is_statistically_significant: false,
    confidence_interval: { lower: -0.033, upper: 0.001 },
  },
  ts: {
    variable_id: "ts",
    unit: "°C",
    display_unit: "°C/decade",
    region: "Pakistan",
    n_observations: 300,
    period_start: "2001-01-01",
    period_end: "2025-12-01",
    method: "modified_mann_kendall_yue_pilon",
    trend_direction: "decreasing",
    sen_slope_per_year: -0.0255,
    p_value: 0.0037,
    is_statistically_significant: true,
    confidence_interval: { lower: -0.0446, upper: -0.0066 },
  },
  precipitation: {
    variable_id: "precipitation",
    unit: "mm/month",
    display_unit: "mm/month/decade",
    region: "Pakistan",
    n_observations: 297,
    period_start: "2001-01-01",
    period_end: "2025-09-01",
    method: "modified_mann_kendall_yue_pilon",
    trend_direction: "increasing",
    sen_slope_per_year: 0.729,
    p_value: 0.0001,
    is_statistically_significant: true,
    confidence_interval: { lower: 0.525, upper: 0.949 },
  },
  evapotranspiration: {
    variable_id: "evapotranspiration",
    unit: "mm/month",
    display_unit: "mm/month/decade",
    region: "Pakistan",
    n_observations: 300,
    period_start: "2001-01-01",
    period_end: "2025-12-01",
    method: "modified_mann_kendall_yue_pilon",
    trend_direction: "increasing",
    sen_slope_per_year: 0.332,
    p_value: 0.0001,
    is_statistically_significant: true,
    confidence_interval: { lower: 0.215, upper: 0.448 },
  },
  soil_moisture_0_10cm: {
    variable_id: "soil_moisture_0_10cm",
    unit: "kg/m²",
    display_unit: "kg/m²/decade",
    region: "Pakistan",
    n_observations: 297,
    period_start: "2001-01-01",
    period_end: "2025-09-01",
    method: "modified_mann_kendall_yue_pilon",
    trend_direction: "increasing",
    sen_slope_per_year: 0.106,
    p_value: 0.0001,
    is_statistically_significant: true,
    confidence_interval: { lower: 0.066, upper: 0.145 },
  },
  soil_moisture_10_40cm: {
    variable_id: "soil_moisture_10_40cm",
    unit: "kg/m²",
    display_unit: "kg/m²/decade",
    region: "Pakistan",
    n_observations: 297,
    period_start: "2001-01-01",
    period_end: "2025-09-01",
    method: "modified_mann_kendall_yue_pilon",
    trend_direction: "increasing",
    sen_slope_per_year: 0.197,
    p_value: 0.0001,
    is_statistically_significant: true,
    confidence_interval: { lower: 0.130, upper: 0.264 },
  },
};

/**
 * Universal JSON fetch helper with timeout and friendly error responses.
 */
async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 12000);

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      let errMsg = `HTTP ${res.status}: ${res.statusText}`;
      try {
        const errorJson = await res.json();
        if (errorJson.message) errMsg = errorJson.message;
        else if (errorJson.detail) errMsg = typeof errorJson.detail === "string" ? errorJson.detail : JSON.stringify(errorJson.detail);
      } catch {
        // ignore json parse error
      }
      throw new Error(errMsg);
    }

    return await res.json();
  } catch (err: any) {
    clearTimeout(timeoutId);
    throw err;
  }
}

/**
 * Health status probe.
 */
export async function fetchHealth(): Promise<HealthStatus> {
  return fetchJson<HealthStatus>("/api/v1/health");
}

/**
 * Dataset catalog retrieval.
 */
export async function fetchDatasets(): Promise<{ datasets: DatasetMeta[]; total_variables: number }> {
  return fetchJson<{ datasets: DatasetMeta[]; total_variables: number }>("/api/v1/datasets");
}

/**
 * Variables catalog retrieval.
 */
export async function fetchVariables(): Promise<{ variables: VariableMeta[]; total_variables: number }> {
  return fetchJson<{ variables: VariableMeta[]; total_variables: number }>("/api/v1/variables");
}

/**
 * Regions catalog retrieval.
 */
export async function fetchRegions(): Promise<{ regions: RegionMeta[]; total_regions: number }> {
  return fetchJson<{ regions: RegionMeta[]; total_regions: number }>("/api/v1/regions");
}

/**
 * Time series query.
 */
export async function fetchTimeSeries(params: {
  variable_id: string;
  start_date?: string;
  end_date?: string;
  max_points?: number;
}): Promise<TimeSeriesResponse> {
  const query = new URLSearchParams();
  query.append("variable_id", params.variable_id);
  if (params.start_date) query.append("start_date", params.start_date);
  if (params.end_date) query.append("end_date", params.end_date);
  if (params.max_points) query.append("max_points", params.max_points.toString());

  return fetchJson<TimeSeriesResponse>(`/api/v1/timeseries?${query.toString()}`);
}

/**
 * Statistical trend analysis.
 */
export async function fetchTrend(params: {
  variable_id: string;
  method?: string;
  start_date?: string;
  end_date?: string;
  alpha?: number;
  deseasonalize?: boolean;
}): Promise<TrendResponse> {
  return fetchJson<TrendResponse>("/api/v1/analysis/trend", {
    method: "POST",
    body: JSON.stringify({
      variable_id: params.variable_id,
      method: params.method || "mann_kendall",
      start_date: params.start_date || null,
      end_date: params.end_date || null,
      alpha: params.alpha ?? 0.05,
      deseasonalize: params.deseasonalize ?? true,
    }),
  });
}

/**
 * Extreme anomaly analysis.
 */
export async function fetchAnomalies(params: {
  variable_id: string;
  top_n?: number;
  start_date?: string;
  end_date?: string;
}): Promise<AnomalyResponse> {
  return fetchJson<AnomalyResponse>("/api/v1/analysis/anomalies", {
    method: "POST",
    body: JSON.stringify({
      variable_id: params.variable_id,
      top_n: params.top_n ?? 5,
      start_date: params.start_date || null,
      end_date: params.end_date || null,
    }),
  });
}

/**
 * Out-of-sample forecast generation.
 */
export async function fetchForecast(params: {
  variable_id: string;
  horizon_months?: number;
  model_id?: string;
  confidence_level?: number;
}): Promise<ForecastResponse> {
  return fetchJson<ForecastResponse>("/api/v1/forecast", {
    method: "POST",
    body: JSON.stringify({
      variable_id: params.variable_id,
      horizon_months: params.horizon_months ?? 12,
      model_id: params.model_id ?? "ridge_lag",
      confidence_level: params.confidence_level ?? 0.95,
    }),
  });
}

/**
 * Forecasting models catalog.
 */
export async function fetchModels(): Promise<ModelCatalogResponse> {
  return fetchJson<ModelCatalogResponse>("/api/v1/models");
}

/**
 * Out-of-sample model evaluation metrics.
 */
export async function fetchModelMetrics(modelId: string): Promise<any> {
  return fetchJson<any>(`/api/v1/models/${encodeURIComponent(modelId)}/metrics`);
}

/**
 * Read-only scientific reports list.
 */
export async function fetchReports(): Promise<{ reports: ReportSummary[] }> {
  return fetchJson<{ reports: ReportSummary[] }>("/api/v1/reports");
}

/**
 * Report excerpt/detail.
 */
export async function fetchReportDetail(reportId: string): Promise<ReportDetailResponse> {
  return fetchJson<ReportDetailResponse>(`/api/v1/reports/${encodeURIComponent(reportId)}`);
}

export const FALLBACK_SPATIAL_SUMMARY: SpatialSummaryResponse = {
  region_id: "pakistan",
  region_name: "Pakistan",
  projection: "EPSG:4326 (WGS 84)",
  spatial_representation: "Area-averaged country polygon (State Dept 2017 shp_171)",
  bounding_box: {
    lat_min: 23.3125,
    lat_max: 37.6875,
    lon_min: 60.390625,
    lon_max: 77.734375,
  },
  polygon_id: "state_dept_countries_2017/shp_171",
  native_grid_resolutions: {
    "MERRA-2 Atmospheric Reanalysis": "0.5° latitude × 0.625° longitude (~50 km × 60 km)",
    "GLDAS-2.1 Noah Land Surface Model": "0.25° latitude × 0.25° longitude (~25 km × 25 km)",
  },
  zones: [
    {
      id: "northern_highlands",
      name: "Northern Highlands & Glacial Basins",
      description: "Glaciated alpine headwaters of the Indus River basin encompassing Karakoram, Himalayas, and Hindu Kush.",
      climate_classification: "Alpine Tundra / Glacial (ET / EF)",
      lat_center: 35.8,
      lon_center: 74.8,
      approx_elevation_m: "2,000 – 8,611 m",
      vulnerability_profile: "Accelerated cryosphere retreat, glacial lake outburst floods (GLOFs), and snowline shifts.",
    },
    {
      id: "upper_indus",
      name: "Upper Indus Agricultural Plain",
      description: "Alluvial agricultural heartland of Punjab with dense canal irrigation networks and high biomass productivity.",
      climate_classification: "Semi-Arid Subtropical (BSh / Cwa)",
      lat_center: 31.5,
      lon_center: 73.2,
      approx_elevation_m: "150 – 350 m",
      vulnerability_profile: "Evaporative demand stress, intense pre-monsoon heatwaves, and seasonal aquifer overdraft.",
    },
    {
      id: "lower_indus",
      name: "Lower Indus Basin & Delta",
      description: "Flat alluvial basin terminating in the Indus Delta and Arabian Sea coastal lagoons in Sindh.",
      climate_classification: "Hyper-Arid Lowland (BWh)",
      lat_center: 26.2,
      lon_center: 68.6,
      approx_elevation_m: "10 – 150 m",
      vulnerability_profile: "Monsoon pluvial inundation (e.g. 2022 catastrophe), coastal saltwater intrusion, and soil waterlogging.",
    },
    {
      id: "western_plateau",
      name: "Western Arid Plateaus & Ranges",
      description: "Rugged highland plateaus and desert basins across Balochistan and Sulaiman mountain ranges.",
      climate_classification: "Cold / Hot Arid Desert (BWk / BWh)",
      lat_center: 28.6,
      lon_center: 65.4,
      approx_elevation_m: "500 – 2,200 m",
      vulnerability_profile: "Protracted meteorological droughts, depleted karez/groundwater reserves, and flash floods.",
    },
    {
      id: "coastal_zone",
      name: "Arabian Sea Coastal Belt",
      description: "Marine-coastal littoral interface stretching 1,050 km along Makran and Sindh shorelines.",
      climate_classification: "Coastal Semi-Arid / Marine (BSh)",
      lat_center: 24.8,
      lon_center: 66.8,
      approx_elevation_m: "0 – 50 m",
      vulnerability_profile: "Tropical cyclonic storm surges, extreme wet-bulb temperatures, and coastal sea-level rise.",
    },
  ],
  variable_trends: [
    {
      variable_id: "t2m",
      variable_name: "2-Meter Air Temperature",
      display_unit: "°C/decade",
      sen_slope_per_decade: -0.1576,
      p_value: 0.057176,
      is_significant: false,
      fdr_adjusted_p_value: 0.057176,
      trend_direction: "no_detected_trend",
      spatial_scope: "Pakistan National Area-Average (shp_171)",
    },
    {
      variable_id: "ts",
      variable_name: "Surface Skin Temperature",
      display_unit: "°C/decade",
      sen_slope_per_decade: -0.2546,
      p_value: 0.003706,
      is_significant: true,
      fdr_adjusted_p_value: 0.004447,
      trend_direction: "decreasing",
      spatial_scope: "Pakistan National Area-Average (shp_171)",
    },
    {
      variable_id: "precipitation",
      variable_name: "Total Precipitation",
      display_unit: "mm/month/decade",
      sen_slope_per_decade: 7.2895,
      p_value: 0.000001,
      is_significant: true,
      fdr_adjusted_p_value: 0.000006,
      trend_direction: "increasing",
      spatial_scope: "Pakistan National Area-Average (shp_171)",
    },
    {
      variable_id: "evapotranspiration",
      variable_name: "Total Evapotranspiration",
      display_unit: "mm/month/decade",
      sen_slope_per_decade: 3.3163,
      p_value: 0.000001,
      is_significant: true,
      fdr_adjusted_p_value: 0.000006,
      trend_direction: "increasing",
      spatial_scope: "Pakistan National Area-Average (shp_171)",
    },
    {
      variable_id: "soil_moisture_0_10cm",
      variable_name: "Topsoil Moisture (0-10 cm)",
      display_unit: "kg/m²/decade",
      sen_slope_per_decade: 1.0634,
      p_value: 0.000001,
      is_significant: true,
      fdr_adjusted_p_value: 0.000006,
      trend_direction: "increasing",
      spatial_scope: "Pakistan National Area-Average (shp_171)",
    },
    {
      variable_id: "soil_moisture_10_40cm",
      variable_name: "Rootzone Moisture (10-40 cm)",
      display_unit: "kg/m²/decade",
      sen_slope_per_decade: 1.9711,
      p_value: 0.000001,
      is_significant: true,
      fdr_adjusted_p_value: 0.000006,
      trend_direction: "increasing",
      spatial_scope: "Pakistan National Area-Average (shp_171)",
    },
  ],
  multiple_testing_correction: "Benjamini-Hochberg False Discovery Rate (FDR) at alpha = 0.05 across all 6 Earth system variables",
  limitations: [
    "Supplied NASA Giovanni extracts are pre-computed area-averaged series over Pakistan country boundary (shp_171).",
    "Spatial variation is described via ecological zones; artificial pixel interpolation is strictly excluded to preserve observational integrity.",
    "MERRA-2 reanalysis (0.5°x0.625°) and GLDAS-2.1 (0.25°x0.25°) spatial resolutions are documented without synthetic downscaling.",
  ],
};

/**
 * Geographic intelligence & spatial summary retrieval.
 */
export async function fetchSpatialSummary(): Promise<SpatialSummaryResponse> {
  return fetchJson<SpatialSummaryResponse>("/api/v1/spatial/summary");
}

