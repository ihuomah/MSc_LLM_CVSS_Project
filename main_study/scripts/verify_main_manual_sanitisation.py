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

MANUAL_REVIEW_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "sanitised"
    / "review"
    / "main_manual_review_v1.xlsx"
)

AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = AUDIT_DIR / "main_manual_sanitisation_verification_v1.xlsx"
LOG_FILE = AUDIT_DIR / "main_manual_sanitisation_verification_v1.txt"


def main():
    df = pd.read_parquet(INPUT_FILE)
    review = pd.read_excel(MANUAL_REVIEW_FILE)

    checks = []

    checks.append({
        "check": "row_count_is_1000",
        "result": len(df) == 1000,
        "details": f"rows={len(df)}",
    })

    checks.append({
        "check": "final_description_exists",
        "result": "final_description" in df.columns,
        "details": "final_description column present",
    })

    checks.append({
        "check": "final_description_no_nulls",
        "result": df["final_description"].notna().all(),
        "details": f"nulls={df['final_description'].isna().sum()}",
    })

    checks.append({
        "check": "final_description_no_empty_strings",
        "result": (df["final_description"].astype(str).str.strip() != "").all(),
        "details": f"empty={(df['final_description'].astype(str).str.strip() == '').sum()}",
    })

    checks.append({
        "check": "manual_redacted_column_exists",
        "result": "manually_redacted" in df.columns,
        "details": "manually_redacted column present",
    })

    manually_redacted_count = int(df["manually_redacted"].sum())

    checks.append({
        "check": "manual_redactions_applied",
        "result": manually_redacted_count > 0,
        "details": f"manually_redacted_count={manually_redacted_count}",
    })

    redactions = review[review["action"].astype(str).str.lower() == "redact"].copy()

    residual_rows = []

    for _, row in redactions.iterrows():
        cve_id = str(row["cve_id"])
        find_text = str(row["find_text"])

        matched = df[df["cve_id"].astype(str) == cve_id]

        if matched.empty:
            residual_rows.append({
                "cve_id": cve_id,
                "find_text": find_text,
                "status": "cve_not_found",
            })
            continue

        final_text = str(matched.iloc[0]["final_description"])

        if find_text and find_text in final_text:
            residual_rows.append({
                "cve_id": cve_id,
                "find_text": find_text,
                "status": "still_present",
            })

    residual_df = pd.DataFrame(residual_rows)

    checks.append({
        "check": "reviewed_find_text_not_present_in_final_description",
        "result": residual_df.empty,
        "details": f"remaining_reviewed_find_text={len(residual_df)}",
    })

    checks_df = pd.DataFrame(checks)

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        checks_df.to_excel(writer, sheet_name="checks", index=False)
        residual_df.to_excel(writer, sheet_name="remaining_find_text", index=False)

    log_text = []
    log_text.append("=" * 80)
    log_text.append("Manual Sanitisation Verification")
    log_text.append("=" * 80)
    log_text.append(checks_df.to_string(index=False))
    log_text.append("")
    log_text.append(f"Verification workbook: {OUTPUT_FILE}")

    if residual_df.empty:
        log_text.append("No reviewed find_text values remain in final_description.")
    else:
        log_text.append("WARNING: Some reviewed find_text values remain.")
        log_text.append(residual_df.to_string(index=False))

    LOG_FILE.write_text("\n".join(log_text), encoding="utf-8")

    print("\n".join(log_text))


if __name__ == "__main__":
    main()