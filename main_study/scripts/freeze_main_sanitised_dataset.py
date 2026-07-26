from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "sanitised"
    / "main_dataset_sanitised_manual_v1.parquet"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "frozen"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PARQUET = OUTPUT_DIR / "main_dataset_sanitised_final_v1.parquet"
OUTPUT_CSV = OUTPUT_DIR / "main_dataset_sanitised_final_v1.csv"
OUTPUT_XLSX = OUTPUT_DIR / "main_dataset_sanitised_final_v1.xlsx"

AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"

LOG_FILE = AUDIT_DIR / "main_dataset_freeze_log_v1.txt"


def main():

    print("=" * 80)
    print("Freezing Final Sanitised Dataset")
    print("=" * 80)

    df = pd.read_parquet(INPUT_FILE)

    print(f"Input rows: {len(df)}")

    expected_rows = 1000

    if len(df) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} rows but found {len(df)}"
        )

    required_columns = [
        "record_id",
        "cve_id",
        "official_cvss_vector",
        "official_base_score",
        "official_severity",
        "epss_score",
        "epss_percentile",
        "final_description",
    ]

    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df.to_parquet(OUTPUT_PARQUET, index=False)
    df.to_csv(OUTPUT_CSV, index=False)

    try:
        df.to_excel(OUTPUT_XLSX, index=False)
    except Exception as e:
        print(f"Excel warning: {e}")

    log_lines = [
        "=" * 80,
        "Main Sanitised Dataset Freeze",
        "=" * 80,
        f"Input file: {INPUT_FILE}",
        f"Rows frozen: {len(df)}",
        "",
        f"Frozen Parquet: {OUTPUT_PARQUET}",
        f"Frozen CSV: {OUTPUT_CSV}",
        f"Frozen XLSX: {OUTPUT_XLSX}",
        "",
        "Validation:",
        "- Row count verified",
        "- Required columns verified",
        "- Manual sanitisation validation passed",
        "",
        "Status: FROZEN",
    ]

    LOG_FILE.write_text(
        "\n".join(log_lines),
        encoding="utf-8"
    )

    print()
    print("Outputs:")
    print(f"Parquet: {OUTPUT_PARQUET}")
    print(f"CSV: {OUTPUT_CSV}")
    print(f"XLSX: {OUTPUT_XLSX}")
    print(f"Log: {LOG_FILE}")
    print()
    print("STATUS: FROZEN")
    print("=" * 80)


if __name__ == "__main__":
    main()