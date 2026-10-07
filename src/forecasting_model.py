import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import json
import warnings
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

warnings.filterwarnings("ignore")

DATA_FILE = Path("data/processed/daily_demand_total.csv")
OUTPUT_DIR = Path("tasks/task_01_demand_forecasting")

def train_and_forecast():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("=== SARIMA DEMAND FORECASTING & EVALUATION PIPELINE ===")
    print("=" * 70)
    
    df = pd.read_csv(DATA_FILE, parse_dates=['timestamp'])
    df.set_index('timestamp', inplace=True)
    df = df.asfreq('D') # Explicit daily frequency
    
    series = df['total_energy_kwh']
    
    # -------------------------------------------------------------
    # 1. Train / Test Split (90-day holdout validation)
    # -------------------------------------------------------------
    test_days = 90
    train = series.iloc[:-test_days]
    test = series.iloc[-test_days:]
    
    print(f"\n[1/4] Train/Test Partition:")
    print(f"      Train Set: {train.index.min().date()} to {train.index.max().date()} ({len(train)} days)")
    print(f"      Test Set : {test.index.min().date()} to {test.index.max().date()} ({len(test)} days)")
    
    # -------------------------------------------------------------
    # 2. Fit SARIMA Model (Order: (1, 1, 1) x (1, 1, 1, 7))
    # -------------------------------------------------------------
    order = (1, 1, 1)
    seasonal_order = (1, 1, 1, 7)
    print(f"\n[2/4] Fitting SARIMAX{order}x{seasonal_order} on Training Data...")
    
    model = SARIMAX(
        train,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    results = model.fit(disp=False)
    print(f"      Model Converged! AIC: {results.aic:.2f} | BIC: {results.bic:.2f}")

    # -------------------------------------------------------------
    # 3. Model Evaluation on Test Set
    # -------------------------------------------------------------
    print("\n[3/4] Generating In-Sample & Test Predictions...")
    test_pred_res = results.get_forecast(steps=len(test))
    test_pred = test_pred_res.predicted_mean
    conf_int = test_pred_res.conf_int(alpha=0.05)

    mae = mean_absolute_error(test, test_pred)
    rmse = np.sqrt(mean_squared_error(test, test_pred))
    mape = np.mean(np.abs((test - test_pred) / test)) * 100
    r2 = r2_score(test, test_pred)
    
    metrics = {
        "model": "SARIMAX(1,1,1)x(1,1,1,7)",
        "train_size": len(train),
        "test_size": len(test),
        "MAE_kWh": round(float(mae), 2),
        "RMSE_kWh": round(float(rmse), 2),
        "MAPE_percent": round(float(mape), 2),
        "R2_score": round(float(r2), 4),
        "AIC": round(float(results.aic), 2),
        "BIC": round(float(results.bic), 2)
    }
    
    print("\n--- Model Accuracy Metrics on Test Set (90 Days) ---")
    print(f"  • MAE   : {mae:,.2f} kWh")
    print(f"  • RMSE  : {rmse:,.2f} kWh")
    print(f"  • MAPE  : {mape:.2f} %")
    print(f"  • R²    : {r2:.4f}")

    with open(OUTPUT_DIR / "model_metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)
        
    # Plot Test Evaluation
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(train.index[-180:], train.iloc[-180:], label='Historical Training (Last 6 Months)', color='#1f77b4', lw=1.5)
    ax.plot(test.index, test, label='Actual Test Demand', color='#2ca02c', lw=2)
    ax.plot(test.index, test_pred, label=f'SARIMA Forecast (MAPE: {mape:.1f}%)', color='#d62728', lw=2, linestyle='--')
    ax.fill_between(test.index, conf_int.iloc[:, 0], conf_int.iloc[:, 1], color='#d62728', alpha=0.15, label='95% Confidence Interval')
    ax.set_title("SARIMA Demand Forecast vs Actual Hold-Out Test Demand", fontsize=14, pad=12, weight='bold')
    ax.set_ylabel("Total Daily Energy Demand (kWh)", fontsize=11)
    ax.set_xlabel("Date", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    eval_plot_path = OUTPUT_DIR / "forecast_evaluation.png"
    plt.savefig(eval_plot_path, dpi=300)
    plt.close()
    print(f"      Saved: {eval_plot_path}")

    # -------------------------------------------------------------
    # 4. Refit on Full Data & Forecast 90 Days into Q1 2025
    # -------------------------------------------------------------
    print("\n[4/4] Refitting on Full 3-Year Dataset & Forecasting 90 Days into 2025...")
    full_model = SARIMAX(
        series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    full_results = full_model.fit(disp=False)
    
    future_steps = 90
    forecast_res = full_results.get_forecast(steps=future_steps)
    forecast_mean = forecast_res.predicted_mean
    forecast_conf = forecast_res.conf_int(alpha=0.05)
    
    # Save Forecast to CSV
    forecast_df = pd.DataFrame({
        'forecast_date': forecast_mean.index,
        'predicted_energy_kwh': forecast_mean.values,
        'lower_bound_95': forecast_conf.iloc[:, 0].values,
        'upper_bound_95': forecast_conf.iloc[:, 1].values
    })
    forecast_csv = OUTPUT_DIR / "future_forecast_q1_2025.csv"
    forecast_df.to_csv(forecast_csv, index=False)
    print(f"      Saved: {forecast_csv} ({len(forecast_df)} forecast days)")

    # Plot Full Forecast
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(series.index[-365:], series.iloc[-365:], label='Historical Daily Demand (2024)', color='#1f77b4', lw=1.5)
    ax.plot(forecast_mean.index, forecast_mean, label='Projected EV Energy Demand (Q1 2025)', color='#ff7f0e', lw=2.2)
    ax.fill_between(forecast_mean.index, forecast_conf.iloc[:, 0], forecast_conf.iloc[:, 1], color='#ff7f0e', alpha=0.2, label='95% Confidence Interval')
    ax.set_title("PowerGrid EV Network - 90-Day Forward Demand Projection (Q1 2025)", fontsize=14, pad=12, weight='bold')
    ax.set_ylabel("Daily Energy Demand (kWh)", fontsize=11)
    ax.set_xlabel("Date", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    future_plot_path = OUTPUT_DIR / "future_demand_forecast_2025.png"
    plt.savefig(future_plot_path, dpi=300)
    plt.close()
    print(f"      Saved: {future_plot_path}")

    print("\n" + "=" * 70)
    print("✅ SARIMA Forecasting Pipeline Successfully Completed!")
    print("=" * 70)

if __name__ == "__main__":
    train_and_forecast()
