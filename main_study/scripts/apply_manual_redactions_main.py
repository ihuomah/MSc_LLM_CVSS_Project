import re
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

REVIEW_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "sanitised"
    / "review"
    / "main_manual_review_v1.xlsx"
)

OUTPUT_PARQUET = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "sanitised"
    / "main_dataset_sanitised_manual_v1.parquet"
)

OUTPUT_CSV = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "sanitised"
    / "main_dataset_sanitised_manual_v1.csv"
)

OUTPUT_XLSX = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "sanitised"
    / "main_dataset_sanitised_manual_v1.xlsx"
)

AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

LOG_XLSX = AUDIT_DIR / "main_manual_redaction_application_log_v1.xlsx"
LOG_TXT = AUDIT_DIR / "main_manual_redaction_application_log_v1.txt"


def apply_replacement(text, find_text, replacement_text, match_type):
    if not isinstance(text, str):
        return text, 0

    if not isinstance(find_text, str) or find_text == "":
        return text, 0

    if match_type == "exact_case_sensitive":
        count = text.count(find_text)
        return text.replace(find_text, replacement_text), count

    if match_type == "exact_case_insensitive":
        pattern = re.compile(re.escape(find_text), re.IGNORECASE)
        return pattern.subn(replacement_text, text)

    if match_type == "regex":
        pattern = re.compile(find_text)
        return pattern.subn(replacement_text, text)

    raise ValueError(f"Unknown match_type: {match_type}")


def clean_text(text):
    if not isinstance(text, str):
        return text

    text = re.sub(r"\b(Vendor X)(\s+Vendor X)+\b", r"\1", text)
    text = re.sub(r"\b(Product Y)(\s+Product Y)+\b", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def main():
    LOG_TXT.write_text("", encoding="utf-8")

    def log(message):
        print(message)
        with LOG_TXT.open("a", encoding="utf-8") as f:
            f.write(message + "\n")

    log("=" * 80)
    log("Starting Manual Redaction Application")
    log("=" * 80)

    df = pd.read_parquet(INPUT_FILE)

    if not REVIEW_FILE.exists():
        raise FileNotFoundError(f"Manual review file not found: {REVIEW_FILE}")

    review = pd.read_excel(REVIEW_FILE)

    required_cols = [
        "cve_id",
        "action",
        "find_text",
        "replacement_text",
        "match_type",
        "reason",
    ]

    missing = [col for col in required_cols if col not in review.columns]
    if missing:
        raise ValueError(f"Manual review file missing required columns: {missing}")

    review = review[review["action"].astype(str).str.lower() == "redact"].copy()

    df["final_description"] = df["sanitised_description"]
    df["manually_redacted"] = False

    logs = []

    for cve_id, edits in review.groupby("cve_id"):
        index_matches = df.index[df["cve_id"].astype(str) == str(cve_id)].tolist()

        if not index_matches:
            for _, edit in edits.iterrows():
                logs.append({
                    "cve_id": cve_id,
                    "find_text": edit.get("find_text", ""),
                    "replacement_text": edit.get("replacement_text", ""),
                    "match_type": edit.get("match_type", ""),
                    "reason": edit.get("reason", ""),
                    "replacements_made": 0,
                    "status": "CVE not found",
                })
            continue

        idx = index_matches[0]

        edits = edits.sort_values(
            by="find_text",
            key=lambda col: col.astype(str).str.len(),
            ascending=False,
        )

        text = df.at[idx, "final_description"]
        total_replacements_for_cve = 0

        for _, edit in edits.iterrows():
            find_text = str(edit["find_text"])
            replacement_text = str(edit["replacement_text"])
            match_type = str(edit["match_type"])
            reason = str(edit["reason"])

            text, count = apply_replacement(
                text,
                find_text,
                replacement_text,
                match_type,
            )

            total_replacements_for_cve += count

            logs.append({
                "cve_id": cve_id,
                "find_text": find_text,
                "replacement_text": replacement_text,
                "match_type": match_type,
                "reason": reason,
                "replacements_made": count,
                "status": "applied" if count > 0 else "zero replacements",
            })

        text = clean_text(text)

        df.at[idx, "final_description"] = text

        if total_replacements_for_cve > 0:
            df.at[idx, "manually_redacted"] = True

    log_df = pd.DataFrame(logs)

    df.to_parquet(OUTPUT_PARQUET, index=False)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    df.to_excel(OUTPUT_XLSX, index=False)
    log_df.to_excel(LOG_XLSX, index=False)

    total_review_rows = len(review)
    total_redacted_cves = int(df["manually_redacted"].sum())
    total_replacements = int(log_df["replacements_made"].sum()) if not log_df.empty else 0
    zero_replacements = int((log_df["replacements_made"] == 0).sum()) if not log_df.empty else 0

    log("\nManual Redaction Summary")
    log(f"Manual review rows processed: {total_review_rows}")
    log(f"CVEs manually redacted: {total_redacted_cves}")
    log(f"Total replacements made: {total_replacements}")
    log(f"Zero-replacement warnings: {zero_replacements}")

    log("\nOutputs:")
    log(f"Manual sanitised Parquet: {OUTPUT_PARQUET}")
    log(f"Manual sanitised CSV: {OUTPUT_CSV}")
    log(f"Manual sanitised XLSX: {OUTPUT_XLSX}")
    log(f"Application log XLSX: {LOG_XLSX}")
    log(f"Application log TXT: {LOG_TXT}")

    if zero_replacements > 0:
        log("\nWARNING: Some manual review rows made zero replacements.")
        log("Inspect the application log before freezing the dataset.")

    log("=" * 80)
    log("Manual Redaction Application Complete")
    log("=" * 80)


if __name__ == "__main__":
    main()