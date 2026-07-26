from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "sanitised"
    / "main_dataset_sanitised_auto_v1.parquet"
)

REVIEW_DIR = PROJECT_ROOT / "main_study" / "datasets" / "sanitised" / "review"
AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"

REVIEW_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = REVIEW_DIR / "main_heavy_review_risk_flags.xlsx"
LOG_FILE = AUDIT_DIR / "main_heavy_review_risk_flags_log.txt"


def count_occurrences(text, phrase):
    if not isinstance(text, str):
        return 0
    return text.count(phrase)


def main():
    LOG_FILE.write_text("", encoding="utf-8")

    df = pd.read_parquet(INPUT_FILE).copy()

    df["original_length"] = df["original_description"].fillna("").astype(str).str.len()
    df["sanitised_length"] = df["sanitised_description"].fillna("").astype(str).str.len()

    df["length_ratio"] = df["sanitised_length"] / df["original_length"].replace(0, pd.NA)

    df["vendor_x_count"] = df["sanitised_description"].fillna("").astype(str).str.count("Vendor X")
    df["product_y_count"] = df["sanitised_description"].fillna("").astype(str).str.count("Product Y")

    df["placeholder_count"] = df["vendor_x_count"] + df["product_y_count"]

    df["flag_high_replacements"] = df["total_replacements"] >= 8
    df["flag_many_placeholders"] = df["placeholder_count"] >= 8
    df["flag_shortened_much"] = df["length_ratio"] < 0.75
    df["flag_repeated_vendor"] = df["sanitised_description"].fillna("").astype(str).str.contains(
        "Vendor X Vendor X",
        regex=False,
    )
    df["flag_repeated_product"] = df["sanitised_description"].fillna("").astype(str).str.contains(
        "Product Y Product Y",
        regex=False,
    )
    df["flag_mixed_placeholder_chain"] = df["sanitised_description"].fillna("").astype(str).str.contains(
        "Vendor X Product Y Product Y",
        regex=False,
    )

    flag_cols = [
        "flag_high_replacements",
        "flag_many_placeholders",
        "flag_shortened_much",
        "flag_repeated_vendor",
        "flag_repeated_product",
        "flag_mixed_placeholder_chain",
    ]

    df["risk_flag_count"] = df[flag_cols].sum(axis=1)

    flagged = df[df["risk_flag_count"] > 0].copy()

    flagged = flagged.sort_values(
        ["risk_flag_count", "total_replacements", "placeholder_count"],
        ascending=False,
    )

    review_cols = [
        "record_id",
        "cve_id",
        "official_severity",
        "published_year",
        "original_description",
        "sanitised_description",
        "total_replacements",
        "vendor_replacements",
        "product_replacements",
        "compound_replacements",
        "placeholder_count",
        "vendor_x_count",
        "product_y_count",
        "original_length",
        "sanitised_length",
        "length_ratio",
        "risk_flag_count",
    ] + flag_cols

    review_cols = [col for col in review_cols if col in flagged.columns]

    flagged[review_cols].to_excel(OUTPUT_FILE, index=False)

    log_text = (
        "Main Heavy Review Risk Flags\n"
        "============================\n"
        f"Input rows: {len(df)}\n"
        f"Flagged rows: {len(flagged)}\n"
        f"Output file: {OUTPUT_FILE}\n"
    )

    LOG_FILE.write_text(log_text, encoding="utf-8")

    print(log_text)
    print("Top flagged rows:")
    print(
        flagged[
            [
                "record_id",
                "cve_id",
                "total_replacements",
                "placeholder_count",
                "risk_flag_count",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()