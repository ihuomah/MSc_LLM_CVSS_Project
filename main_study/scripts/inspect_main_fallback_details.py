from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "main_study" / "datasets" / "raw" / "main_candidate_pool_raw.parquet"

AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"
OUTPUT_FILE = AUDIT_DIR / "main_fallback_cvss_details.xlsx"

AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    df = pd.read_parquet(INPUT_FILE)

    fallback = df[df["cvss_selection_method"] == "fallback_first_available"].copy()

    overall = pd.DataFrame([{
        "total_candidate_pool": len(df),
        "fallback_records": len(fallback),
        "fallback_percent": round((len(fallback) / len(df)) * 100, 2) if len(df) else 0,
    }])

    source_type_counts = (
        fallback
        .groupby(["cvss_source", "cvss_type", "cvss_version"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    fallback["published_year"] = pd.to_datetime(
        fallback["published_date"], errors="coerce"
    ).dt.year

    by_year_source_type = (
        fallback
        .groupby(["published_year", "cvss_source", "cvss_type", "cvss_version"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["published_year", "count"], ascending=[True, False])
    )

    by_severity_source_type = (
        fallback
        .groupby(["official_severity", "cvss_source", "cvss_type", "cvss_version"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["official_severity", "count"], ascending=[True, False])
    )

    fallback_examples = fallback[[
        "cve_id",
        "published_date",
        "official_severity",
        "official_cvss_vector",
        "official_base_score",
        "cvss_source",
        "cvss_type",
        "cvss_version",
        "cvss_selection_method",
    ]].head(100)

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        overall.to_excel(writer, sheet_name="overall", index=False)
        source_type_counts.to_excel(writer, sheet_name="source_type_counts", index=False)
        by_year_source_type.to_excel(writer, sheet_name="by_year_source_type", index=False)
        by_severity_source_type.to_excel(writer, sheet_name="by_severity_source_type", index=False)
        fallback_examples.to_excel(writer, sheet_name="fallback_examples", index=False)

    print("=" * 80)
    print("Fallback CVSS inspection complete")
    print("=" * 80)

    print("\nOverall:")
    print(overall.to_string(index=False))

    print("\nFallback source/type/version counts:")
    print(source_type_counts.head(30).to_string(index=False))

    print(f"\nSaved report to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()