import re
from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "main_study" / "datasets" / "frozen" / "main_dataset_sanitised_final_v1.parquet"

REVIEW_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "sanitised"
    / "review"
    / "main_inference_leak_review_v1.xlsx"
)

OUTPUT_DIR = PROJECT_ROOT / "main_study" / "datasets" / "frozen"

OUTPUT_PARQUET = OUTPUT_DIR / "main_dataset_sanitised_final_v2.parquet"
OUTPUT_CSV = OUTPUT_DIR / "main_dataset_sanitised_final_v2.csv"
OUTPUT_XLSX = OUTPUT_DIR / "main_dataset_sanitised_final_v2.xlsx"

AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

LOG_XLSX = AUDIT_DIR / "main_inference_leak_redaction_log_v1.xlsx"
LOG_TXT = AUDIT_DIR / "main_inference_leak_redaction_log_v1.txt"


def apply_replacement(text, find_text, replacement_text, match_type):
    if not isinstance(text, str):
        return text, 0

    if not isinstance(find_text, str) or not find_text.strip():
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
    return re.sub(r"\s+", " ", text).strip()


def main():
    LOG_TXT.write_text("", encoding="utf-8")

    def log(message):
        print(message)
        with LOG_TXT.open("a", encoding="utf-8") as f:
            f.write(message + "\n")

    log("=" * 80)
    log("Applying Inference Leakage Redactions")
    log("=" * 80)

    df = pd.read_parquet(INPUT_FILE)
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
        raise ValueError(f"Review file missing required columns: {missing}")

    review = review[review["action"].astype(str).str.lower() == "redact"].copy()

    if "final_description" not in df.columns:
        raise ValueError("Input dataset does not contain final_description.")

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

            logs.append({
                "cve_id": cve_id,
                "find_text": find_text,
                "replacement_text": replacement_text,
                "match_type": match_type,
                "reason": reason,
                "replacements_made": count,
                "status": "applied" if count > 0 else "zero replacements",
            })

        df.at[idx, "final_description"] = clean_text(text)

    log_df = pd.DataFrame(logs)

    df.to_parquet(OUTPUT_PARQUET, index=False)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    df.to_excel(OUTPUT_XLSX, index=False)
    log_df.to_excel(LOG_XLSX, index=False)

    total_replacements = int(log_df["replacements_made"].sum())
    zero_replacements = int((log_df["replacements_made"] == 0).sum())

    log("\nSummary")
    log(f"Review rows processed: {len(review)}")
    log(f"Total replacements made: {total_replacements}")
    log(f"Zero-replacement warnings: {zero_replacements}")

    log("\nOutputs:")
    log(f"Updated frozen Parquet: {OUTPUT_PARQUET}")
    log(f"Updated frozen CSV: {OUTPUT_CSV}")
    log(f"Updated frozen XLSX: {OUTPUT_XLSX}")
    log(f"Log XLSX: {LOG_XLSX}")
    log(f"Log TXT: {LOG_TXT}")

    if zero_replacements > 0:
        log("\nWARNING: Inspect zero-replacement rows before proceeding.")

    log("=" * 80)
    log("Inference Leakage Redaction Complete")
    log("=" * 80)


if __name__ == "__main__":
    main()