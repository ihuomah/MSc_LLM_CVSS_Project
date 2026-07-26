from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "main_study" / "datasets" / "raw" / "main_candidate_pool_raw.xlsx"
OUTPUT_FILE = PROJECT_ROOT / "main_study" / "audit" / "main_excel_truncation_inspection.xlsx"

EXCEL_CELL_LIMIT = 32767


def main():
    df = pd.read_excel(INPUT_FILE)

    rows = []

    for col in df.columns:
        lengths = df[col].fillna("").astype(str).str.len()
        max_len = int(lengths.max()) if len(lengths) else 0
        over_limit = lengths > EXCEL_CELL_LIMIT

        rows.append({
            "column": col,
            "dtype": str(df[col].dtype),
            "max_length": max_len,
            "rows_over_excel_limit": int(over_limit.sum()),
            "example_cve_id": df.loc[lengths.idxmax(), "cve_id"] if "cve_id" in df.columns and len(lengths) else "",
            "example_length": max_len,
        })

    result = (
        pd.DataFrame(rows)
        .sort_values(by="max_length", ascending=False)
        .reset_index(drop=True)
    )

    result.to_excel(OUTPUT_FILE, index=False)

    print("=" * 80)
    print("Excel truncation inspection complete")
    print("=" * 80)
    print(result.head(20).to_string(index=False))
    print(f"\nSaved report to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()