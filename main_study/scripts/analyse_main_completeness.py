import numpy as np
import pandas as pd
from pathlib import Path

INPUT_FILE = Path("main_study/results/raw_results/run_001_results.parquet")
OUTPUT_DIR = Path("main_study/results/analysis/completeness")

SUMMARY_FILE = OUTPUT_DIR / "main_completeness_summary.xlsx"
REPORT_FILE = OUTPUT_DIR / "main_completeness_report.md"

EXPECTED_RECORDS = 1000
EXPECTED_PROVIDERS = ["openai", "gemini", "ollama"]
EXPECTED_CONDITIONS = ["conventional", "structured"]
EXPECTED_ROWS = EXPECTED_RECORDS * len(EXPECTED_PROVIDERS) * len(EXPECTED_CONDITIONS)

COMPLIANCE_CATEGORIES = [
    "strict",
    "fenced",
    "embedded",
    "invalid",
    "parser_exception",
]


def pct(numerator, denominator):
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def safe_bool(series):
    return series.fillna(False).astype(bool)


def dataframe_to_markdown(df):
    if df.empty:
        return "_No rows._"
    try:
        return df.to_markdown(index=False)
    except ImportError:
        return df.to_string(index=False)


def load_results():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_parquet(INPUT_FILE)

    required_columns = [
        "record_id",
        "model_name",
        "prompt_condition",
        "api_success",
        "parse_success",
        "compliance_category",
        "predicted_vector",
        "predicted_base_score",
        "vector_score_consistent",
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

    api_ok = safe_bool(df["api_success"])
    parse_ok = safe_bool(df["parse_success"])

    df["state"] = np.select(
        [
            api_ok & parse_ok,
            api_ok & ~parse_ok,
        ],
        [
            "S1_api_success_parse_success",
            "S2_api_success_parse_failure_rq5",
        ],
        default="S3_api_failure",
    )

    return df


def create_overall_summary(df):
    actual_rows = len(df)
    distinct_records = df["record_id"].nunique()

    api_ok = safe_bool(df["api_success"])
    parse_ok = safe_bool(df["parse_success"])

    api_successes = int(api_ok.sum())
    api_failures = int((~api_ok).sum())

    parse_successes = int(parse_ok.sum())
    parse_failures = int((~parse_ok).sum())

    s1_clean = int((df["state"] == "S1_api_success_parse_success").sum())
    s2_rq5 = int((df["state"] == "S2_api_success_parse_failure_rq5").sum())
    s3_api_failure = int((df["state"] == "S3_api_failure").sum())

    total_retries = int(pd.to_numeric(df["retry_count"], errors="coerce").fillna(0).sum())
    rows_with_retries = int((pd.to_numeric(df["retry_count"], errors="coerce").fillna(0) > 0).sum())

    return pd.DataFrame([{
        "expected_rows": EXPECTED_ROWS,
        "actual_rows": actual_rows,
        "row_count_pass": actual_rows == EXPECTED_ROWS,
        "expected_distinct_records": EXPECTED_RECORDS,
        "actual_distinct_records": distinct_records,
        "distinct_record_count_pass": distinct_records == EXPECTED_RECORDS,
        "api_successes": api_successes,
        "api_failures": api_failures,
        "api_failure_pass": api_failures == 0,
        "parse_successes": parse_successes,
        "parse_failures": parse_failures,
        "state_1_clean_rows": s1_clean,
        "state_2_parse_failure_rq5_rows": s2_rq5,
        "state_3_api_failure_rows": s3_api_failure,
        "overall_api_success_rate_percent": pct(api_successes, actual_rows),
        "overall_parse_rate_percent": pct(parse_successes, actual_rows),
        "total_retries": total_retries,
        "rows_with_retries": rows_with_retries,
    }])


def create_provider_summary(df):
    rows = []

    for provider in EXPECTED_PROVIDERS:
        subset = df[df["model_name"] == provider]
        expected = EXPECTED_RECORDS * len(EXPECTED_CONDITIONS)

        api_ok = safe_bool(subset["api_success"])
        parse_ok = safe_bool(subset["parse_success"])

        total = len(subset)
        parse_successes = int(parse_ok.sum())

        rows.append({
            "provider": provider,
            "expected_rows": expected,
            "actual_rows": total,
            "row_count_pass": total == expected,
            "api_successes": int(api_ok.sum()),
            "api_failures": int((~api_ok).sum()),
            "parse_successes": parse_successes,
            "parse_failures": int((~parse_ok).sum()),
            "state_2_parse_failure_rq5_rows": int((subset["state"] == "S2_api_success_parse_failure_rq5").sum()),
            "parse_rate_percent": pct(parse_successes, total),
        })

    return pd.DataFrame(rows)


def create_condition_summary(df):
    rows = []

    for condition in EXPECTED_CONDITIONS:
        subset = df[df["prompt_condition"] == condition]
        expected = EXPECTED_RECORDS * len(EXPECTED_PROVIDERS)

        api_ok = safe_bool(subset["api_success"])
        parse_ok = safe_bool(subset["parse_success"])

        total = len(subset)
        parse_successes = int(parse_ok.sum())

        rows.append({
            "condition": condition,
            "expected_rows": expected,
            "actual_rows": total,
            "row_count_pass": total == expected,
            "api_successes": int(api_ok.sum()),
            "api_failures": int((~api_ok).sum()),
            "parse_successes": parse_successes,
            "parse_failures": int((~parse_ok).sum()),
            "state_2_parse_failure_rq5_rows": int((subset["state"] == "S2_api_success_parse_failure_rq5").sum()),
            "parse_rate_percent": pct(parse_successes, total),
        })

    return pd.DataFrame(rows)


def create_provider_condition_summary(df):
    rows = []

    for provider in EXPECTED_PROVIDERS:
        for condition in EXPECTED_CONDITIONS:
            subset = df[
                (df["model_name"] == provider)
                & (df["prompt_condition"] == condition)
            ]

            api_ok = safe_bool(subset["api_success"])
            parse_ok = safe_bool(subset["parse_success"])

            total = len(subset)
            parse_successes = int(parse_ok.sum())

            rows.append({
                "provider": provider,
                "condition": condition,
                "expected_rows": EXPECTED_RECORDS,
                "actual_rows": total,
                "row_count_pass": total == EXPECTED_RECORDS,
                "api_successes": int(api_ok.sum()),
                "api_failures": int((~api_ok).sum()),
                "parse_successes": parse_successes,
                "parse_failures": int((~parse_ok).sum()),
                "state_2_parse_failure_rq5_rows": int((subset["state"] == "S2_api_success_parse_failure_rq5").sum()),
                "parse_rate_percent": pct(parse_successes, total),
            })

    return pd.DataFrame(rows)


def create_state_summary(df):
    return (
        df.groupby(["model_name", "prompt_condition", "state"])
        .size()
        .reset_index(name="count")
        .sort_values(["model_name", "prompt_condition", "state"])
    )


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
                "total_rows": len(subset),
            }

            for category in COMPLIANCE_CATEGORIES:
                row[category] = int((subset["compliance_category"] == category).sum())

            known_total = sum(row[category] for category in COMPLIANCE_CATEGORIES)
            row["other_or_missing"] = len(subset) - known_total

            rows.append(row)

    return pd.DataFrame(rows)


def create_parse_compliance_crosstab(df):
    crosstab = pd.crosstab(
        df["parse_success"].fillna(False),
        df["compliance_category"].fillna("missing"),
        dropna=False,
        margins=True,
    )

    crosstab = crosstab.reset_index()
    crosstab = crosstab.rename(columns={"parse_success": "parse_success_flag"})

    return crosstab


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

            rows.append({
                "provider": provider,
                "condition": condition,
                "rows_with_valid_vector_and_score": total_checkable,
                "consistent": consistent,
                "inconsistent": inconsistent,
                "consistency_rate_percent": pct(consistent, total_checkable),
            })

    return pd.DataFrame(rows)


def create_retry_summary(df):
    rows = []

    for provider in EXPECTED_PROVIDERS:
        for condition in EXPECTED_CONDITIONS:
            subset = df[
                (df["model_name"] == provider)
                & (df["prompt_condition"] == condition)
            ]

            retry_count = pd.to_numeric(subset["retry_count"], errors="coerce").fillna(0)
            retry_wait = pd.to_numeric(subset["total_retry_wait_ms"], errors="coerce").fillna(0)

            rows.append({
                "provider": provider,
                "condition": condition,
                "total_retry_count": int(retry_count.sum()),
                "rows_with_retry": int((retry_count > 0).sum()),
                "max_retry_count": int(retry_count.max()) if len(retry_count) else 0,
                "total_retry_wait_ms": int(retry_wait.sum()),
            })

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

            rows.append({
                "provider": provider,
                "condition": condition,
                "rows_with_latency": len(latency),
                "mean_latency_ms": round(latency.mean(), 2) if len(latency) else None,
                "median_latency_ms": round(latency.median(), 2) if len(latency) else None,
                "min_latency_ms": int(latency.min()) if len(latency) else None,
                "max_latency_ms": int(latency.max()) if len(latency) else None,
                "std_dev_latency_ms": round(latency.std(), 2) if len(latency) > 1 else 0,
            })

    return pd.DataFrame(rows)


def create_duplicate_summary(df):
    key_cols = ["record_id", "model_name", "prompt_condition"]
    duplicates = df[df.duplicated(subset=key_cols, keep=False)].copy()

    return pd.DataFrame([{
        "duplicate_rows_found": len(duplicates),
        "duplicate_key_count": duplicates[key_cols].drop_duplicates().shape[0] if not duplicates.empty else 0,
        "duplicate_check_pass": duplicates.empty,
    }])


def create_duplicate_inventory(df):
    key_cols = ["record_id", "model_name", "prompt_condition"]
    duplicates = df[df.duplicated(subset=key_cols, keep=False)].copy()

    if duplicates.empty:
        return pd.DataFrame(columns=key_cols)

    return duplicates.sort_values(key_cols)[
        key_cols + ["api_success", "parse_success", "state", "raw_response_file"]
    ]


def create_missing_combination_inventory(df):
    records = sorted(df["record_id"].dropna().unique())

    expected_grid = pd.MultiIndex.from_product(
        [records, EXPECTED_PROVIDERS, EXPECTED_CONDITIONS],
        names=["record_id", "model_name", "prompt_condition"],
    ).to_frame(index=False)

    observed = df[["record_id", "model_name", "prompt_condition"]].drop_duplicates()

    missing = expected_grid.merge(
        observed,
        on=["record_id", "model_name", "prompt_condition"],
        how="left",
        indicator=True,
    )

    missing = missing[missing["_merge"] == "left_only"].drop(columns=["_merge"])

    return missing.sort_values(["record_id", "model_name", "prompt_condition"])


def create_unexpected_values_summary(df):
    unexpected_providers = sorted(set(df["model_name"].dropna()) - set(EXPECTED_PROVIDERS))
    unexpected_conditions = sorted(set(df["prompt_condition"].dropna()) - set(EXPECTED_CONDITIONS))
    unexpected_compliance = sorted(set(df["compliance_category"].dropna()) - set(COMPLIANCE_CATEGORIES))

    return pd.DataFrame([{
        "unexpected_providers": ", ".join(unexpected_providers) if unexpected_providers else "",
        "unexpected_conditions": ", ".join(unexpected_conditions) if unexpected_conditions else "",
        "unexpected_compliance_categories": ", ".join(unexpected_compliance) if unexpected_compliance else "",
        "unexpected_values_pass": not unexpected_providers and not unexpected_conditions and not unexpected_compliance,
    }])


def create_observed_issue_inventory(df):
    issues = df[
        (~safe_bool(df["api_success"]))
        | (~safe_bool(df["parse_success"]))
        | (df["compliance_category"].isin(["invalid", "parser_exception"]))
        | (df["error_type"].notna())
    ].copy()

    columns = [
        "record_id",
        "model_name",
        "prompt_condition",
        "api_success",
        "parse_success",
        "state",
        "compliance_category",
        "error_type",
        "error_message",
        "raw_response_file",
        "parsed_output_file",
    ]

    return issues[columns].sort_values(
        by=["model_name", "prompt_condition", "record_id"]
    )


def create_per_record_issue_summary(df):
    temp = df.copy()

    temp["has_observed_issue"] = (
        (~safe_bool(temp["api_success"]))
        | (~safe_bool(temp["parse_success"]))
        | (temp["compliance_category"].isin(["invalid", "parser_exception"]))
        | (temp["error_type"].notna())
    )

    summary = (
        temp.groupby("record_id")
        .agg(
            total_inferences=("record_id", "count"),
            observed_issue_count=("has_observed_issue", "sum"),
        )
        .reset_index()
    )

    summary["clean_inferences"] = (
        summary["total_inferences"] - summary["observed_issue_count"]
    )

    return summary.sort_values(
        by=["observed_issue_count", "record_id"],
        ascending=[False, True],
    )


def create_verdict_summary(overall, duplicate_summary, missing_inventory, unexpected_values):
    row = overall.iloc[0]

    verdict = {
        "row_count_pass": bool(row["row_count_pass"]),
        "distinct_record_count_pass": bool(row["distinct_record_count_pass"]),
        "api_failure_pass": bool(row["api_failure_pass"]),
        "duplicate_check_pass": bool(duplicate_summary.iloc[0]["duplicate_check_pass"]),
        "missing_combination_pass": len(missing_inventory) == 0,
        "unexpected_values_pass": bool(unexpected_values.iloc[0]["unexpected_values_pass"]),
    }

    verdict["overall_completeness_pass"] = all(verdict.values())

    return pd.DataFrame([verdict])


def write_markdown_report(
    verdict_summary,
    overall,
    provider_summary,
    condition_summary,
    provider_condition_summary,
    state_summary,
    compliance_summary,
    parse_compliance_crosstab,
    vector_score_summary,
    retry_summary,
    latency_summary,
    duplicate_summary,
    duplicate_inventory,
    missing_inventory,
    unexpected_values,
    observed_issue_inventory,
    per_record_issue_summary,
):
    row = overall.iloc[0]
    verdict = verdict_summary.iloc[0]

    lines = []

    lines.append("# Main Experiment Completeness Report\n")

    lines.append("## Verdict\n")
    lines.append(
        f"- Row count complete: {verdict['row_count_pass']}\n"
        f"- Distinct record count complete: {verdict['distinct_record_count_pass']}\n"
        f"- No API failures: {verdict['api_failure_pass']}\n"
        f"- No duplicate record/model/prompt rows: {verdict['duplicate_check_pass']}\n"
        f"- No missing record/model/prompt combinations: {verdict['missing_combination_pass']}\n"
        f"- No unexpected labels: {verdict['unexpected_values_pass']}\n"
        f"- Overall completeness pass: {verdict['overall_completeness_pass']}\n"
    )

    lines.append("## Purpose\n")
    lines.append(
        "This report checks whether the combined main experiment output is complete and internally consistent before accuracy, prompt sensitivity, EPSS correlation, and failure-mode analyses are performed. "
        "It does not make claims about correctness against official CVSS ground truth.\n"
    )

    lines.append("## Summary\n")
    lines.append(
        f"The main experiment expected {row['expected_rows']} inference rows and produced {row['actual_rows']} rows across {row['actual_distinct_records']} distinct records. "
        f"The combined dataset contains {row['api_successes']} API-successful rows and {row['api_failures']} API failure(s). "
        f"There were {row['parse_successes']} successful parses and {row['parse_failures']} parse failure(s), giving an overall parse rate of {row['overall_parse_rate_percent']}%. "
        f"State 2 rows, where the API call succeeded but parsing failed, totalled {row['state_2_parse_failure_rq5_rows']} and are retained as observed evidence for failure-mode analysis.\n"
    )

    tables = [
        ("Table 1: Verdict Summary", verdict_summary),
        ("Table 2: Overall Completion", overall),
        ("Table 3: Provider Summary", provider_summary),
        ("Table 4: Prompt Condition Summary", condition_summary),
        ("Table 5: Provider × Prompt Condition Summary", provider_condition_summary),
        ("Table 6: State Summary", state_summary),
        ("Table 7: Compliance Category Summary", compliance_summary),
        ("Table 8: Parse Success × Compliance Category Crosstab", parse_compliance_crosstab),
        ("Table 9: Vector-Score Consistency Summary", vector_score_summary),
        ("Table 10: Retry Summary", retry_summary),
        ("Table 11: Latency Summary", latency_summary),
        ("Table 12: Duplicate Summary", duplicate_summary),
        ("Table 13: Duplicate Inventory", duplicate_inventory),
        ("Table 14: Missing Combination Inventory", missing_inventory),
        ("Table 15: Unexpected Values Summary", unexpected_values),
        ("Table 16: Observed Issue Inventory", observed_issue_inventory),
        ("Table 17: Per-Record Issue Summary", per_record_issue_summary),
    ]

    for title, table in tables:
        lines.append(f"## {title}\n")
        lines.append(dataframe_to_markdown(table))
        lines.append("\n")

    lines.append("## Methodological Notes\n")
    lines.append(
        "- The Parquet export is used as the authoritative input because it preserves the combined results without Excel truncation issues.\n"
        "- State 1 means API success and parse success.\n"
        "- State 2 means API success but parse failure. These rows are retained as observed evidence for failure-mode analysis.\n"
        "- State 3 means API failure. No State 3 rows are expected in the final main experiment output.\n"
        "- The parse/compliance crosstab is included to check whether parser flags and compliance categories are coherent.\n"
        "- Accuracy against official CVSS values is assessed separately in the main accuracy analysis.\n"
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_results()

    overall = create_overall_summary(df)
    provider_summary = create_provider_summary(df)
    condition_summary = create_condition_summary(df)
    provider_condition_summary = create_provider_condition_summary(df)
    state_summary = create_state_summary(df)
    compliance_summary = create_compliance_summary(df)
    parse_compliance_crosstab = create_parse_compliance_crosstab(df)
    vector_score_summary = create_vector_score_summary(df)
    retry_summary = create_retry_summary(df)
    latency_summary = create_latency_summary(df)
    duplicate_summary = create_duplicate_summary(df)
    duplicate_inventory = create_duplicate_inventory(df)
    missing_inventory = create_missing_combination_inventory(df)
    unexpected_values = create_unexpected_values_summary(df)
    observed_issue_inventory = create_observed_issue_inventory(df)
    per_record_issue_summary = create_per_record_issue_summary(df)

    verdict_summary = create_verdict_summary(
        overall,
        duplicate_summary,
        missing_inventory,
        unexpected_values,
    )

    with pd.ExcelWriter(SUMMARY_FILE, engine="openpyxl") as writer:
        verdict_summary.to_excel(writer, sheet_name="verdict", index=False)
        overall.to_excel(writer, sheet_name="overall", index=False)
        provider_summary.to_excel(writer, sheet_name="provider_summary", index=False)
        condition_summary.to_excel(writer, sheet_name="condition_summary", index=False)
        provider_condition_summary.to_excel(writer, sheet_name="provider_condition", index=False)
        state_summary.to_excel(writer, sheet_name="state_summary", index=False)
        compliance_summary.to_excel(writer, sheet_name="compliance", index=False)
        parse_compliance_crosstab.to_excel(writer, sheet_name="parse_compliance_xtab", index=False)
        vector_score_summary.to_excel(writer, sheet_name="vector_consistency", index=False)
        retry_summary.to_excel(writer, sheet_name="retries", index=False)
        latency_summary.to_excel(writer, sheet_name="latency", index=False)
        duplicate_summary.to_excel(writer, sheet_name="duplicate_summary", index=False)
        duplicate_inventory.to_excel(writer, sheet_name="duplicate_inventory", index=False)
        missing_inventory.to_excel(writer, sheet_name="missing_combinations", index=False)
        unexpected_values.to_excel(writer, sheet_name="unexpected_values", index=False)
        observed_issue_inventory.to_excel(writer, sheet_name="observed_issues", index=False)
        per_record_issue_summary.to_excel(writer, sheet_name="record_issues", index=False)

    write_markdown_report(
        verdict_summary,
        overall,
        provider_summary,
        condition_summary,
        provider_condition_summary,
        state_summary,
        compliance_summary,
        parse_compliance_crosstab,
        vector_score_summary,
        retry_summary,
        latency_summary,
        duplicate_summary,
        duplicate_inventory,
        missing_inventory,
        unexpected_values,
        observed_issue_inventory,
        per_record_issue_summary,
    )

    print("=" * 80)
    print("Main completeness analysis complete")
    print("=" * 80)
    print(f"Input file: {INPUT_FILE}")
    print(f"Rows loaded: {len(df)}")
    print(f"Excel summary written to: {SUMMARY_FILE}")
    print(f"Markdown report written to: {REPORT_FILE}")

    print("\nKey checks:")
    print(f"- Expected rows: {EXPECTED_ROWS}")
    print(f"- Actual rows: {len(df)}")
    print(f"- Distinct records: {df['record_id'].nunique()}")
    print(f"- API failures: {int((~safe_bool(df['api_success'])).sum())}")
    print(f"- Parse failures: {int((~safe_bool(df['parse_success'])).sum())}")
    print(f"- State 2 parse-failure rows for RQ5: {int((df['state'] == 'S2_api_success_parse_failure_rq5').sum())}")
    print(f"- Missing combinations: {len(missing_inventory)}")
    print(f"- Duplicate rows: {int(duplicate_summary.iloc[0]['duplicate_rows_found'])}")
    print(f"- Overall completeness pass: {bool(verdict_summary.iloc[0]['overall_completeness_pass'])}")


if __name__ == "__main__":
    main()
