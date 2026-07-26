import re
import pandas as pd

SANITISED_FILE = "data/processed/nvd_pilot_sanitised.xlsx"
REVIEW_FILE = "data/processed/pilot_manual_review.xlsx"

FINAL_FILE = "data/processed/nvd_pilot_final.xlsx"
LOG_FILE = "data/processed/manual_redaction_application_log.xlsx"


def apply_replacement(text, find_text, replacement_text, match_type):
    if not isinstance(text, str):
        return text, 0

    if match_type == "exact_case_sensitive":
        count = text.count(find_text)
        return text.replace(find_text, replacement_text), count

    elif match_type == "exact_case_insensitive":
        pattern = re.compile(re.escape(find_text), re.IGNORECASE)
        return pattern.subn(replacement_text, text)

    elif match_type == "regex":
        pattern = re.compile(find_text)
        return pattern.subn(replacement_text, text)

    else:
        raise ValueError(f"Unknown match_type: {match_type}")


df = pd.read_excel(SANITISED_FILE)
review = pd.read_excel(REVIEW_FILE)

review = review[review["action"].str.lower() == "redact"].copy()

df["final_description"] = df["sanitised_description"]
df["manually_redacted"] = False

logs = []

for cve_id, edits in review.groupby("cve_id"):
    index_matches = df.index[df["cve_id"] == cve_id].tolist()

    if not index_matches:
        logs.append({
            "cve_id": cve_id,
            "find_text": "",
            "replacement_text": "",
            "match_type": "",
            "replacements_made": 0,
            "status": "CVE not found"
        })
        continue

    idx = index_matches[0]

    edits = edits.sort_values(
        by="find_text",
        key=lambda col: col.astype(str).str.len(),
        ascending=False
    )

    text = df.at[idx, "final_description"]
    total_replacements_for_cve = 0

    for _, edit in edits.iterrows():
        find_text = str(edit["find_text"])
        replacement_text = str(edit["replacement_text"])
        match_type = str(edit["match_type"])

        text, count = apply_replacement(
            text,
            find_text,
            replacement_text,
            match_type
        )

        total_replacements_for_cve += count

        logs.append({
            "cve_id": cve_id,
            "find_text": find_text,
            "replacement_text": replacement_text,
            "match_type": match_type,
            "replacements_made": count,
            "status": "applied" if count > 0 else "zero replacements"
        })

    text = re.sub(r"\b(Vendor X)(\s+Vendor X)+\b", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()

    df.at[idx, "final_description"] = text

    if total_replacements_for_cve > 0:
        df.at[idx, "manually_redacted"] = True


log_df = pd.DataFrame(logs)

df.to_excel(FINAL_FILE, index=False)
log_df.to_excel(LOG_FILE, index=False)

print(f"\nFinal pilot dataset saved to:")
print(FINAL_FILE)

print(f"\nManual redaction log saved to:")
print(LOG_FILE)

print("\nSummary:")
print(f"Manual review rows processed: {len(review)}")
print(f"CVEs manually redacted: {df['manually_redacted'].sum()}")
print(f"Total replacements made: {log_df['replacements_made'].sum()}")

zero_count = (log_df["replacements_made"] == 0).sum()
print(f"Zero-replacement warnings: {zero_count}")

if zero_count > 0:
    print("\nRows with zero replacements:")
    print(log_df[log_df["replacements_made"] == 0])