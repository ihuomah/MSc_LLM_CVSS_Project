from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "frozen"
    / "main_dataset_frozen_v1.parquet"
)

df = pd.read_parquet(INPUT_FILE)

print("=" * 80)
print("has_cpe distribution")
print("=" * 80)
print(df["has_cpe"].value_counts(dropna=False))