from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "main_study" / "datasets" / "raw" / "main_candidate_pool_raw.parquet"

AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"
OUTPUT_FILE = AUDIT_DIR / "main_cvss_source_distribution.xlsx"

AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    df = pd.read_parquet(INPUT_FILE)

    df["published_year"] = pd.to_datetime(
        df["published_date"], errors="coerce"
    ).dt.year

    overall = (
        df["cvss_selection_method"]
        .value_counts(dropna=False)
        .reset_index()
    )
    overall.columns = ["cvss_selection_method", "count"]

    by_severity = pd.crosstab(
        df["official_severity"],
        df["cvss_selection_method"]
    )

    by_year = pd.crosstab(
        df["published_year"],
        df["cvss_selection_method"]
    )

    by_year_severity = (
        df.groupby(["published_year", "official_severity", "cvss_selection_method"])
        .size()
        .reset_index(name="count")
        .sort_values(["published_year", "official_severity", "cvss_selection_method"])
    )

    by_source_type = (
        df.groupby(["cvss_selection_method", "cvss_source", "cvss_type"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    low_only = df[df["official_severity"] == "LOW"].copy()

    low_by_year_method = pd.crosstab(
        low_only["published_year"],
        low_only["cvss_selection_method"]
    )

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        overall.to_excel(writer, sheet_name="overall", index=False)
        by_severity.to_excel(writer, sheet_name="by_severity")
        by_year.to_excel(writer, sheet_name="by_year")
        by_year_severity.to_excel(writer, sheet_name="year_severity_method", index=False)
        by_source_type.to_excel(writer, sheet_name="source_type", index=False)
        low_by_year_method.to_excel(writer, sheet_name="low_by_year_method")

    print("=" * 80)
    print("CVSS source distribution inspection complete")
    print("=" * 80)

    print("\nOverall CVSS selection method distribution:")
    print(overall.to_string(index=False))

    print("\nCVSS selection method by severity:")
    print(by_severity.to_string())

    print("\nCVSS selection method by year:")
    print(by_year.to_string())

    print("\nLOW severity by year and selection method:")
    print(low_by_year_method.to_string())

    print(f"\nSaved report to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()