from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PILOT_FILE = PROJECT_ROOT / "data" / "frozen_pilot_v2" / "datasets" / "pilot_record_id_verification_v2.xlsx"
ENRICHED_POOL = PROJECT_ROOT / "main_study" / "datasets" / "processed" / "main_candidate_pool_with_epss.parquet"

OUTPUT_FILE = PROJECT_ROOT / "main_study" / "audit" / "pilot_cvss_source_distribution_check.xlsx"


def main():
    pilot = pd.read_excel(PILOT_FILE)
    pool = pd.read_parquet(ENRICHED_POOL)

    pilot_cves = pilot[["record_id", "cve_id"]].copy()

    joined = pilot_cves.merge(
        pool[
            [
                "cve_id",
                "official_severity",
                "cvss_selection_method",
                "cvss_source",
                "cvss_type",
                "cvss_version",
                "is_nvd_grounded",
                "has_epss",
            ]
        ],
        on="cve_id",
        how="left",
    )

    summary = (
        joined["cvss_selection_method"]
        .fillna("not_found")
        .value_counts()
        .reset_index()
    )
    summary.columns = ["cvss_selection_method", "count"]

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        joined.to_excel(writer, sheet_name="pilot_joined", index=False)
        summary.to_excel(writer, sheet_name="summary", index=False)

    print("=" * 80)
    print("Pilot CVSS source distribution check")
    print("=" * 80)
    print(summary.to_string(index=False))
    print(f"\nSaved report to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()