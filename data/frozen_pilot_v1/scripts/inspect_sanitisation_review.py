import pandas as pd

SANITISED_FILE = "data/processed/nvd_pilot_sanitised.xlsx"

NO_CPE_OUTPUT = "data/processed/no_cpe_review.xlsx"
CPE_LEAK_OUTPUT = "data/processed/cpe_leak_review.xlsx"

df = pd.read_excel(SANITISED_FILE)

review_columns = [
    "cve_id",
    "has_cpe",
    "cpe_vendors",
    "cpe_products",
    "original_description",
    "sanitised_description",
    "residual_flags",
    "official_cvss_vector",
    "official_base_score",
    "official_severity",
    "published_date",
]

review_columns = [col for col in review_columns if col in df.columns]

no_cpe = df[df["has_cpe"] == False].copy()

cpe_leaks = df[
    (df["has_cpe"] == True) &
    (df["residual_flags"].fillna("").str.len() > 0)
].copy()

no_cpe[review_columns].to_excel(NO_CPE_OUTPUT, index=False)
cpe_leaks[review_columns].to_excel(CPE_LEAK_OUTPUT, index=False)

print("\n===== SANITISATION REVIEW SUMMARY =====")
print(f"No-CPE rows: {len(no_cpe)}")
print(f"CPE rows with residual flags: {len(cpe_leaks)}")

print(f"\nNo-CPE review file saved to: {NO_CPE_OUTPUT}")
print(f"CPE leak review file saved to: {CPE_LEAK_OUTPUT}")

print("\n===== NO-CPE ROWS =====")
for _, row in no_cpe.iterrows():
    print("\n---")
    print("CVE:", row["cve_id"])
    print("Severity:", row["official_severity"])
    print("CPE Vendors:", row.get("cpe_vendors"))
    print("CPE Products:", row.get("cpe_products"))
    print("Sanitised:", row["sanitised_description"])
    print("Residual flags:", row["residual_flags"])

print("\n===== CPE ROWS WITH RESIDUAL FLAGS: FIRST 10 =====")
for _, row in cpe_leaks.head(10).iterrows():
    print("\n---")
    print("CVE:", row["cve_id"])
    print("Severity:", row["official_severity"])
    print("CPE Vendors:", row.get("cpe_vendors"))
    print("CPE Products:", row.get("cpe_products"))
    print("Sanitised:", row["sanitised_description"])
    print("Residual flags:", row["residual_flags"])