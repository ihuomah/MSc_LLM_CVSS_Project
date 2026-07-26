from pathlib import Path
import pandas as pd

FILE = Path(
    "data/frozen_pilot_v2/datasets/nvd_pilot_raw_with_epss_v2.xlsx"
)

print("=" * 80)
print("GROUND TRUTH FILE COLUMN INSPECTION")
print("=" * 80)

df = pd.read_excel(FILE)

print(f"\nRows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\nCOLUMN NAMES")
print("-" * 80)

for i, col in enumerate(df.columns, start=1):
    print(f"{i:02d}. {col}")

print("\nFIRST ROW")
print("-" * 80)

print(df.iloc[0].to_string())

print("\nDONE")