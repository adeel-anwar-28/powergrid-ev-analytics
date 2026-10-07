import pandas as pd
from pathlib import Path
import time
import sys

# Force UTF-8 standard output if needed
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

DATA_PATH = Path("data/raw/ev_charging_dataset.xlsx")

def inspect_workbook():
    start_time = time.time()
    print("=" * 70)
    print("=== EV CHARGING DATASET INSPECTION ===")
    print("=" * 70)
    
    excel_file = pd.ExcelFile(DATA_PATH)
    print(f"\n=== Available Sheets in Workbook ({len(excel_file.sheet_names)}) ===")
    for idx, sheet in enumerate(excel_file.sheet_names, 1):
        print(f"  {idx}. {sheet}")
    
    for sheet_name in excel_file.sheet_names:
        print(f"\n{'-' * 70}")
        print(f"[*] Sheet: '{sheet_name}'")
        print(f"{'-' * 70}")
        
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
        
        print("\nColumns & Types:")
        for col in df.columns:
            print(f"  - {col:<26} ({df[col].dtype})")
        
        print("\nFirst 5 Rows:")
        print(df.head().to_string(index=False))
        
        # Missing values
        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0]
        print("\nMissing Values:")
        if null_cols.empty:
            print("  [+] Zero missing values detected across all columns.")
        else:
            for col, count in null_cols.items():
                print(f"  [!] {col}: {count:,} nulls ({(count/len(df))*100:.2f}%)")
        
        # Datetime inspection
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]) or 'timestamp' in col.lower() or 'date' in col.lower():
                dt_series = pd.to_datetime(df[col], errors='coerce')
                valid = dt_series.dropna()
                if len(valid) > 0:
                    print(f"\nTimestamp Column Analysis for '{col}':")
                    print(f"  - Earliest Timestamp : {valid.min()}")
                    print(f"  - Latest Timestamp   : {valid.max()}")
                    print(f"  - Total Span         : {valid.max() - valid.min()}")
    
    print(f"\n{'=' * 70}")
    print(f"Completed inspection in {time.time() - start_time:.2f} seconds.")
    print("=" * 70)

if __name__ == "__main__":
    inspect_workbook()


