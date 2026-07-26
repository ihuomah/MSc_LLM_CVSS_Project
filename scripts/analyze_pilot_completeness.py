import pandas as pd
from pathlib import Path

INPUT_FILE = Path("results/pilot/raw_results/pilot_run_001_results.xlsx")
OUTPUT_DIR = Path("results/pilot/analysis/completeness")

SUMMARY_FILE = OUTPUT_DIR / "completeness_summary.xlsx"
REPORT_FILE = OUTPUT_DIR / "completeness_report.md"

EXPECTED_RECORDS = 50
EXPECTED_PROVIDERS = ["ollama", "openai", "gemini"]
EXPECTED_CONDITIONS = ["conventional", "structured"]
EXPECTED_ROWS = EXPECTED_RECORDS * len(EXPECTED_PROVIDERS) * len(EXPECTED_CONDITIONS)

VECTOR_SCORE_TOLERANCE = 0.15
COMPLIANCE_CATEGORIES = ["strict", "fenced", "embedded", "invalid"]


def pct(numerator, denominator):
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def load_results():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_excel(INPUT_FILE)

    required_columns = [
        "record_id",
        "model_name",
        "prompt_condition",
        "parse_success",
        "compliance_category",
        "vector_score_consistent",
        "predicted_vector",
        "predicted_base_score",
        "retry_count",
        "total_retry_wait_ms",
        "inference_latency_ms",
        "error_type",
        "error_message",
        "raw_response_file",
        "parsed_output_file",
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def create_overall_summary(df):
    actual_rows = len(df)
    parsed = int(df["parse_success"].fillna(False).sum())
    failed = actual_rows - parsed
    total_retries = int(df["retry_count"].fillna(0).sum())
    rows_with_retries = int((df["retry_count"].fillna(0) > 0).sum())

    return pd.DataFrame(
        [
            {
                "expected_rows": EXPECTED_ROWS,
                "actual_rows": actual_rows,
                "missing_rows": EXPECTED_ROWS - actual_rows,
                "parse_successes": parsed,
                "parse_failures": failed,
                "overall_parse_rate_percent": pct(parsed, actual_rows),
                "total_retries": total_retries,
                "rows_with_retries": rows_with_retries,
            }
        ]
    )


def create_parse_summary(df):
    rows = []

    for provider in EXPECTED_PROVIDERS:
        for condition in EXPECTED_CONDITIONS:
            subset = df[
                (df["model_name"] == provider)
                & (df["prompt_condition"] == condition)
            ]

            total = len(subset)
            parsed = int(subset["parse_success"].fillna(False).sum())
            failed = total - parsed
            invalid = int((subset["compliance_category"] == "invalid").sum())
            failed_other = failed - invalid

            rows.append(
                {
                    "provider": provider,
                    "condition": condition,
                    "total_rows": total,
                    "parsed": parsed,
                    "failed": failed,
                    "failed_invalid": invalid,
                    "failed_other": failed_other,
                    "parse_rate_percent": pct(parsed, total),
                }
            )

    return pd.DataFrame(rows)


def create_compliance_summary(df):
    rows = []

    for provider in EXPECTED_PROVIDERS:
        for condition in EXPECTED_CONDITIONS:
            subset = df[
                (df["model_name"] == provider)
                & (df["prompt_condition"] == condition)
            ]

            row = {
                "provider": provider,
                "condition": condition,
            }

            for category in COMPLIANCE_CATEGORIES:
                row[category] = int((subset["compliance_category"] == category).sum())

            known_total = sum(row[category] for category in COMPLIANCE_CATEGORIES)
            row["other"] = len(subset) - known_total

            rows.append(row)

    return pd.DataFrame(rows)


def create_vector_score_summary(df):
    rows = []

    for provider in EXPECTED_PROVIDERS:
        for condition in EXPECTED_CONDITIONS:
            subset = df[
                (df["model_name"] == provider)
                & (df["prompt_condition"] == condition)
            ]

            checkable = subset[
                subset["predicted_vector"].notna()
                & subset["predicted_base_score"].notna()
                & subset["vector_score_consistent"].notna()
            ]

            total_checkable = len(checkable)
            consistent = int((checkable["vector_score_consistent"] == True).sum())
            inconsistent = int((checkable["vector_score_consistent"] == False).sum())

            rows.append(
                {
                    "provider": provider,
                    "condition": condition,
                    "rows_with_valid_vector_and_score": total_checkable,
                    "consistent": consistent,
                    "inconsistent": inconsistent,
                    "consistency_rate_percent": pct(consistent, total_checkable),
                    "tolerance_used": VECTOR_SCORE_TOLERANCE,
                }
            )

    return pd.DataFrame(rows)


def create_retry_summary(df):
    rows = []

    for provider in EXPECTED_PROVIDERS:
        for condition in EXPECTED_CONDITIONS:
            subset = df[
                (df["model_name"] == provider)
                & (df["prompt_condition"] == condition)
            ]

            retry_count = subset["retry_count"].fillna(0)
            retry_wait = subset["total_retry_wait_ms"].fillna(0)

            rows.append(
                {
                    "provider": provider,
                    "condition": condition,
                    "total_retry_count": int(retry_count.sum()),
                    "rows_with_retry": int((retry_count > 0).sum()),
                    "max_retry_count": int(retry_count.max()) if len(retry_count) else 0,
                    "total_retry_wait_ms": int(retry_wait.sum()),
                }
            )

    return pd.DataFrame(rows)


def create_latency_summary(df):
    rows = []

    for provider in EXPECTED_PROVIDERS:
        for condition in EXPECTED_CONDITIONS:
            subset = df[
                (df["model_name"] == provider)
                & (df["prompt_condition"] == condition)
            ]

            latency = pd.to_numeric(subset["inference_latency_ms"], errors="coerce").dropna()

            rows.append(
                {
                    "provider": provider,
                    "condition": condition,
                    "mean_latency_ms": round(latency.mean(), 2) if len(latency) else None,
                    "median_latency_ms": round(latency.median(), 2) if len(latency) else None,
                    "min_latency_ms": int(latency.min()) if len(latency) else None,
                    "max_latency_ms": int(latency.max()) if len(latency) else None,
                    "std_dev_latency_ms": round(latency.std(), 2) if len(latency) > 1 else 0,
                }
            )

    return pd.DataFrame(rows)


def create_failure_inventory(df):
    failures = df[
        (df["parse_success"] != True)
        | (df["compliance_category"] == "invalid")
        | (df["error_type"].notna())
    ].copy()

    columns = [
        "record_id",
        "model_name",
        "prompt_condition",
        "parse_success",
        "compliance_category",
        "error_type",
        "error_message",
        "raw_response_file",
        "parsed_output_file",
    ]

    return failures[columns].sort_values(
        by=["record_id", "model_name", "prompt_condition"]
    )


def create_per_record_failure_summary(df):
    temp = df.copy()
    temp["is_failure"] = (
        (temp["parse_success"] != True)
        | (temp["compliance_category"] == "invalid")
        | (temp["error_type"].notna())
    )

    summary = (
        temp.groupby("record_id")
        .agg(
            total_inferences=("record_id", "count"),
            failed_inferences=("is_failure", "sum"),
        )
        .reset_index()
    )

    summary["successful_inferences"] = (
        summary["total_inferences"] - summary["failed_inferences"]
    )

    return summary.sort_values(by=["failed_inferences", "record_id"], ascending=[False, True])


def dataframe_to_markdown(df):
    if df.empty:
        return "_No rows._"
    return df.to_markdown(index=False)


def write_markdown_report(
    overall,
    parse_summary,
    compliance_summary,
    vector_score_summary,
    retry_summary,
    latency_summary,
    failure_inventory,
    per_record_failure_summary,
):
    lines = []

    lines.append("# Pilot Completeness Report\n")
    lines.append("## Purpose\n")
    lines.append(
        "This report summarises the completeness and internal reliability of the 50-record pilot run. "
        "It does not compare model outputs against ground-truth CVSS values or EPSS scores.\n"
    )

    lines.append("## Summary\n")
    row = overall.iloc[0]
    lines.append(
        f"The pilot expected {row['expected_rows']} inference rows and produced {row['actual_rows']} rows. "
        f"There were {row['parse_successes']} successful parses and {row['parse_failures']} parse failure(s), "
        f"giving an overall parse rate of {row['overall_parse_rate_percent']}%. "
        f"No ground-truth accuracy claims are made in this report.\n"
    )

    lines.append("## Table 1: Overall Pilot Completion\n")
    lines.append(dataframe_to_markdown(overall))
    lines.append("\n")

    lines.append("## Table 2: Provider × Condition Parse Summary\n")
    lines.append(dataframe_to_markdown(parse_summary))
    lines.append("\n")

    lines.append("## Table 3: Compliance Category Summary\n")
    lines.append(dataframe_to_markdown(compliance_summary))
    lines.append("\n")

    lines.append("## Table 4: Vector-Score Consistency Summary\n")
    lines.append(
        f"Vector-score consistency was assessed only where both a predicted vector and predicted base score were available. "
        f"The tolerance used was ±{VECTOR_SCORE_TOLERANCE}.\n"
    )
    lines.append(dataframe_to_markdown(vector_score_summary))
    lines.append("\n")

    lines.append("## Table 5: Retry Summary\n")
    lines.append(dataframe_to_markdown(retry_summary))
    lines.append("\n")

    lines.append("## Table 6: Latency Summary\n")
    lines.append(dataframe_to_markdown(latency_summary))
    lines.append("\n")

    lines.append("## Table 7: Failure Inventory\n")
    lines.append(dataframe_to_markdown(failure_inventory))
    lines.append("\n")

    lines.append("## Table 8: Per-Record Failure Summary\n")
    lines.append(dataframe_to_markdown(per_record_failure_summary))
    lines.append("\n")

    lines.append("## Methodological Notes\n")
    lines.append(
        "- This report evaluates pilot completeness, parseability, compliance category, retry behaviour, latency, and internal vector-score consistency.\n"
        "- It does not evaluate correctness against official CVSS vectors or EPSS values.\n"
        "- Compliance categories are expected to be: strict, fenced, embedded, and invalid.\n"
        "- Failed or invalid rows are retained as observed data and are not re-run or manually repaired.\n"
    )

    lines.append("\n## Research Question Mapping\n")
    lines.append(
        "These completeness metrics primarily support RQ4 and RQ5 by documenting reliability, stability, output-format compliance, and observed failure modes under different prompting strategies.\n"
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_results()

    overall = create_overall_summary(df)
    parse_summary = create_parse_summary(df)
    compliance_summary = create_compliance_summary(df)
    vector_score_summary = create_vector_score_summary(df)
    retry_summary = create_retry_summary(df)
    latency_summary = create_latency_summary(df)
    failure_inventory = create_failure_inventory(df)
    per_record_failure_summary = create_per_record_failure_summary(df)

    with pd.ExcelWriter(SUMMARY_FILE, engine="openpyxl") as writer:
        overall.to_excel(writer, sheet_name="overall", index=False)
        parse_summary.to_excel(writer, sheet_name="parse_summary", index=False)
        compliance_summary.to_excel(writer, sheet_name="compliance", index=False)
        vector_score_summary.to_excel(writer, sheet_name="vector_consistency", index=False)
        retry_summary.to_excel(writer, sheet_name="retries", index=False)
        latency_summary.to_excel(writer, sheet_name="latency", index=False)
        failure_inventory.to_excel(writer, sheet_name="failures", index=False)
        per_record_failure_summary.to_excel(writer, sheet_name="record_failures", index=False)

    write_markdown_report(
        overall,
        parse_summary,
        compliance_summary,
        vector_score_summary,
        retry_summary,
        latency_summary,
        failure_inventory,
        per_record_failure_summary,
    )

    print("=" * 80)
    print("Pilot completeness analysis complete")
    print("=" * 80)
    print(f"Input file: {INPUT_FILE}")
    print(f"Excel summary written to: {SUMMARY_FILE}")
    print(f"Markdown report written to: {REPORT_FILE}")


if __name__ == "__main__":
    main()