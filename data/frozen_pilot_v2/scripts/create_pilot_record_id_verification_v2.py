from pathlib import Path
import pandas as pd


V1_VERIFICATION = Path("data/frozen_pilot_v1/datasets/pilot_record_id_verification_v1.xlsx")
EPSS_V2 = Path("data/frozen_pilot_v2/datasets/nvd_pilot_raw_with_epss_v2.xlsx")

V2_DATASETS_DIR = Path("data/frozen_pilot_v2/datasets")
V2_AUDIT_DIR = Path("data/frozen_pilot_v2/audit")

V2_DATASETS_DIR.mkdir(parents=True, exist_ok=True)
V2_AUDIT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_VERIFICATION = V2_DATASETS_DIR / "pilot_record_id_verification_v2.xlsx"
OUTPUT_LOG = V2_AUDIT_DIR / "pilot_record_id_verification_v2_creation_log.txt"


def main():
    print("Loading pilot_record_id_verification_v1...")
    verification_v1 = pd.read_excel(V1_VERIFICATION)

    print("Loading nvd_pilot_raw_with_epss_v2...")
    epss_v2 = pd.read_excel(EPSS_V2)

    required_verification_cols = [
        "record_id",
        "cve_id",
        "final_description",
        "official_cvss_vector",
        "official_base_score",
        "official_severity",
    ]

    required_epss_cols = [
        "cve_id",
        "epss_score",
        "epss_percentile",
        "has_epss",
        "epss_date",
        "epss_source",
    ]

    for col in required_verification_cols:
        if col not in verification_v1.columns:
            raise ValueError(f"Missing column in verification v1: {col}")

    for col in required_epss_cols:
        if col not in epss_v2.columns:
            raise ValueError(f"Missing column in EPSS v2 file: {col}")

    epss_subset = epss_v2[required_epss_cols].copy()

    print("Merging verification v1 with EPSS fields...")
    verification_v2 = verification_v1.merge(
        epss_subset,
        on="cve_id",
        how="left",
        validate="one_to_one",
    )

    if len(verification_v2) != len(verification_v1):
        raise ValueError("Row count changed during merge. Stop and inspect.")

    missing_epss = int(verification_v2["epss_score"].isna().sum())

    print("Saving verification v2...")
    verification_v2.to_excel(OUTPUT_VERIFICATION, index=False)

    with open(OUTPUT_LOG, "w", encoding="utf-8") as log:
        log.write("Pilot Record ID Verification v2 Creation Log\n")
        log.write("=" * 80 + "\n")
        log.write(f"Source verification v1: {V1_VERIFICATION}\n")
        log.write(f"Source EPSS v2: {EPSS_V2}\n")
        log.write(f"Output verification v2: {OUTPUT_VERIFICATION}\n")
        log.write(f"Verification v1 rows: {len(verification_v1)}\n")
        log.write(f"Verification v2 rows: {len(verification_v2)}\n")
        log.write(f"Missing EPSS after merge: {missing_epss}\n")
        log.write("\nColumns in verification v2:\n")
        for col in verification_v2.columns:
            log.write(f"- {col}\n")

    print("=" * 80)
    print("pilot_record_id_verification_v2 created successfully")
    print("=" * 80)
    print(f"Rows: {len(verification_v2)}")
    print(f"Missing EPSS after merge: {missing_epss}")
    print(f"Saved to: {OUTPUT_VERIFICATION}")
    print(f"Log saved to: {OUTPUT_LOG}")


if __name__ == "__main__":
    main()