# Geographic Intelligence & Spatial Analysis Report

**Project:** EarthScope (Earth System Trend Intelligence)  
**NASA Space Apps Challenge 2026:** "Be an Earth System Trend Detective!"  
**Stage:** Stage 8 Complete (Geographic Intelligence & Spatial Integrity)  
**Date:** 2026-11-15  

---

## 1. Executive Summary

This document formalizes the geospatial domain, coordinate boundaries, native satellite sensor grid resolutions, and multiple-testing statistical corrections applied within EarthScope.

In alignment with the NASA Challenge rule:
> *"If the supplied datasets do not support maps, do not invent geographic precision. Provide a clear alternative such as region comparison or a coverage map."*

EarthScope models the geographic scope strictly upon the verified spatial polygon provided in the NASA Giovanni extracts (`state_dept_countries_2017/shp_171` — Pakistan), avoiding speculative pixel-level downscaling while providing structured regional and ecological zone attribution.

---

## 2. Spatial Domain & Boundary Specification

| Parameter | Specification | Description |
|---|---|---|
| **Country Boundary** | Pakistan (`shp_171`) | U.S. State Department 2017 National Polygon Boundary |
| **Coordinate Reference System** | EPSG:4326 (WGS 84) | Standard World Geodetic System 1984 |
| **Northern Boundary** | 37.6875° N | Karakoram, Hindu Kush, and Himalayan glaciated ranges |
| **Southern Boundary** | 23.3125° N | Arabian Sea littoral boundary and Indus Delta coastline |
| **Western Boundary** | 60.390625° E | Balochistan plateau frontier with Iran and Afghanistan |
| **Eastern Boundary** | 77.734375° E | Punjab and Sindh alluvial plains frontier |
| **Spatial Weighting** | Area-weighted | Cells integrated via cosine of latitude weighting ($\cos\phi$) |

---

## 3. Native Satellite Grid Resolutions

The observational time series analyzed in EarthScope originate from two complementary NASA Earth-observing modeling systems:

1. **MERRA-2 Atmospheric Reanalysis (GMAO):**
   - Products: 2-meter air temperature (`t2m`), surface skin temperature (`ts`), bias-corrected precipitation (`precipitation`).
   - Native Grid Resolution: **0.5° latitude × 0.625° longitude** ($\approx 50\text{ km} \times 60\text{ km}$ per grid cell).
   - Temporal Frequency: Monthly aggregates (2001–2025).

2. **GLDAS-2.1 Noah Land Surface Model:**
   - Products: Total evapotranspiration (`evapotranspiration`), topsoil moisture 0–10 cm (`soil_moisture_0_10cm`), root-zone soil moisture 10–40 cm (`soil_moisture_10_40cm`).
   - Native Grid Resolution: **0.25° latitude × 0.25° longitude** ($\approx 25\text{ km} \times 25\text{ km}$ per grid cell).
   - Temporal Frequency: Monthly aggregates (2001–2025).

---

## 4. Ecological Zones & Regional Disaggregation

Although the Giovanni extracts are area-averaged over the national boundary, Pakistan's topography encompasses five distinct bioclimatic zones. EarthScope maps how national-scale indicators intersect with each zone:

### 4.1 Northern Highlands & Glacial Basins
- **Geographic Extent:** 34.5°N – 37.7°N, 71.0°E – 77.5°E (Gilgit-Baltistan, Upper KP).
- **Elevation Range:** 2,000 – 8,611 m.
- **Climate Classification:** Alpine Tundra / Glacial (*ET / EF*).
- **Vulnerability Profile:** High sensitivity to thermal anomalies, accelerated cryosphere melting, expansion of moraine-dammed glacial lakes, and Glacial Lake Outburst Floods (GLOFs).

### 4.2 Upper Indus Agricultural Plain
- **Geographic Extent:** 28.5°N – 34.0°N, 70.0°E – 75.5°E (Punjab).
- **Elevation Range:** 150 – 350 m.
- **Climate Classification:** Semi-Arid Subtropical (*BSh / Cwa*).
- **Vulnerability Profile:** Extreme pre-monsoon heatwave stress (temperatures exceeding 45°C), intensive canal irrigation creating strong land-atmosphere evaporative cooling feedbacks, and groundwater overdraft.

### 4.3 Lower Indus Basin & Delta
- **Geographic Extent:** 24.0°N – 28.5°N, 67.0°E – 71.0°E (Sindh).
- **Elevation Range:** 10 – 150 m.
- **Climate Classification:** Hyper-Arid Lowland (*BWh*).
- **Vulnerability Profile:** Catastrophic monsoon flood vulnerability (exemplified by the August 2022 pluvial inundation), flat drainage gradients, coastal sea-water intrusion, and soil salinization.

### 4.4 Western Arid Plateaus & Mountain Ranges
- **Geographic Extent:** 25.0°N – 32.5°N, 61.0°E – 70.0°E (Balochistan).
- **Elevation Range:** 500 – 2,200 m.
- **Climate Classification:** Cold / Hot Arid Desert (*BWk / BWh*).
- **Vulnerability Profile:** Chronic meteorological drought vulnerability, reliance on ancient *karez* and depleting aquifers, interspersed with erratic flash flooding.

### 4.5 Arabian Sea Coastal Belt
- **Geographic Extent:** 23.5°N – 25.5°N, 61.5°E – 68.5°E (Makran and Sindh coast).
- **Elevation Range:** 0 – 50 m.
- **Climate Classification:** Coastal Semi-Arid / Marine (*BSh*).
- **Vulnerability Profile:** Extreme wet-bulb temperatures, Arabian Sea tropical cyclonic storm surges, and marine heatwaves.

---

## 5. Spatial Multiple-Testing Correction: Benjamini-Hochberg FDR

When evaluating multiple environmental trends simultaneously, the probability of at least one false positive (Type I error) inflates according to $1 - (1 - \alpha)^m$.

To guarantee statistical rigor across all 6 environmental time-series, EarthScope applies the **Benjamini-Hochberg (1995) False Discovery Rate (FDR)** procedure at $\alpha = 0.05$:

$$\text{Rank } k \text{ threshold: } p_{(k)} \le \frac{k}{m} \cdot \alpha$$

### 5.1 Empirical FDR Test Results ($m = 6, \alpha = 0.05$)

| Variable | Sen Slope / Decade | Raw $p$-value | BH Adjusted $q$-value | FDR Significance ($\alpha=0.05$) |
|---|---|---|---|---|
| **Total Precipitation** | $+7.29\text{ mm/month}$ | $< 0.000001$ | $< 0.000006$ | **Significant** |
| **Total Evapotranspiration** | $+3.32\text{ mm/month}$ | $< 0.000001$ | $< 0.000006$ | **Significant** |
| **Topsoil Moisture (0–10 cm)** | $+1.06\text{ kg/m}^2$ | $< 0.000001$ | $< 0.000006$ | **Significant** |
| **Rootzone Moisture (10–40 cm)** | $+1.97\text{ kg/m}^2$ | $< 0.000001$ | $< 0.000006$ | **Significant** |
| **Surface Skin Temperature (TS)** | $-0.255\text{ }^\circ\text{C}$ | $0.003706$ | $0.004447$ | **Significant** |
| **2-Meter Air Temperature (T2M)** | $-0.158\text{ }^\circ\text{C}$ | $0.057176$ | $0.057176$ | **Not Significant** |

### 5.2 Key Takeaways
1. All 4 hydrological and land-surface moisture variables pass FDR adjustment with extraordinary statistical confidence ($q < 10^{-5}$).
2. Surface Skin Temperature exhibits a significant cooling trend ($q = 0.0044$), corroborating agricultural irrigation expansion in the Indus Basin.
3. 2-Meter Air Temperature marginal significance ($p = 0.0572$) correctly reflects that after removing seasonal climatology and prewhitening serial correlation, the area-averaged decadal trend cannot be definitively asserted at the 95% level.

---

## 6. Scientific Integrity & Mapping Principles

1. **No Synthetic Interpolation:** Many applications interpolate country-level averages across a fine grid to create false visual maps. EarthScope strictly avoids this, displaying the national bounding polygon and geographic zones without fabricating pixel-level precision.
2. **Clear Attribution:** All bounding coordinates and polygon definitions cite NASA Giovanni and U.S. State Department boundary standard `shp_171`.
3. **Reproducibility:** The `/api/v1/spatial/summary` API endpoint exposes coordinate definitions, grid resolution metadata, and FDR-corrected statistics for programmatic verification.
