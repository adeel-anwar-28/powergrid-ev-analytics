# Task 01 Deliverable Report: EV Charging Demand Forecasting & Grid Load Analysis

## 1. Context & Business Problem
Electric Vehicle (EV) adoption across the UK power distribution network introduces significant peak-load volatility. Distribution Network Operators (DNOs) require reliable forward projections of daily energy demand (kWh) to schedule grid transformer maintenance, prevent localized feeder overloads, and optimize wholesale energy procurement.

This report documents the statistical analysis and time-series model developed for **Task 01: Demand Forecasting**.

---

## 2. Dataset Ingestion & Preprocessing
* **Source Dataset:** `ev_charging_dataset.xlsx` (25.81 MB)
* **Transaction Count:** 294,024 charging sessions
* **Time Span:** January 1, 2022 to December 31, 2024 (3 full calendar years / 1,096 days)
* **Entities:** 33 Charging Stations across London, North West, and Midlands with 199 DC rapid chargers (50kW and 150kW).

### Aggregation Summary
* **Total Energy Delivered (3 Years):** ~23.4 GWh
* **Average Daily Demand:** ~21,400 kWh / day
* **Peak Daily Demand Recorded:** ~38,200 kWh / day (December 2024)

---

## 3. Statistical Properties & Stationarity Analysis

### 3.1 Unit Root Tests
| Series | ADF Statistic | p-value | Critical Value (5%) | Conclusion |
| :--- | :--- | :--- | :--- | :--- |
| **Raw Daily Demand** | $-0.7233$ | $0.8406$ | $-2.8642$ | Non-Stationary (Upward EV Growth Trend) |
| **First Difference ($d=1$)** | **$-6.6379$** | **$5.50 \times 10^{-9}$** | $-2.8642$ | **Stationary** ($p < 0.001$) |
| **Seasonal Difference ($d=1, D=1, s=7$)** | **$-11.9274$** | **$4.87 \times 10^{-22}$** | $-2.8643$ | **Strong Seasonal Stationarity** |

### 3.2 Seasonal Decomposition Insights
1. **Trend Component:** Steady, compounding growth of approximately $+28\%$ YoY in network-wide energy throughput driven by commercial fleet and taxi adoption.
2. **Weekly Seasonal Cycle ($s=7$):** Distinct intra-week variations where Tuesday–Thursday exhibit peak commercial charging demand, while weekends show reduced commercial volume but extended session durations.

---

## 4. SARIMA Model Architecture & Validation

### 4.1 Model Formulation
$$\text{SARIMAX}(1, 1, 1) \times (1, 1, 1)_7$$

* **$p=1$ (AR lag 1):** Captures auto-regressive momentum from the previous day.
* **$d=1$ (First difference):** Stabilizes the macro adoption trend.
* **$q=1$ (MA lag 1):** Accommodates transient shocks (e.g., inclement weather, localized power outages).
* **$P=1, D=1, Q=1, s=7$ (Seasonal components):** Explicitly models the weekly cyclical pattern.

### 4.2 Out-of-Sample Hold-Out Evaluation (90 Days)
* **Test Window:** October 3, 2024 to December 31, 2024
* **Mean Absolute Percentage Error (MAPE):** **`7.95%`**
* **Mean Absolute Error (MAE):** **`1,622.83 kWh / day`**
* **Root Mean Squared Error (RMSE):** **`1,856.88 kWh / day`**
* **Coefficient of Determination ($R^2$):** **`0.6018`**

---

## 5. Forward Projections & Grid Capacity Recommendations (Q1 2025)

The model was refit on the full 3-year history to project demand across **January 1 to March 31, 2025** (90 days):

* **Projected Average Daily Demand (Q1 2025):** `31,850 kWh / day` (vs `26,400 kWh / day` in Q1 2024, a **$+20.6\%$ YoY increase**).
* **Projected Peak Day in Q1 2025:** `39,400 kWh / day` with upper 95% confidence bound at `43,100 kWh / day`.

### 💡 Strategic Grid Recommendations:
1. **Transformer Headroom:** Substation transformers serving the London and North West hubs should ensure at least 15% reserve capacity during Thursday peak windows (16:00–19:00).
2. **Time-of-Use (ToU) Tariff Incentives:** Recommend dynamic off-peak pricing between 23:00 and 05:00 to shift fleet charging away from early evening grid peaks.
3. **Storage Buffer Co-location:** Deploy Battery Energy Storage Systems (BESS) at top 5 utilized stations to shave peak feeder stress.

---

## 6. Deliverable Artifacts Index
* `future_forecast_q1_2025.csv`: Complete daily forecasted values with confidence limits.
* `future_demand_forecast_2025.png`: High-resolution executive visualization.
* `forecast_evaluation.png`: Test evaluation curve against ground truth.
* `seasonal_decomposition_weekly.png`: 4-panel trend, seasonal, and residual decomposition.
* `acf_pacf_diagnostics.png`: Autocorrelation and partial autocorrelation plots.
