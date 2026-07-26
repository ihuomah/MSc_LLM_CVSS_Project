import pandas as pd

FINAL_FILE = "data/processed/nvd_pilot_final.xlsx"

df = pd.read_excel(FINAL_FILE)

print("\n===== FINAL DATASET CHECK =====")
print("Rows:", len(df))
print("Columns:", df.columns.tolist())

print("\nManually redacted count:")
print(df["manually_redacted"].value_counts())

print("\n===== MANUALLY REDACTED ROWS =====")
for _, row in df[df["manually_redacted"] == True].iterrows():
    print("\n---")
    print("CVE:", row["cve_id"])
    print("Final description:", row["final_description"])