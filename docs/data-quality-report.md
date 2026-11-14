# Data Quality & Scientific Audit Report

**Date of Audit:** 2026-11-14  
**Auditor:** EarthScope Data Engineer  
**Scope:** Complete inventory and audit of all supplied datasets in `datasets/`  

---

## 1. Executive Summary

A comprehensive recursive audit was conducted across all files provided in `datasets/`. The dataset collection comprises **19 files** across 5 directories, providing **6 distinct monthly Earth-system physical variables** for Pakistan over a 25-year period (2001–2025).

All 6 datasets were generated via the **NASA GES DISC Giovanni** analytical engine using the Area-Averaged Time Series service (`ArAvTs`), queried across the official US State Department 2017 country polygon for **Pakistan** (`shp_171`, latitude 23.31°N–37.69°N, longitude 60.39°E–77.73°E).

### Audit Verdict: **EXCELLENT / PRODUCTION-READY**
- **Completeness:** 100% data presence (0 missing points or gaps across all series during active periods).
- **Temporal Consistency:** Strict monthly cadence (28–31 day intervals, 0 irregular timestamps or duplicate records).
- **Physical Validity:** All values reside within physically realistic atmospheric and hydrologic bounds.
- **Cross-variable Alignment:** Complete 297-month overlap across all 6 variables (January 2001 – September 2025), with 3 variables extending to December 2025 (300 months).

---

## 2. File Inventory & Integrity

| Variable ID | Physical Variable | Model / Source | Format | Size (Bytes) | SHA-256 (CSV) |
|---|---|---|---|---|---|
| `t2m` | 2-Meter Air Temperature | MERRA-2 (M2TMNXSLV v5.12.4) | CSV, NC, PNG | 9,856 | `6973005b...` |
| `ts` | Surface Skin Temperature | MERRA-2 (M2TMNXSLV v5.12.4) | CSV, NC, PNG | 9,842 | `5f6e0886...` |
| `precipitation` | Bias-Corrected Precipitation | MERRA-2 (M2TMNXFLX v5.12.4) | CSV, NC, PNG | 10,967 | `d1ede233...` |
| `evapotranspiration` | Total Evapotranspiration | GLDAS Noah LSM L4 v2.1 | CSV, NC, PNG | 11,121 | `7084ac3c...` |
| `soil_moisture_0_10cm` | Topsoil Moisture (0–10 cm) | GLDAS Noah LSM L4 v2.1 | CSV, NC, PNG | 9,876 | `2afd5b08...` |
| `soil_moisture_10_40cm`| Rootzone Moisture (10–40 cm) | GLDAS Noah LSM L4 v2.1 | CSV, NC, PNG | 9,866 | `4ed38bef...` |

*(Full SHA-256 signatures for every file are cataloged in `data/metadata/dataset_inventory.csv`)*

---

## 3. Variable-by-Variable Profile & Data Integrity

### 3.1 2-Meter Air Temperature (`t2m`)
- **Source Mission / Model:** NASA GMAO MERRA-2 Reanalysis (`M2TMNXSLV_5_12_4_T2M`).
- **Nominal Unit:** Kelvin ($K$).
- **Display Unit:** Degrees Celsius ($^\circ\text{C}$ where $^\circ\text{C} = K - 273.15$).
- **Observation Range:** 2001-01-01 to 2025-12-01 (300 months, 25 full years).
- **Data Completeness:** 300 / 300 valid records (0 missing values, 0% missingness).
- **Statistics (Kelvin):**
  - Minimum: $279.52\text{ K}$ ($6.37^\circ\text{C}$, typically January).
  - Maximum: $304.34\text{ K}$ ($31.19^\circ\text{C}$, typically June).
  - Mean: $294.28\text{ K}$ ($21.13^\circ\text{C}$).
  - Standard Deviation: $7.57\text{ K}$.
- **Fill Value:** Declared as $1.0 \times 10^{15}$; no occurrences in data.

### 3.2 Surface Skin Temperature (`ts`)
- **Source Mission / Model:** NASA GMAO MERRA-2 Reanalysis (`M2TMNXSLV_5_12_4_TS`).
- **Nominal Unit:** Kelvin ($K$).
- **Display Unit:** Degrees Celsius ($^\circ\text{C}$).
- **Observation Range:** 2001-01-01 to 2025-12-01 (300 months).
- **Data Completeness:** 300 / 300 valid records (0% missingness).
- **Statistics (Kelvin):**
  - Minimum: $278.78\text{ K}$ ($5.63^\circ\text{C}$).
  - Maximum: $307.06\text{ K}$ ($33.91^\circ\text{C}$).
  - Mean: $295.09\text{ K}$ ($21.94^\circ\text{C}$).
  - Standard Deviation: $8.86\text{ K}$.
- **Physical Consistency Check:** Surface skin temperature displays higher seasonal variance ($\text{std} = 8.86\text{ K}$) than 2-meter air temperature ($\text{std} = 7.57\text{ K}$), consistent with physical land-surface thermodynamic principles.

### 3.3 Bias-Corrected Precipitation (`precipitation`)
- **Source Mission / Model:** NASA GMAO MERRA-2 Reanalysis (`M2TMNXFLX_5_12_4_PRECTOTCORR`).
- **Nominal Unit:** $\text{kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1}$.
- **Display Unit:** $\text{mm/day}$ ($1\text{ kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1} = 86,400\text{ mm/day}$) or $\text{mm/month}$.
- **Observation Range:** 2001-01-01 to 2025-09-01 (297 months).
- **Data Completeness:** 297 / 297 valid records (0% missingness).
- **Statistics ($\text{kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1}$):**
  - Minimum: $1.34 \times 10^{-8}$ ($\sim 0.001\text{ mm/day}$).
  - Maximum: $9.49 \times 10^{-5}$ ($\sim 8.20\text{ mm/day}$, representing major monsoon flooding months, including August 2022).
  - Mean: $1.03 \times 10^{-5}$ ($\sim 0.89\text{ mm/day}$).
  - Standard Deviation: $1.19 \times 10^{-5}$.
- **Sanity Check:** Strong monsoon spikes visible in July–August each year, matching Pakistan's climatology.

### 3.4 Total Evapotranspiration Flux (`evapotranspiration`)
- **Source Mission / Model:** NASA GSFC / NOAA GLDAS Noah Land Surface Model v2.1 (`GLDAS_NOAH10_M_2_1_Evap_tavg`).
- **Nominal Unit:** $\text{kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1}$.
- **Display Unit:** $\text{mm/day}$ or $\text{mm/month}$.
- **Observation Range:** 2001-01-01 to 2025-12-01 (300 months).
- **Data Completeness:** 300 / 300 valid records (0% missingness).
- **Statistics ($\text{kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1}$):**
  - Minimum: $1.71 \times 10^{-6}$ ($\sim 0.15\text{ mm/day}$).
  - Maximum: $3.20 \times 10^{-5}$ ($\sim 2.76\text{ mm/day}$).
  - Mean: $1.00 \times 10^{-5}$ ($\sim 0.87\text{ mm/day}$).
  - Standard Deviation: $5.91 \times 10^{-6}$.
- **Fill Value:** Declared as $-9999.0$; no occurrences in data.

### 3.5 Topsoil Moisture 0–10 cm (`soil_moisture_0_10cm`)
- **Source Mission / Model:** GLDAS Noah LSM L4 v2.1 (`SoilMoi0_10cm_inst`).
- **Nominal Unit:** $\text{kg}\cdot\text{m}^{-2}$ (equivalent to mm of water depth in top 100 mm soil column).
- **Observation Range:** 2001-01-01 to 2025-09-01 (297 months).
- **Data Completeness:** 297 / 297 valid records (0% missingness).
- **Statistics ($\text{kg}\cdot\text{m}^{-2}$):**
  - Minimum: $10.89\text{ kg}\cdot\text{m}^{-2}$ ($\sim 10.9\%$ volumetric equivalent).
  - Maximum: $28.00\text{ kg}\cdot\text{m}^{-2}$.
  - Mean: $16.97\text{ kg}\cdot\text{m}^{-2}$.
  - Standard Deviation: $3.03\text{ kg}\cdot\text{m}^{-2}$.

### 3.6 Rootzone Soil Moisture 10–40 cm (`soil_moisture_10_40cm`)
- **Source Mission / Model:** GLDAS Noah LSM L4 v2.1 (`SoilMoi10_40cm_inst`).
- **Nominal Unit:** $\text{kg}\cdot\text{m}^{-2}$ (in 300 mm soil column).
- **Observation Range:** 2001-01-01 to 2025-09-01 (297 months).
- **Data Completeness:** 297 / 297 valid records (0% missingness).
- **Statistics ($\text{kg}\cdot\text{m}^{-2}$):**
  - Minimum: $53.95\text{ kg}\cdot\text{m}^{-2}$.
  - Maximum: $87.66\text{ kg}\cdot\text{m}^{-2}$.
  - Mean: $65.72\text{ kg}\cdot\text{m}^{-2}$.
  - Standard Deviation: $5.13\text{ kg}\cdot\text{m}^{-2}$.

---

## 4. Scientific Feasibility and Coupling Assessment

Because these 6 variables describe the exact same region over identical monthly periods, they form a **closed Earth-system hydrometeorological cycle**:
1. **Atmosphere $\rightarrow$ Surface:** Solar radiation drives Air & Skin Temperature.
2. **Atmosphere $\rightarrow$ Soil:** Precipitation fluxes infiltrate into the top 10 cm and percolate to the 10–40 cm root zone.
3. **Soil $\rightarrow$ Atmosphere:** Soil moisture combined with surface heat drives Evapotranspiration back into the atmosphere.

This provides an exceptional foundation for multi-variable trend investigation and forecasting.

---

## 5. Documented Limitations

1. **Spatial Aggregation:** All data are area-averaged over the national polygon of Pakistan (`shp_171`). Sub-regional spatial microclimates (such as the Karakoram glaciated north versus the arid Balochistan plateau) cannot be extracted from these specific area-averaged files. The application will explicitly inform users that metrics reflect national territorial area-averages.
2. **Temporal Cutoff Differences:** MERRA-2 precipitation and GLDAS soil moisture currently end in September 2025 (297 months), whereas MERRA-2 temperature and GLDAS evapotranspiration extend through December 2025 (300 months). In multi-variable modeling, the shared overlapping window (2001-01 to 2025-09, 297 months) must be used.
