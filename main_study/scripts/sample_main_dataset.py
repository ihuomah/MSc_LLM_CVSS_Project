from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "processed"
    / "main_candidate_pool_with_epss.parquet"
)

PILOT_VERIFICATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "frozen_pilot_v2"
    / "datasets"
    / "pilot_record_id_verification_v2.xlsx"
)

FROZEN_DIR = PROJECT_ROOT / "main_study" / "datasets" / "frozen"
AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"

FROZEN_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PARQUET = FROZEN_DIR / "main_dataset_frozen_v1.parquet"
OUTPUT_CSV = FROZEN_DIR / "main_dataset_frozen_v1.csv"
OUTPUT_XLSX = FROZEN_DIR / "main_dataset_frozen_v1.xlsx"

SAMPLING_LOG = AUDIT_DIR / "main_sampling_log_v1.txt"
SAMPLING_SUMMARY = AUDIT_DIR / "main_sampling_summary_v1.xlsx"

RANDOM_SEED = 42

SEVERITY_TARGETS = {
    "CRITICAL": 250,
    "HIGH": 250,
    "MEDIUM": 250,
    "LOW": 250,
}


def write_log(message):
    print(message)
    with SAMPLING_LOG.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def main():
    SAMPLING_LOG.write_text("", encoding="utf-8")

    write_log("=" * 80)
    write_log("Starting Main Dataset Sampling")
    write_log("=" * 80)

    df = pd.read_parquet(INPUT_FILE)
    pilot = pd.read_excel(PILOT_VERIFICATION_FILE)

    if "cve_id" not in pilot.columns:
        raise ValueError("Pilot verification file does not contain cve_id column.")

    pilot_cves = set(pilot["cve_id"].astype(str))

    required_cols = [
        "cve_id",
        "official_severity",
        "is_nvd_grounded",
        "has_epss",
        "published_date",
        "epss_score",
        "epss_percentile",
        "official_cvss_vector",
        "official_base_score",
        "cvss_selection_method",
    ]

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Input dataset missing required columns: {missing}")

    write_log(f"Input enriched candidate pool rows: {len(df)}")
    write_log(f"Pilot CVEs loaded: {len(pilot_cves)}")

    sampling_pool = df[
        (df["is_nvd_grounded"] == True)
        & (df["has_epss"] == True)
    ].copy()

    write_log(f"NVD-grounded + EPSS-covered rows before pilot exclusion: {len(sampling_pool)}")

    pilot_present_mask = sampling_pool["cve_id"].astype(str).isin(pilot_cves)
    pilot_found = int(pilot_present_mask.sum())
    pilot_missing_from_sampling_pool = len(pilot_cves) - pilot_found

    write_log(f"Pilot CVEs found in sampling pool and excluded: {pilot_found}")
    write_log(f"Pilot CVEs not present in sampling pool: {pilot_missing_from_sampling_pool}")

    sampling_pool = sampling_pool[~pilot_present_mask].copy()

    write_log(f"Rows after pilot exclusion: {len(sampling_pool)}")

    severity_counts_after_exclusion = (
        sampling_pool["official_severity"]
        .value_counts()
        .reindex(SEVERITY_TARGETS.keys())
        .fillna(0)
        .astype(int)
    )

    write_log("\nSeverity counts after NVD-grounded + EPSS + pilot exclusion:")
    write_log(str(severity_counts_after_exclusion))

    for severity, target in SEVERITY_TARGETS.items():
        available = int(severity_counts_after_exclusion.loc[severity])
        if available < target:
            raise ValueError(
                f"Not enough {severity} records. Required {target}, available {available}."
            )

    sampled_frames = []

    for severity, target in SEVERITY_TARGETS.items():
        subset = sampling_pool[sampling_pool["official_severity"] == severity].copy()
        sampled = subset.sample(n=target, random_state=RANDOM_SEED)
        sampled_frames.append(sampled)

    final_df = (
        pd.concat(sampled_frames)
        .sample(frac=1, random_state=RANDOM_SEED)
        .reset_index(drop=True)
    )

    final_df.insert(0, "record_id", range(1, len(final_df) + 1))

    final_df["published_year"] = pd.to_datetime(
        final_df["published_date"], errors="coerce"
    ).dt.year

    sampled_severity_counts = (
        final_df["official_severity"]
        .value_counts()
        .reindex(SEVERITY_TARGETS.keys())
        .fillna(0)
        .astype(int)
    )

    sampled_year_counts = final_df["published_year"].value_counts().sort_index()

    sampled_cvss_method_counts = final_df["cvss_selection_method"].value_counts()

    # Save frozen dataset
    final_df.to_parquet(OUTPUT_PARQUET, index=False)
    final_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    final_df.to_excel(OUTPUT_XLSX, index=False)

    # Summary workbook
    overall_summary = pd.DataFrame([{
        "input_enriched_rows": len(df),
        "sampling_pool_before_pilot_exclusion": len(df[(df["is_nvd_grounded"] == True) & (df["has_epss"] == True)]),
        "pilot_cves_loaded": len(pilot_cves),
        "pilot_cves_found_excluded": pilot_found,
        "pilot_cves_not_present_in_sampling_pool": pilot_missing_from_sampling_pool,
        "sampling_pool_after_pilot_exclusion": len(sampling_pool),
        "final_sample_size": len(final_df),
        "random_seed": RANDOM_SEED,
    }])

    severity_after_exclusion_df = severity_counts_after_exclusion.reset_index()
    severity_after_exclusion_df.columns = ["official_severity", "available_after_exclusion"]

    sampled_severity_df = sampled_severity_counts.reset_index()
    sampled_severity_df.columns = ["official_severity", "sampled_count"]

    sampled_year_df = sampled_year_counts.reset_index()
    sampled_year_df.columns = ["published_year", "sampled_count"]

    sampled_cvss_method_df = sampled_cvss_method_counts.reset_index()
    sampled_cvss_method_df.columns = ["cvss_selection_method", "sampled_count"]

    with pd.ExcelWriter(SAMPLING_SUMMARY, engine="openpyxl") as writer:
        overall_summary.to_excel(writer, sheet_name="overall", index=False)
        severity_after_exclusion_df.to_excel(writer, sheet_name="available_by_severity", index=False)
        sampled_severity_df.to_excel(writer, sheet_name="sampled_by_severity", index=False)
        sampled_year_df.to_excel(writer, sheet_name="sampled_by_year", index=False)
        sampled_cvss_method_df.to_excel(writer, sheet_name="sampled_by_cvss_method", index=False)

    write_log("\nSampled severity distribution:")
    write_log(str(sampled_severity_counts))

    write_log("\nSampled publication year distribution:")
    write_log(str(sampled_year_counts))

    write_log("\nSampled CVSS selection method distribution:")
    write_log(str(sampled_cvss_method_counts))

    write_log("\nOutputs:")
    write_log(f"Frozen Parquet: {OUTPUT_PARQUET}")
    write_log(f"Frozen CSV: {OUTPUT_CSV}")
    write_log(f"Frozen XLSX: {OUTPUT_XLSX}")
    write_log(f"Sampling log: {SAMPLING_LOG}")
    write_log(f"Sampling summary: {SAMPLING_SUMMARY}")

    write_log("=" * 80)
    write_log("Main Dataset Sampling Complete")
    write_log("=" * 80)


if __name__ == "__main__":
    main()