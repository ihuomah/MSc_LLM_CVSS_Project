import json
import shutil
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("main_study/results/raw_results/run_001_results.parquet")
OUTPUT_DIR = Path("main_study/results/analysis/failure_modes")

FAILURE_INVENTORY_XLSX = OUTPUT_DIR / "main_parse_failure_inventory.xlsx"
FAILURE_INVENTORY_CSV = OUTPUT_DIR / "main_parse_failure_inventory.csv"
FAILURE_REPORT_MD = OUTPUT_DIR / "main_parse_failure_report.md"
RAW_SAMPLE_DIR = OUTPUT_DIR / "raw_response_samples"

EXPECTED_STATE2_FAILURES = 65
ISSUE_CATEGORIES = ["invalid", "parser_exception"]


def safe_bool(series: pd.Series) -> pd.Series:
    return series.fillna(False).astype(bool)


def pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def load_results() -> pd.DataFrame:
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
        "error_type",
        "error_message",
        "raw_response_file",
        "parsed_output_file",
        "predicted_vector",
        "predicted_base_score",
        "vector_score_consistent",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    api_ok = safe_bool(df["api_success"])
    parse_ok = safe_bool(df["parse_success"])

    df["state"] = "S3_api_failure"
    df.loc[api_ok & parse_ok, "state"] = "S1_api_success_parse_success"
    df.loc[api_ok & ~parse_ok, "state"] = "S2_api_success_parse_failure_rq5"

    return df


def extract_state2_failures(df: pd.DataFrame) -> pd.DataFrame:
    failures = df[df["state"] == "S2_api_success_parse_failure_rq5"].copy()

    useful_columns = [
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
        "predicted_vector",
        "predicted_base_score",
        "vector_score_consistent",
    ]

    failures = failures[useful_columns].sort_values(
        by=["model_name", "prompt_condition", "compliance_category", "record_id"]
    )

    failures["failure_group"] = (
        failures["model_name"].astype(str)
        + " | "
        + failures["prompt_condition"].astype(str)
        + " | "
        + failures["compliance_category"].astype(str)
        + " | "
        + failures["error_type"].fillna("no_error_type").astype(str)
    )

    return failures


def create_provider_summary(failures: pd.DataFrame) -> pd.DataFrame:
    if failures.empty:
        return pd.DataFrame(columns=["model_name", "state2_parse_failures"])

    return (
        failures.groupby("model_name")
        .size()
        .reset_index(name="state2_parse_failures")
        .sort_values("model_name")
    )


def create_condition_summary(failures: pd.DataFrame) -> pd.DataFrame:
    if failures.empty:
        return pd.DataFrame(columns=["prompt_condition", "state2_parse_failures"])

    return (
        failures.groupby("prompt_condition")
        .size()
        .reset_index(name="state2_parse_failures")
        .sort_values("prompt_condition")
    )


def create_provider_condition_summary(failures: pd.DataFrame) -> pd.DataFrame:
    if failures.empty:
        return pd.DataFrame(columns=["model_name", "prompt_condition", "state2_parse_failures"])

    return (
        failures.groupby(["model_name", "prompt_condition"])
        .size()
        .reset_index(name="state2_parse_failures")
        .sort_values(["model_name", "prompt_condition"])
    )


def create_compliance_summary(failures: pd.DataFrame) -> pd.DataFrame:
    if failures.empty:
        return pd.DataFrame(columns=["compliance_category", "state2_parse_failures"])

    return (
        failures.groupby("compliance_category")
        .size()
        .reset_index(name="state2_parse_failures")
        .sort_values("compliance_category")
    )


def create_error_message_summary(failures: pd.DataFrame) -> pd.DataFrame:
    temp = failures.copy()
    temp["error_type_clean"] = temp["error_type"].fillna("no_error_type")
    temp["error_message_clean"] = temp["error_message"].fillna("no_error_message")

    return (
        temp.groupby(["model_name", "prompt_condition", "compliance_category", "error_type_clean", "error_message_clean"])
        .size()
        .reset_index(name="count")
        .sort_values(["count", "model_name"], ascending=[False, True])
    )


def create_failure_group_summary(failures: pd.DataFrame) -> pd.DataFrame:
    if failures.empty:
        return pd.DataFrame(columns=["failure_group", "count"])

    return (
        failures.groupby("failure_group")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


def read_raw_response(raw_path_value: str) -> str:
    if pd.isna(raw_path_value) or not str(raw_path_value).strip():
        return ""

    raw_path = Path(str(raw_path_value))

    if not raw_path.exists():
        return ""

    try:
        return raw_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return f"[Could not read raw response: {exc}]"


def add_raw_response_preview(failures: pd.DataFrame, max_chars: int = 1200) -> pd.DataFrame:
    failures = failures.copy()

    previews = []
    lengths = []

    for raw_path in failures["raw_response_file"]:
        text = read_raw_response(raw_path)
        lengths.append(len(text))
        previews.append(text[:max_chars])

    failures["raw_response_char_count"] = lengths
    failures["raw_response_preview"] = previews

    return failures


def copy_representative_raw_responses(failures: pd.DataFrame) -> pd.DataFrame:
    RAW_SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    sample_rows = []

    grouped = failures.groupby("failure_group", dropna=False)

    for group_name, group in grouped:
        group_sorted = group.sort_values("record_id")
        sample = group_sorted.head(3).copy()

        for _, row in sample.iterrows():
            raw_path = Path(str(row["raw_response_file"])) if pd.notna(row["raw_response_file"]) else None

            copied_to = ""
            copy_status = "not_copied"

            if raw_path and raw_path.exists():
                safe_group = (
                    str(group_name)
                    .replace(" | ", "__")
                    .replace("/", "-")
                    .replace("\\", "-")
                    .replace(":", "-")
                )
                filename = f"record_{row['record_id']}_{row['model_name']}_{row['prompt_condition']}_{safe_group}.txt"
                destination = RAW_SAMPLE_DIR / filename

                try:
                    shutil.copyfile(raw_path, destination)
                    copied_to = str(destination)
                    copy_status = "copied"
                except Exception as exc:
                    copied_to = str(destination)
                    copy_status = f"copy_failed: {exc}"
            else:
                copy_status = "raw_file_missing"

            sample_rows.append({
                "failure_group": group_name,
                "record_id": row["record_id"],
                "model_name": row["model_name"],
                "prompt_condition": row["prompt_condition"],
                "compliance_category": row["compliance_category"],
                "error_type": row["error_type"],
                "error_message": row["error_message"],
                "raw_response_file": row["raw_response_file"],
                "copied_sample_file": copied_to,
                "copy_status": copy_status,
            })

    return pd.DataFrame(sample_rows)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"

    try:
        return df.to_markdown(index=False)
    except ImportError:
        return df.to_string(index=False)


def write_markdown_report(
    failures: pd.DataFrame,
    provider_summary: pd.DataFrame,
    condition_summary: pd.DataFrame,
    provider_condition_summary: pd.DataFrame,
    compliance_summary: pd.DataFrame,
    error_message_summary: pd.DataFrame,
    failure_group_summary: pd.DataFrame,
    sample_inventory: pd.DataFrame,
) -> None:
    total = len(failures)

    lines = []
    lines.append("# Main Parse Failure Extraction Report\n")

    lines.append("## Purpose\n")
    lines.append(
        "This report extracts State 2 rows from the main experiment. State 2 means that the model API call succeeded, but the response did not parse successfully. "
        "These rows are retained as observed evidence for failure-mode analysis and prompt-sensitivity interpretation.\n"
    )

    lines.append("## Summary\n")
    lines.append(
        f"The combined result file contains {total} State 2 parse-failure rows. "
        f"This script expected {EXPECTED_STATE2_FAILURES} rows based on the completeness analysis. "
        f"Expectation match: {total == EXPECTED_STATE2_FAILURES}.\n"
    )

    lines.append("## Table 1: Provider Summary\n")
    lines.append(dataframe_to_markdown(provider_summary))
    lines.append("\n")

    lines.append("## Table 2: Prompt Condition Summary\n")
    lines.append(dataframe_to_markdown(condition_summary))
    lines.append("\n")

    lines.append("## Table 3: Provider × Prompt Condition Summary\n")
    lines.append(dataframe_to_markdown(provider_condition_summary))
    lines.append("\n")

    lines.append("## Table 4: Compliance Category Summary\n")
    lines.append(dataframe_to_markdown(compliance_summary))
    lines.append("\n")

    lines.append("## Table 5: Error Message Summary\n")
    lines.append(dataframe_to_markdown(error_message_summary))
    lines.append("\n")

    lines.append("## Table 6: Failure Group Summary\n")
    lines.append(dataframe_to_markdown(failure_group_summary))
    lines.append("\n")

    lines.append("## Table 7: Representative Raw Response Samples Copied\n")
    lines.append(dataframe_to_markdown(sample_inventory))
    lines.append("\n")

    lines.append("## Methodological Notes\n")
    lines.append(
        "- This script does not modify or repair any model output.\n"
        "- The extracted failures remain part of the observed experimental results.\n"
        "- Representative raw responses are copied only for inspection; the original raw response files remain the source files.\n"
        "- The next manual step is to inspect representative raw responses and classify whether failures appear to be model output near-misses, hard invalid outputs, parser exceptions, or potential parser-asymmetry artefacts.\n"
    )

    FAILURE_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_results()
    failures = extract_state2_failures(df)
    failures_with_preview = add_raw_response_preview(failures)

    provider_summary = create_provider_summary(failures)
    condition_summary = create_condition_summary(failures)
    provider_condition_summary = create_provider_condition_summary(failures)
    compliance_summary = create_compliance_summary(failures)
    error_message_summary = create_error_message_summary(failures)
    failure_group_summary = create_failure_group_summary(failures)
    sample_inventory = copy_representative_raw_responses(failures)

    with pd.ExcelWriter(FAILURE_INVENTORY_XLSX, engine="openpyxl") as writer:
        failures_with_preview.to_excel(writer, sheet_name="failure_inventory", index=False)
        provider_summary.to_excel(writer, sheet_name="provider_summary", index=False)
        condition_summary.to_excel(writer, sheet_name="condition_summary", index=False)
        provider_condition_summary.to_excel(writer, sheet_name="provider_condition", index=False)
        compliance_summary.to_excel(writer, sheet_name="compliance_summary", index=False)
        error_message_summary.to_excel(writer, sheet_name="error_messages", index=False)
        failure_group_summary.to_excel(writer, sheet_name="failure_groups", index=False)
        sample_inventory.to_excel(writer, sheet_name="sample_inventory", index=False)

    failures_with_preview.to_csv(FAILURE_INVENTORY_CSV, index=False, encoding="utf-8")

    write_markdown_report(
        failures=failures,
        provider_summary=provider_summary,
        condition_summary=condition_summary,
        provider_condition_summary=provider_condition_summary,
        compliance_summary=compliance_summary,
        error_message_summary=error_message_summary,
        failure_group_summary=failure_group_summary,
        sample_inventory=sample_inventory,
    )

    print("=" * 80)
    print("Main parse failure extraction complete")
    print("=" * 80)
    print(f"Input file: {INPUT_FILE}")
    print(f"Rows loaded: {len(df)}")
    print(f"State 2 parse-failure rows extracted: {len(failures)}")
    print(f"Expected State 2 rows: {EXPECTED_STATE2_FAILURES}")
    print(f"Expectation match: {len(failures) == EXPECTED_STATE2_FAILURES}")
    print(f"Excel inventory written to: {FAILURE_INVENTORY_XLSX}")
    print(f"CSV inventory written to: {FAILURE_INVENTORY_CSV}")
    print(f"Markdown report written to: {FAILURE_REPORT_MD}")
    print(f"Representative raw response samples copied to: {RAW_SAMPLE_DIR}")

    print("\nProvider summary:")
    print(provider_summary.to_string(index=False))

    print("\nCondition summary:")
    print(condition_summary.to_string(index=False))

    print("\nCompliance summary:")
    print(compliance_summary.to_string(index=False))

    print("\nFailure group summary:")
    print(failure_group_summary.to_string(index=False))


if __name__ == "__main__":
    main()
