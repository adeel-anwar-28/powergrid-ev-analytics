"""
===============================================================================
PowerGrid EV Analytics - Master Pipeline Runner
===============================================================================
Executes all stages of the data processing, statistical time-series
analysis, and SARIMA forecasting pipeline for Task 01.
===============================================================================
"""

import sys
import time
from pathlib import Path

# UTF-8 stdout configuration for Windows compatibility
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from src.inspect_data import inspect_workbook
from src.data_processing import process_and_export_data
from src.time_series_analysis import analyze_and_plot
from src.forecasting_model import train_and_forecast

def main():
    total_start = time.time()
    print("=" * 75)
    print("⚡ POWERGRID EV ANALYTICS — END-TO-END PIPELINE ORCHESTRATOR")
    print("=" * 75)

    print("\n[STAGE 1/4] Inspecting Raw Workbook Schema...")
    inspect_workbook()

    print("\n[STAGE 2/4] Processing & Aggregating Time-Series Datasets...")
    process_and_export_data()

    print("\n[STAGE 3/4] Running Stationarity Tests & Time-Series Diagnostics...")
    analyze_and_plot()

    print("\n[STAGE 4/4] Training SARIMA Model & Generating Q1 2025 Forecast...")
    train_and_forecast()

    print("\n" + "=" * 75)
    print(f"🎉 ALL PIPELINE STAGES COMPLETED IN {time.time() - total_start:.2f} SECONDS!")
    print("=" * 75)
    print("Artifacts generated in: tasks/task_01_demand_forecasting/")
    print("Processed datasets in : data/processed/")

if __name__ == "__main__":
    main()
