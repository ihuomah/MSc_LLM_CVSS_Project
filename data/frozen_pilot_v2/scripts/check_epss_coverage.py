import pandas as pd
from pathlib import Path
from urllib.request import urlretrieve


PILOT_DATASET = Path("data/frozen_pilot_v1/datasets/nvd_pilot_raw.xlsx")

EPSS_DIR = Path("data/epss")
EPSS_DIR.mkdir(parents=True, exist_ok=True)

EPSS_URL = "https://epss.cyentia.com/epss_scores-current.csv.gz"
EPSS_FILE = EPSS_DIR / "epss_scores-current.csv.gz"


def main():
    print("Loading pilot dataset...")
    pilot = pd.read_excel(PILOT_DATASET)

    if "cve_id" not in pilot.columns:
        raise ValueError("Column 'cve_id' not found in pilot dataset.")

    print(f"Pilot records: {len(pilot)}")

    print("Downloading current EPSS CSV...")
    urlretrieve(EPSS_URL, EPSS_FILE)

    print("Loading EPSS data...")
    epss = pd.read_csv(EPSS_FILE, compression="gzip", skiprows=1)

    if "cve" not in epss.columns:
        raise ValueError("Column 'cve' not found in EPSS dataset.")

    pilot_cves = set(pilot["cve_id"].astype(str))
    epss_cves = set(epss["cve"].astype(str))

    has_epss = pilot["cve_id"].astype(str).isin(epss_cves)

    total = len(pilot)
    covered = int(has_epss.sum())
    missing = total - covered
    coverage_pct = (covered / total) * 100 if total > 0 else 0

    print("=" * 80)
    print("EPSS Coverage Report")
    print("=" * 80)
    print(f"Pilot records: {total}")
    print(f"Has EPSS: {covered}")
    print(f"Missing EPSS: {missing}")
    print(f"Coverage: {coverage_pct:.2f}%")

    missing_cves = pilot.loc[~has_epss, "cve_id"].tolist()

    if missing_cves:
        print("\nMissing CVEs:")
        for cve in missing_cves:
            print(f"- {cve}")

    output_report = EPSS_DIR / "pilot_epss_coverage_report.txt"

    with open(output_report, "w", encoding="utf-8") as f:
        f.write("EPSS Coverage Report\n")
        f.write("=" * 80 + "\n")
        f.write(f"Pilot records: {total}\n")
        f.write(f"Has EPSS: {covered}\n")
        f.write(f"Missing EPSS: {missing}\n")
        f.write(f"Coverage: {coverage_pct:.2f}%\n")

        if missing_cves:
            f.write("\nMissing CVEs:\n")
            for cve in missing_cves:
                f.write(f"- {cve}\n")

    print(f"\nCoverage report saved to: {output_report}")


if __name__ == "__main__":
    main()