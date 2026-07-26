import pandas as pd

FINAL_FILE = "data/processed/nvd_pilot_final.xlsx"

INFERENCE_FILE = "data/processed/pilot_inference_input_v1.xlsx"
MAPPING_FILE = "data/processed/pilot_record_id_mapping_v1.xlsx"
VERIFICATION_FILE = "data/processed/pilot_record_id_verification_v1.xlsx"

df = pd.read_excel(FINAL_FILE).reset_index(drop=True)

df["record_id"] = range(1, len(df) + 1)

inference_df = df[["record_id", "final_description"]].rename(
    columns={"final_description": "description_for_model"}
)

mapping_df = df[["record_id", "cve_id"]]

verification_df = df[[
    "record_id",
    "cve_id",
    "final_description",
    "official_cvss_vector",
    "official_base_score",
    "official_severity"
]]

inference_df.to_excel(INFERENCE_FILE, index=False)
mapping_df.to_excel(MAPPING_FILE, index=False)
verification_df.to_excel(VERIFICATION_FILE, index=False)

print("\nFiles created:")
print(INFERENCE_FILE)
print(MAPPING_FILE)
print(VERIFICATION_FILE)

print("\nRows:", len(df))

print("\nPreview:")
print(verification_df.head())