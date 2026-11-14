# Dataset Selection & MVP Scope Recommendation

**Project:** EarthScope (NASA Space Apps Challenge 2026)  
**Document:** Dataset Selection & MVP Justification  
**Date:** 2026-11-14  

---

## 1. Candidate Variable Ranking

Based on the evidence from the Stage 1 audit of `datasets/`, all 6 candidate variables were evaluated against five criteria:
1. **Data Completeness:** Absence of missing observations or gaps.
2. **Challenge Alignment:** Direct relevance to detecting Earth-system trends.
3. **Temporal Coverage:** Multi-decadal duration for statistical power.
4. **Physical Interpretability:** Clarity of units, physical meaning, and public relevance.
5. **Forecast Feasibility:** Predictable seasonal structure and cross-variable interactions.

| Rank | Variable ID | Completeness | Coverage | Challenge Relevance | Forecast Feasibility | Recommended Role |
|---|---|---|---|---|---|---|
| **1** | `t2m` (2m Air Temp) | 100% (300/300) | 2001–2025 | Very High (Thermal trend) | High (Strong seasonal cycle) | **Core MVP Target** |
| **2** | `precipitation` | 100% (297/297) | 2001–2025 | Very High (Monsoon extremes) | Moderate (High variance) | **Core MVP Target** |
| **3** | `soil_moisture_0_10cm` | 100% (297/297) | 2001–2025 | High (Drought/Flood indicator) | High (Memory/Autocorrelation) | **Core MVP Target** |
| **4** | `evapotranspiration` | 100% (300/300) | 2001–2025 | High (Land-atmosphere coupling)| High (Strong seasonal cycle) | Secondary / Correlative |
| **5** | `ts` (Surface Skin Temp) | 100% (300/300) | 2001–2025 | High (Surface heat balance) | High (Parallel to T2M) | Secondary / Comparative |
| **6** | `soil_moisture_10_40cm`| 100% (297/297) | 2001–2025 | Medium-High (Subsurface storage)| High (Inertial dynamics) | Secondary / Deep storage |

---

## 2. Recommended MVP Scope

Rather than dropping any of the supplied variables, EarthScope will integrate **all 6 variables** into a cohesive **Earth System Hydrometeorological Suite** for Pakistan, grouped into three complementary diagnostic modules:

### Module A: Atmospheric & Thermal Trends
- **Primary:** `t2m` (2-Meter Air Temperature, Kelvin $\rightarrow$ °C).
- **Secondary:** `ts` (Surface Skin Temperature, Kelvin $\rightarrow$ °C).
- **Scientific Question:** *Is Pakistan experiencing statistically significant warming over the 2001–2025 period, and does surface heating outpace atmospheric air temperature?*

### Module B: Hydro-Climatic Fluxes & Monsoon Extremes
- **Primary:** `precipitation` (PRECTOTCORR, $\text{kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1} \rightarrow \text{mm/day}$).
- **Secondary:** `evapotranspiration` (Evap_tavg, $\text{kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1} \rightarrow \text{mm/day}$).
- **Scientific Question:** *Are monsoon precipitation anomalies increasing in intensity, and is moisture flux through evapotranspiration keeping pace with increased thermal demand?*

### Module C: Terrestrial Hydrological Storage
- **Primary:** `soil_moisture_0_10cm` (Topsoil moisture, $\text{kg}\cdot\text{m}^{-2}$).
- **Secondary:** `soil_moisture_10_40cm` (Rootzone moisture, $\text{kg}\cdot\text{m}^{-2}$).
- **Scientific Question:** *How quickly do extreme rainfall events recharge soil storage, and is there evidence of persistent multi-year desiccation or wetting?*

---

## 3. Justification of Scope Against Challenge Objectives

1. **Defensible Statistical Trend Testing:** 297–300 monthly observations provide substantial statistical power for both parametric OLS and non-parametric Mann-Kendall and Sen's slope tests ($n \approx 300 \gg 30$).
2. **Seasonal Decomposition Necessity:** The strong 12-month seasonality in all variables directly necessitates deseasonalization and seasonal Mann-Kendall analysis, illustrating core NASA challenge requirements.
3. **Multi-Model Forecasting:** The strong autocorrelation in soil moisture and seasonal predictability in temperature provide a sound basis for comparing baseline benchmarks (persistence, seasonal naive) against machine learning models (Ridge regression, Random Forest) without overfitting.
4. **Inter-Variable Correlation & Storytelling:** The combination of temperature, precipitation, and soil moisture tells a complete climate story, providing competition-level depth and originality.
