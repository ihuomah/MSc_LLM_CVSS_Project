import pandas as pd

file_path = "data/raw/nvd_pilot_raw.xlsx"

df = pd.read_excel(file_path)

print("\n===== DATASET SHAPE =====")
print(df.shape)

print("\n===== COLUMNS =====")
print(df.columns.tolist())

print("\n===== SEVERITY DISTRIBUTION =====")
print(df["official_severity"].value_counts())

print("\n===== FIRST 5 RECORDS =====")
print(df.head())