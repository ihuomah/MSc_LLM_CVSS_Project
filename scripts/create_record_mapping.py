import pandas as pd

FINAL_FILE = "data/processed/nvd_pilot_final.xlsx"
OUTPUT_FILE = "data/processed/pilot_record_id_mapping.xlsx"

df = pd.read_excel(FINAL_FILE)

mapping_df = pd.DataFrame({
    "record_id": range(1, len(df) + 1),
    "cve_id": df["cve_id"]
})

mapping_df.to_excel(OUTPUT_FILE, index=False)

print(f"\nMapping file saved to:")
print(OUTPUT_FILE)

print("\nRows:", len(mapping_df))
print("\nPreview:")
print(mapping_df.head())