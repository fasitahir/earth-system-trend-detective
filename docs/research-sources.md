# Research Sources & Data Provenance

## 1. Challenge Definition
- **Challenge Title:** Be an Earth System Trend Detective!
- **Competition:** NASA Space Apps Challenge 2026
- **URL:** https://www.spaceappschallenge.org/2026/challenges/be-an-earth-system-trend-detective/
- **Key Themes:** Detecting directional changes in Earth system variables, isolating seasonal variability, quantifying statistical significance, evaluating geographic and inter-variable interactions, and forecasting future behavior.

---

## 2. NASA Missions, Models & Data Portals

### 2.1 NASA Giovanni
- **Portal:** Goddard Earth Sciences Data and Information Services Center (GES DISC) Giovanni
- **URL:** https://giovanni.gsfc.nasa.gov/giovanni/
- **Role:** Interactive analytical tool for visualizing and querying Earth science data without downloading entire multi-terabyte datasets.
- **Query Service Used in Provided Data:** `ArAvTs` (Area-Averaged Time Series).
- **Shape Layer:** `state_dept_countries_2017/shp_171` (Pakistan national boundary).

### 2.2 MERRA-2 (Modern-Era Retrospective Analysis for Research and Applications, Version 2)
- **Source Mission / Model:** NASA Global Modeling and Assimilation Office (GMAO).
- **Spatial Resolution:** 0.5° latitude x 0.625° longitude.
- **Temporal Resolution:** Monthly.
- **Variables Supplied:**
  - `M2TMNXSLV_5_12_4_T2M`: 2-meter air temperature (Kelvin).
  - `M2TMNXSLV_5_12_4_TS`: Surface skin temperature (Kelvin).
  - `M2TMNXFLX_5_12_4_PRECTOTCORR`: Bias-corrected total surface precipitation flux (kg m-2 s-1).
- **Documentation:** https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/

### 2.3 GLDAS-2.1 (Global Land Data Assimilation System)
- **Source Mission / Model:** NASA GSFC Hydrological Sciences Laboratory & NOAA NCEP.
- **Model:** Noah Land Surface Model v2.1.
- **Spatial Resolution:** 1.0° x 1.0°.
- **Temporal Resolution:** Monthly.
- **Variables Supplied:**
  - `GLDAS_NOAH10_M_2_1_Evap_tavg`: Total evapotranspiration flux (kg m-2 s-1).
  - `GLDAS_NOAH10_M_2_1_SoilMoi0_10cm_inst`: Soil moisture in top 0–10 cm layer (kg m-2).
  - `GLDAS_NOAH10_M_2_1_SoilMoi10_40cm_inst`: Soil moisture in 10–40 cm layer (kg m-2).
- **Documentation:** https://ldas.gsfc.nasa.gov/gldas/
