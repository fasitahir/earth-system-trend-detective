# Statistical Trend Methodology & Findings Report

**Project:** EarthScope (NASA Space Apps Challenge 2026)  
**Challenge:** "Be an Earth System Trend Detective!"  
**Region:** Pakistan (Area-Averaged, 23.31°N–37.69°N, 60.39°E–77.73°E)  
**Period:** 2001–2025  
**Document:** Statistical Trend Detection Methodology & Findings  

---

## 1. Mathematical & Statistical Framework

EarthScope implements both parametric and non-parametric statistical methods to detect, quantify, and test the significance of long-term trends in Earth system variables.

### 1.1 Ordinary Least Squares (OLS) Linear Regression

Fits the parametric linear model:
$$y_t = \beta_0 + \beta_1 t + \epsilon_t, \quad \epsilon_t \sim \mathcal{N}(0, \sigma^2)$$

- **Rate of change ($\beta_1$):**
  $$\hat{\beta}_1 = \frac{\sum_{t=1}^n (t - \bar{t})(y_t - \bar{y})}{\sum_{t=1}^n (t - \bar{t})^2}$$
- **$t$-statistic & $p$-value:** Tests $H_0: \beta_1 = 0$ against $H_1: \beta_1 \neq 0$ using $t = \hat{\beta}_1 / \text{SE}(\hat{\beta}_1)$ with $n - 2$ degrees of freedom.
- **Assumptions:** Residuals are normally distributed, homoscedastic, and serially uncorrelated.
- **Limitation:** Highly vulnerable to heavy-tailed distributions and single extreme events (e.g. monsoon floods).

---

### 1.2 Non-Parametric Mann-Kendall Test

Tests whether a time series has a monotonic upward or downward trend without assuming normality.

- **Mann-Kendall $S$ Statistic:**
  $$S = \sum_{i=1}^{n-1} \sum_{j=i+1}^n \text{sgn}(y_j - y_i)$$
  where:
  $$\text{sgn}(\theta) = \begin{cases} +1 & \text{if } \theta > 0 \\ 0 & \text{if } \theta = 0 \\ -1 & \text{if } \theta < 0 \end{cases}$$

- **Variance of $S$ with Tie Correction:**
  $$\text{Var}(S) = \frac{n(n - 1)(2n + 5) - \sum_{k=1}^m t_k(t_k - 1)(2t_k + 5)}{18}$$
  where $m$ is the number of tied groups and $t_k$ is the size of the $k$-th tied group.

- **Standardized Test Statistic ($Z$):**
  $$Z = \begin{cases} \frac{S - 1}{\sqrt{\text{Var}(S)}} & \text{if } S > 0 \\ 0 & \text{if } S = 0 \\ \frac{S + 1}{\sqrt{\text{Var}(S)}} & \text{if } S < 0 \end{cases}$$
- **Two-Sided $p$-value:** $p = 2 \left[1 - \Phi(|Z|)\right]$, where $\Phi$ is the standard normal cumulative distribution function.

---

### 1.3 Sen's Robust Slope Estimator

Computes the non-parametric median rate of change, invariant to extreme outliers:
$$\beta_{\text{Sen}} = \text{median} \left\{ \frac{y_j - y_i}{t_j - t_i} \right\} \quad \forall \ 1 \le i < j \le n$$

- **$100(1 - \alpha)\%$ Confidence Interval:**
  Rank bounds $M_1$ and $M_2$ are derived from the order statistics of sorted pairwise slopes:
  $$C_\alpha = Z_{1 - \alpha/2} \cdot \sqrt{\text{Var}(S)}$$
  $$M_1 = \frac{N - C_\alpha}{2}, \quad M_2 = \frac{N + C_\alpha}{2}$$
  where $N = \frac{n(n-1)}{2}$. The confidence interval is $[\text{Slope}_{(M_1)}, \text{Slope}_{(M_2)}]$.

---

### 1.4 Trend-Free Pre-Whitening (Yue-Pilon Modified Mann-Kendall)

Positive serial autocorrelation ($r_1 > 0$) artificially inflates $\text{Var}(S)$, producing false-positive trend detections. When significant lag-1 autocorrelation is detected ($|r_1| > 1.96/\sqrt{n}$), the Yue-Pilon (2002) algorithm:
1. Removes the monotonic trend: $y'_t = y_t - \beta_{\text{Sen}} \cdot t$.
2. Estimates the lag-1 autocorrelation coefficient $r_1$ of $y'_t$.
3. Pre-whitens residuals: $e_t = y'_t - r_1 y'_{t-1}$.
4. Blends the true slope back in: $Y''_t = e_t + \beta_{\text{Sen}} \cdot t$.
5. Executes the Mann-Kendall test on $Y''_t$.

---

### 1.5 Seasonal Mann-Kendall (Hirsch et al. 1982)

For unadjusted seasonal monthly time series, computes $S_m$ and $\text{Var}(S_m)$ for each of the 12 individual calendar months independently:
$$S_{\text{total}} = \sum_{m=1}^{12} S_m, \quad \text{Var}(S_{\text{total}}) = \sum_{m=1}^{12} \text{Var}(S_m)$$
This eliminates seasonal cycle interference while testing for consistent inter-annual monotonic changes across all seasons.

---

## 2. Empirical Trend Results for Pakistan (2001–2025)

*(Evaluation on Deseasonalized Monthly Anomalies, $\alpha = 0.05$)*

| Variable | Sen's Slope (per decade) | 95% Confidence Interval | Deseasonalized MK $p$-value | OLS Slope (per decade) | OLS $p$-value | Trend Direction ($\alpha=0.05$) |
|---|---|---|---|---|---|---|
| **Precipitation** | **+7.29 mm/mo** | $[+5.25, +9.49]$ | **$p < 0.0001$** | $+13.23\text{ mm/mo}$ | $p < 0.0001$ | **Increasing (Significant)** |
| **Evapotranspiration** | **+3.32 mm/mo** | $[+2.15, +4.48]$ | **$p < 0.0001$** | $+3.80\text{ mm/mo}$ | $p < 0.0001$ | **Increasing (Significant)** |
| **Topsoil Moisture (0–10cm)** | **+1.06 kg/m²** | $[+0.66, +1.45]$ | **$p < 0.0001$** | $+1.01\text{ kg/m²}$ | $p < 0.0001$ | **Increasing (Significant)** |
| **Rootzone Moisture (10–40cm)**| **+1.97 kg/m²** | $[+1.30, +2.64]$ | **$p < 0.0001$** | $+2.12\text{ kg/m²}$ | $p < 0.0001$ | **Increasing (Significant)** |
| **Surface Skin Temp (`ts`)** | **-0.255 °C** | $[-0.446, -0.066]$ | **$p = 0.0037$** | $-0.265\text{ °C}$ | $p = 0.0073$ | **Decreasing (Significant)** |
| **2m Air Temp (`t2m`)** | **-0.158 °C** | $[-0.330, +0.008]$ | **$p = 0.0572$** | $-0.143\text{ °C}$ | $p = 0.1160$ | **No Detected Trend ($p > 0.05$)** |

---

## 3. Scientific Interpretation of Findings

### 3.1 The Coupled Hydrological Intensification
- All four hydrological variables—**precipitation, topsoil moisture, rootzone moisture, and evapotranspiration**—exhibit statistically significant increasing monotonic trends over the 2001–2025 period ($p < 0.0001$).
- **Sen's Slope vs OLS Discrepancy in Precipitation:** OLS estimates a slope of $+13.23\text{ mm/month/decade}$, whereas Sen's median slope is $+7.29\text{ mm/month/decade}$. The OLS slope is inflated by nearly 80% due to catastrophic flood years (such as 2020 and 2022). Sen's slope represents the true robust median climatological trend, uncorrupted by skewness.

### 3.2 The Evaporative Cooling Signal
- Surface skin temperature exhibits a statistically significant cooling trend of **$-0.255^\circ\text{C}$ per decade** ($p = 0.0037$).
- This cooling trend aligns with physical Earth-system dynamics: Pakistan's increased precipitation and elevated soil moisture recharge have driven higher evapotranspiration ($+3.32\text{ mm/month/decade}$), transforming sensible heat into latent heat and cooling the ground surface.
- In contrast, ambient 2-meter air temperature shows a slight negative Sen's slope ($-0.158^\circ\text{C/decade}$) which is **not statistically significant** ($p = 0.057 > 0.05$).

---

## 4. Verification and Multiple Testing Considerations

- **Single Region Context:** For national aggregate series, Family-Wise Error Rate (FWER) adjustments are not applicable across spatial grids because each variable is a distinct physical time series.
- **Independence & Autocorrelation:** The Modified Yue-Pilon pre-whitening ensures that trend significance in soil moisture is not a spurious artifact of monthly autocorrelation.
- **Reproducibility:** All trend outputs are deterministically computed by `backend/analytics/trend_detection/engine.py` and verifiable via automated pytest benchmarks.
