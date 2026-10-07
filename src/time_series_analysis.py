import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

warnings.filterwarnings("ignore")

# Configure plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

DATA_FILE = Path("data/processed/daily_demand_total.csv")
OUTPUT_DIR = Path("tasks/task_01_demand_forecasting")

def run_adf_test(series, name="Series"):
    print(f"\n--- Augmented Dickey-Fuller (ADF) Test: {name} ---")
    result = adfuller(series.dropna(), autolag='AIC')
    print(f"  ADF Statistic       : {result[0]:.4f}")
    print(f"  p-value             : {result[1]:.4e}")
    print(f"  Lags Used           : {result[2]}")
    print(f"  Number of Obs       : {result[3]}")
    print("  Critical Values:")
    for key, val in result[4].items():
        print(f"    {key}: {val:.4f}")
    
    if result[1] <= 0.05:
        print("  => Conclusion: Reject H0 -> The series is STATIONARY (p <= 0.05)")
        is_stationary = True
    else:
        print("  => Conclusion: Fail to reject H0 -> The series is NON-STATIONARY (Differencing required, d >= 1)")
        is_stationary = False
    return is_stationary, result[1]

def run_kpss_test(series, name="Series", regression="c"):
    print(f"\n--- KPSS Test: {name} (regression='{regression}') ---")
    kpss_stat, p_val, lags, crit_vals = kpss(series.dropna(), regression=regression, nlags='auto')
    print(f"  KPSS Statistic      : {kpss_stat:.4f}")
    print(f"  p-value             : {p_val:.4f}")
    print(f"  Lags Used           : {lags}")
    print("  Critical Values:")
    for key, val in crit_vals.items():
        print(f"    {key}: {val:.4f}")
        
    if p_val < 0.05:
        print("  => Conclusion: Reject H0 -> The series has a Unit Root / is NON-STATIONARY")
    else:
        print("  => Conclusion: Fail to reject H0 -> The series is STATIONARY")

def analyze_and_plot():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("=== TIME-SERIES STATISTICAL & STATIONARITY ANALYSIS ===")
    print("=" * 70)
    
    df = pd.read_csv(DATA_FILE, parse_dates=['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    series = df['total_energy_kwh']
    
    # 1. Raw Series Stationarity
    print("\n[STEP 1] Stationarity Check on Original Daily Energy Demand:")
    is_stat, p_val = run_adf_test(series, name="Raw Daily Demand (kWh)")
    run_kpss_test(series, name="Raw Daily Demand (kWh)", regression="ct")
    
    # 2. First Difference Stationarity (d=1)
    diff_1 = series.diff().dropna()
    print("\n[STEP 2] Stationarity Check on First-Differenced Series (d=1):")
    run_adf_test(diff_1, name="First-Differenced Demand (d=1)")
    run_kpss_test(diff_1, name="First-Differenced Demand (d=1)", regression="c")
    
    # 3. Seasonal Difference (D=1, s=7)
    seasonal_diff = diff_1.diff(7).dropna()
    print("\n[STEP 3] Stationarity Check on Seasonal-Differenced Series (d=1, D=1, s=7):")
    run_adf_test(seasonal_diff, name="Seasonal Differenced Demand (d=1, D=1, s=7)")

    # 4. Seasonal Decomposition (period = 7 for weekly seasonality)
    print("\n[STEP 4] Performing Classical Seasonal Decomposition (Weekly Cycle s=7)...")
    decomposition = seasonal_decompose(series, model='additive', period=7)
    
    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    decomposition.observed.plot(ax=axes[0], color='#1f77b4', lw=1.5, title='Observed Daily EV Demand (kWh)')
    decomposition.trend.plot(ax=axes[1], color='#ff7f0e', lw=2, title='Trend Component (Growth in EV Adoption)')
    decomposition.seasonal.plot(ax=axes[2], color='#2ca02c', lw=1.2, title='Seasonal Component (7-Day Weekly Cycle)')
    decomposition.resid.plot(ax=axes[3], color='#d62728', lw=1, style='.', title='Residual / Noise Component')
    
    for ax in axes:
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    decomp_path = OUTPUT_DIR / "seasonal_decomposition_weekly.png"
    plt.savefig(decomp_path, dpi=300)
    plt.close()
    print(f"  ✓ Saved decomposition plot: {decomp_path}")

    # 5. ACF and PACF Plots for Parameter Identification (p, q, P, Q)
    print("\n[STEP 5] Generating ACF and PACF Diagnostic Plots...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    
    plot_acf(diff_1, lags=30, ax=ax1, title="Autocorrelation Function (ACF) - First Difference (d=1)", color='#1f77b4')
    plot_pacf(diff_1, lags=30, ax=ax2, title="Partial Autocorrelation Function (PACF) - First Difference (d=1)", method='ywm', color='#ff7f0e')
    
    ax1.grid(True, alpha=0.3)
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    acf_pacf_path = OUTPUT_DIR / "acf_pacf_diagnostics.png"
    plt.savefig(acf_pacf_path, dpi=300)
    plt.close()
    print(f"  ✓ Saved ACF/PACF plot: {acf_pacf_path}")

    print("\n" + "=" * 70)
    print("✅ Time-Series Diagnostics Completed Successfully!")
    print("=" * 70)

if __name__ == "__main__":
    analyze_and_plot()
