import pandas as pd

FINAL_FILE = "data/processed/nvd_pilot_final.xlsx"
OUTPUT_FILE = "data/processed/pilot_inference_input.xlsx"

df = pd.read_excel(FINAL_FILE)

inference_df = pd.DataFrame({
    "record_id": range(1, len(df) + 1),
    "description_for_model": df["final_description"]
})

inference_df.to_excel(OUTPUT_FILE, index=False)

print(f"\nPilot inference input saved to:")
print(OUTPUT_FILE)

print("\nRows:", len(inference_df))
print("\nColumns:", inference_df.columns.tolist())

print("\nPreview:")
print(inference_df.head())