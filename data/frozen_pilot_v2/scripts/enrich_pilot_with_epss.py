from pathlib import Path
from datetime import datetime, timezone
import pandas as pd


PILOT_V1 = Path("data/frozen_pilot_v1/datasets/nvd_pilot_raw.xlsx")
EPSS_FILE = Path("data/epss/epss_scores-current.csv.gz")

OUTPUT_DIR = Path("data/enriched_pilot_v2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_DATASET = OUTPUT_DIR / "nvd_pilot_raw_with_epss_v2.xlsx"
OUTPUT_COVERAGE_LOG = OUTPUT_DIR / "epss_enrichment_log_v2.txt"


def main():
    enrichment_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    epss_source = f"FIRST_EPSS_daily_csv_current_downloaded_{enrichment_timestamp}"

    print("Loading frozen pilot v1...")
    pilot = pd.read_excel(PILOT_V1)

    print("Loading EPSS CSV...")
    epss = pd.read_csv(
        EPSS_FILE,
        compression="gzip",
        skiprows=1,
        dtype={"cve": str, "epss": float, "percentile": float},
    )

    print("Preparing EPSS fields...")
    epss_subset = epss[["cve", "epss", "percentile"]].copy()
    epss_subset = epss_subset.rename(
        columns={
            "cve": "cve_id",
            "epss": "epss_score",
            "percentile": "epss_percentile",
        }
    )

    print("Merging EPSS with frozen pilot v1...")
    enriched = pilot.merge(epss_subset, on="cve_id", how="left")

    enriched["has_epss"] = enriched["epss_score"].notna()
    enriched["epss_date"] = enrichment_timestamp
    enriched["epss_source"] = epss_source

    total = len(enriched)
    covered = int(enriched["has_epss"].sum())
    missing = total - covered
    coverage_pct = (covered / total) * 100 if total else 0

    print("=" * 80)
    print("EPSS Enrichment Summary")
    print("=" * 80)
    print(f"Input dataset: {PILOT_V1}")
    print(f"EPSS file: {EPSS_FILE}")
    print(f"Output dataset: {OUTPUT_DATASET}")
    print(f"Pilot records: {total}")
    print(f"Has EPSS: {covered}")
    print(f"Missing EPSS: {missing}")
    print(f"Coverage: {coverage_pct:.2f}%")
    print(f"EPSS timestamp: {enrichment_timestamp}")

    enriched.to_excel(OUTPUT_DATASET, index=False)

    with open(OUTPUT_COVERAGE_LOG, "w", encoding="utf-8") as f:
        f.write("EPSS Enrichment Log v2\n")
        f.write("=" * 80 + "\n")
        f.write(f"Input dataset: {PILOT_V1}\n")
        f.write(f"EPSS file: {EPSS_FILE}\n")
        f.write(f"Output dataset: {OUTPUT_DATASET}\n")
        f.write(f"Pilot records: {total}\n")
        f.write(f"Has EPSS: {covered}\n")
        f.write(f"Missing EPSS: {missing}\n")
        f.write(f"Coverage: {coverage_pct:.2f}%\n")
        f.write(f"EPSS timestamp: {enrichment_timestamp}\n")
        f.write(f"EPSS source: {epss_source}\n")

        if missing > 0:
            f.write("\nMissing CVEs:\n")
            missing_cves = enriched.loc[~enriched["has_epss"], "cve_id"].tolist()
            for cve in missing_cves:
                f.write(f"- {cve}\n")

    print(f"\nSaved enriched dataset to: {OUTPUT_DATASET}")
    print(f"Saved enrichment log to: {OUTPUT_COVERAGE_LOG}")


if __name__ == "__main__":
    main()