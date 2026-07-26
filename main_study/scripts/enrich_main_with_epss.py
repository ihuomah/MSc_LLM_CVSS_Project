from pathlib import Path
from datetime import datetime, timezone
from urllib.request import urlretrieve

import pandas as pd


# ============================================================================
# Paths
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "raw"
    / "main_candidate_pool_raw.parquet"
)

PROCESSED_DIR = PROJECT_ROOT / "main_study" / "datasets" / "processed"
AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"
EPSS_DIR = PROJECT_ROOT / "main_study" / "datasets" / "raw" / "epss"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
EPSS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PARQUET = PROCESSED_DIR / "main_candidate_pool_with_epss.parquet"
OUTPUT_CSV = PROCESSED_DIR / "main_candidate_pool_with_epss.csv"

LOG_FILE = AUDIT_DIR / "main_epss_enrichment_log.txt"

EPSS_URL = "https://epss.cyentia.com/epss_scores-current.csv.gz"
EPSS_FILE = EPSS_DIR / "epss_scores-current.csv.gz"


# ============================================================================
# Helpers
# ============================================================================

def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_log(message):
    print(message)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def pct(num, den):
    if den == 0:
        return 0.0
    return round((num / den) * 100, 2)


def coverage_summary(df, group_cols=None):
    if group_cols is None:
        total = len(df)
        covered = int(df["has_epss"].sum())
        missing = total - covered
        return pd.DataFrame([{
            "total_records": total,
            "has_epss": covered,
            "missing_epss": missing,
            "coverage_percent": pct(covered, total),
        }])

    rows = []

    grouped = df.groupby(group_cols, dropna=False)

    for keys, subset in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)

        total = len(subset)
        covered = int(subset["has_epss"].sum())
        missing = total - covered

        row = {}
        for col, value in zip(group_cols, keys):
            row[col] = value

        row.update({
            "total_records": total,
            "has_epss": covered,
            "missing_epss": missing,
            "coverage_percent": pct(covered, total),
        })

        rows.append(row)

    return pd.DataFrame(rows).sort_values(group_cols).reset_index(drop=True)


# ============================================================================
# Main
# ============================================================================

def main():
    LOG_FILE.write_text("", encoding="utf-8")

    enrichment_timestamp = utc_now()
    epss_source = f"FIRST_EPSS_daily_csv_current_downloaded_{enrichment_timestamp}"

    write_log("=" * 80)
    write_log("Starting Main Study EPSS enrichment")
    write_log("=" * 80)
    write_log(f"Input file: {INPUT_FILE}")
    write_log(f"EPSS URL: {EPSS_URL}")
    write_log(f"EPSS local file: {EPSS_FILE}")
    write_log(f"Enrichment timestamp: {enrichment_timestamp}")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input candidate pool not found: {INPUT_FILE}")

    write_log("\nLoading candidate pool...")
    candidate = pd.read_parquet(INPUT_FILE)

    required_cols = [
        "cve_id",
        "published_date",
        "official_severity",
        "cvss_selection_method",
    ]

    missing_cols = [col for col in required_cols if col not in candidate.columns]
    if missing_cols:
        raise ValueError(f"Candidate pool missing required columns: {missing_cols}")

    write_log(f"Candidate pool rows: {len(candidate)}")

    write_log("\nDownloading EPSS snapshot...")
    urlretrieve(EPSS_URL, EPSS_FILE)

    write_log("Loading EPSS snapshot...")
    epss = pd.read_csv(
        EPSS_FILE,
        compression="gzip",
        skiprows=1,
        dtype={"cve": str, "epss": float, "percentile": float},
    )

    required_epss_cols = ["cve", "epss", "percentile"]
    missing_epss_cols = [col for col in required_epss_cols if col not in epss.columns]
    if missing_epss_cols:
        raise ValueError(f"EPSS file missing required columns: {missing_epss_cols}")

    epss_subset = epss[["cve", "epss", "percentile"]].copy()
    epss_subset = epss_subset.rename(
        columns={
            "cve": "cve_id",
            "epss": "epss_score",
            "percentile": "epss_percentile",
        }
    )

    write_log(f"EPSS rows loaded: {len(epss_subset)}")

    write_log("\nMerging EPSS with candidate pool...")
    enriched = candidate.merge(
        epss_subset,
        on="cve_id",
        how="left",
        validate="one_to_one",
    )

    if len(enriched) != len(candidate):
        raise ValueError("Row count changed during EPSS merge. Stop and inspect.")

    enriched["has_epss"] = enriched["epss_score"].notna()
    enriched["epss_date"] = enrichment_timestamp
    enriched["epss_source"] = epss_source

    enriched["published_year"] = pd.to_datetime(
        enriched["published_date"], errors="coerce"
    ).dt.year

    enriched["is_nvd_grounded"] = enriched["cvss_selection_method"].isin(
        ["primary_type", "nvd_source"]
    )

    # ============================================================================
    # Coverage summaries
    # ============================================================================

    overall = coverage_summary(enriched)
    by_severity = coverage_summary(enriched, ["official_severity"])
    by_year = coverage_summary(enriched, ["published_year"])
    by_cvss_method = coverage_summary(enriched, ["cvss_selection_method"])
    by_severity_method = coverage_summary(
        enriched,
        ["official_severity", "cvss_selection_method"],
    )
    by_year_method = coverage_summary(
        enriched,
        ["published_year", "cvss_selection_method"],
    )

    nvd_grounded = enriched[enriched["is_nvd_grounded"] == True].copy()

    nvd_overall = coverage_summary(nvd_grounded)
    nvd_by_severity = coverage_summary(nvd_grounded, ["official_severity"])
    nvd_by_year = coverage_summary(nvd_grounded, ["published_year"])
    nvd_by_year_severity = coverage_summary(
        nvd_grounded,
        ["published_year", "official_severity"],
    )

    low_nvd = nvd_grounded[nvd_grounded["official_severity"] == "LOW"].copy()
    low_nvd_summary = coverage_summary(low_nvd)

    # ============================================================================
    # Save outputs
    # ============================================================================

    write_log("\nSaving enriched outputs...")
    enriched.to_parquet(OUTPUT_PARQUET, index=False)
    enriched.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    SUMMARY_XLSX = AUDIT_DIR / "main_epss_coverage_summary.xlsx"

    with pd.ExcelWriter(SUMMARY_XLSX, engine="openpyxl") as writer:
        overall.to_excel(writer, sheet_name="overall", index=False)
        by_severity.to_excel(writer, sheet_name="by_severity", index=False)
        by_year.to_excel(writer, sheet_name="by_year", index=False)
        by_cvss_method.to_excel(writer, sheet_name="by_cvss_method", index=False)
        by_severity_method.to_excel(writer, sheet_name="severity_method", index=False)
        by_year_method.to_excel(writer, sheet_name="year_method", index=False)
        nvd_overall.to_excel(writer, sheet_name="nvd_overall", index=False)
        nvd_by_severity.to_excel(writer, sheet_name="nvd_by_severity", index=False)
        nvd_by_year.to_excel(writer, sheet_name="nvd_by_year", index=False)
        nvd_by_year_severity.to_excel(writer, sheet_name="nvd_year_severity", index=False)
        low_nvd_summary.to_excel(writer, sheet_name="low_nvd_summary", index=False)

    # ============================================================================
    # Log summaries
    # ============================================================================

    write_log("=" * 80)
    write_log("EPSS Enrichment Summary")
    write_log("=" * 80)

    write_log("\nOverall EPSS coverage:")
    write_log(overall.to_string(index=False))

    write_log("\nEPSS coverage by severity:")
    write_log(by_severity.to_string(index=False))

    write_log("\nEPSS coverage by year:")
    write_log(by_year.to_string(index=False))

    write_log("\nEPSS coverage by CVSS selection method:")
    write_log(by_cvss_method.to_string(index=False))

    write_log("\nNVD-grounded EPSS coverage:")
    write_log(nvd_overall.to_string(index=False))

    write_log("\nNVD-grounded EPSS coverage by severity:")
    write_log(nvd_by_severity.to_string(index=False))

    write_log("\nNVD-grounded LOW severity EPSS coverage:")
    write_log(low_nvd_summary.to_string(index=False))

    write_log("\nOutputs:")
    write_log(f"Enriched Parquet: {OUTPUT_PARQUET}")
    write_log(f"Enriched CSV: {OUTPUT_CSV}")
    write_log(f"Coverage summary workbook: {SUMMARY_XLSX}")
    write_log(f"EPSS enrichment log: {LOG_FILE}")

    write_log("=" * 80)
    write_log("Main Study EPSS enrichment complete")
    write_log("=" * 80)


if __name__ == "__main__":
    main()