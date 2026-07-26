from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PARQUET_FILE = PROJECT_ROOT / "main_study" / "datasets" / "frozen" / "main_dataset_frozen_v1.parquet"
CSV_FILE = PROJECT_ROOT / "main_study" / "datasets" / "frozen" / "main_dataset_frozen_v1.csv"

OUTPUT_FILE = PROJECT_ROOT / "main_study" / "audit" / "main_frozen_cpe_length_check.xlsx"


def build_summary(df, source_name):
    rows = []

    for col in ["cpe_vendors", "cpe_products", "cpe_uris"]:
        lengths = df[col].fillna("").astype(str).str.len()

        rows.append({
            "source": source_name,
            "column": col,
            "max_length": int(lengths.max()),
            "rows_over_excel_limit": int((lengths > 32767).sum()),
            "example_cve_id": df.loc[lengths.idxmax(), "cve_id"],
            "example_length": int(lengths.max()),
        })

    return pd.DataFrame(rows)


def main():
    parquet_df = pd.read_parquet(PARQUET_FILE)
    csv_df = pd.read_csv(CSV_FILE)

    parquet_summary = build_summary(parquet_df, "parquet")
    csv_summary = build_summary(csv_df, "csv")

    summary = pd.concat([parquet_summary, csv_summary], ignore_index=True)

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="summary", index=False)

    print("=" * 80)
    print("Frozen CPE length verification")
    print("=" * 80)
    print(summary.to_string(index=False))
    print(f"\nSaved report to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()