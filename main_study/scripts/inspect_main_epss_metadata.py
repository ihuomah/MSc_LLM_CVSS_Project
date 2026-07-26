from pathlib import Path
import gzip

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EPSS_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "raw"
    / "epss"
    / "epss_scores-current.csv.gz"
)

OUTPUT_FILE = PROJECT_ROOT / "main_study" / "audit" / "main_epss_snapshot_metadata.txt"


def main():
    with gzip.open(EPSS_FILE, "rt", encoding="utf-8") as f:
        header_line = f.readline().strip()
        columns_line = f.readline().strip()

    text = (
        "Main Study EPSS Snapshot Metadata\n"
        "=================================\n"
        f"EPSS file: {EPSS_FILE}\n"
        f"Header line: {header_line}\n"
        f"Columns line: {columns_line}\n"
    )

    OUTPUT_FILE.write_text(text, encoding="utf-8")

    print(text)
    print(f"Saved metadata to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()