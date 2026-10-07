import pandas as pd
from pathlib import Path
import time
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

RAW_DATA_PATH = Path("data/raw/ev_charging_dataset.xlsx")
PROCESSED_DIR = Path("data/processed")

def process_and_export_data():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("⚡ EV CHARGING DEMAND - DATA PROCESSING & AGGREGATION PIPELINE")
    print("=" * 70)
    
    t0 = time.time()
    print("\n[1/4] Loading 'sessions', 'stations', and 'chargers' from Excel...")
    excel_file = pd.ExcelFile(RAW_DATA_PATH)
    
    df_sessions = pd.read_excel(excel_file, sheet_name="sessions")
    df_stations = pd.read_excel(excel_file, sheet_name="stations")
    df_chargers = pd.read_excel(excel_file, sheet_name="chargers")
    
    print(f"      Loaded {len(df_sessions):,} sessions in {time.time() - t0:.2f}s.")
    
    # Ensure start_timestamp is datetime
    df_sessions['start_timestamp'] = pd.to_datetime(df_sessions['start_timestamp'])
    df_sessions['date'] = df_sessions['start_timestamp'].dt.date
    df_sessions['hour'] = df_sessions['start_timestamp'].dt.hour
    
    # -------------------------------------------------------------
    # 1. Total Daily Network Demand
    # -------------------------------------------------------------
    print("\n[2/4] Generating Total Daily Network Demand time-series...")
    daily_total = df_sessions.groupby(pd.Grouper(key='start_timestamp', freq='D')).agg(
        total_energy_kwh=('energy_kwh', 'sum'),
        session_count=('session_id', 'count'),
        avg_session_duration_min=('session_duration_minutes', 'mean'),
        total_revenue=('total_cost', 'sum'),
        avg_price_per_kwh=('price_per_kwh', 'mean'),
        unique_customers=('customer_id', 'nunique')
    ).reset_index()
    daily_total.rename(columns={'start_timestamp': 'timestamp'}, inplace=True)
    
    daily_total_path = PROCESSED_DIR / "daily_demand_total.csv"
    daily_total.to_csv(daily_total_path, index=False)
    print(f"      Saved: {daily_total_path} ({len(daily_total)} daily records)")
    
    # -------------------------------------------------------------
    # 2. Regional Daily Demand Breakdown
    # -------------------------------------------------------------
    print("\n[3/4] Generating Regional Daily Demand time-series...")
    daily_regional = df_sessions.groupby([
        pd.Grouper(key='start_timestamp', freq='D'),
        'station_region'
    ]).agg(
        total_energy_kwh=('energy_kwh', 'sum'),
        session_count=('session_id', 'count'),
        total_revenue=('total_cost', 'sum'),
        unique_customers=('customer_id', 'nunique')
    ).reset_index()
    daily_regional.rename(columns={'start_timestamp': 'timestamp'}, inplace=True)
    
    daily_regional_path = PROCESSED_DIR / "daily_demand_by_region.csv"
    daily_regional.to_csv(daily_regional_path, index=False)
    print(f"      Saved: {daily_regional_path} ({len(daily_regional)} records)")

    # -------------------------------------------------------------
    # 3. Hourly Network Demand (for peak-hour & load profiling)
    # -------------------------------------------------------------
    print("\n[4/4] Generating Hourly Network Demand time-series...")
    hourly_total = df_sessions.groupby(pd.Grouper(key='start_timestamp', freq='h')).agg(
        total_energy_kwh=('energy_kwh', 'sum'),
        session_count=('session_id', 'count'),
        total_revenue=('total_cost', 'sum')
    ).reset_index()
    hourly_total.rename(columns={'start_timestamp': 'timestamp'}, inplace=True)
    # Fill hours with 0 sessions
    hourly_total['total_energy_kwh'] = hourly_total['total_energy_kwh'].fillna(0)
    hourly_total['session_count'] = hourly_total['session_count'].fillna(0)
    hourly_total['total_revenue'] = hourly_total['total_revenue'].fillna(0)
    
    hourly_total_path = PROCESSED_DIR / "hourly_demand_total.csv"
    hourly_total.to_csv(hourly_total_path, index=False)
    print(f"      Saved: {hourly_total_path} ({len(hourly_total)} hourly records)")

    # Also save metadata lookup files for stations and chargers in processed/
    df_stations.to_csv(PROCESSED_DIR / "dim_stations.csv", index=False)
    df_chargers.to_csv(PROCESSED_DIR / "dim_chargers.csv", index=False)

    print("\n" + "=" * 70)
    print(f" SUCCESS: All processed datasets exported in {time.time() - t0:.2f}s!")
    print("=" * 70)

if __name__ == "__main__":
    process_and_export_data()
