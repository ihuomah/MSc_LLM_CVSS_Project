import math
from pathlib import Path

import pandas as pd
from cvss import CVSS3

try:
    from scipy.stats import spearmanr
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


RESULTS_FILE = Path("main_study/results/raw_results/run_001_results.parquet")
GROUND_TRUTH_FILE = Path("main_study/experiment_inputs/main_record_verification_v1.parquet")
OUTPUT_DIR = Path("main_study/results/analysis/accuracy")

JOINED_PARQUET_FILE = OUTPUT_DIR / "main_accuracy_joined_rows.parquet"
JOINED_CSV_FILE = OUTPUT_DIR / "main_accuracy_joined_rows.csv"
JOINED_XLSX_FILE = OUTPUT_DIR / "main_accuracy_joined_rows.xlsx"
SUMMARY_FILE = OUTPUT_DIR / "main_accuracy_summary.xlsx"
REPORT_FILE = OUTPUT_DIR / "main_accuracy_report.md"

PROVIDERS = ["openai", "gemini", "ollama"]
CONDITIONS = ["conventional", "structured"]

METRIC_COLUMNS = {
    "AV": "attack_vector",
    "AC": "attack_complexity",
    "PR": "privileges_required",
    "UI": "user_interaction",
    "S": "scope",
    "C": "confidentiality_impact",
    "I": "integrity_impact",
    "A": "availability_impact",
}

OFFICIAL_METRIC_COLUMNS = {
    "AV": "official_attack_vector",
    "AC": "official_attack_complexity",
    "PR": "official_privileges_required",
    "UI": "official_user_interaction",
    "S": "official_scope",
    "C": "official_confidentiality_impact",
    "I": "official_integrity_impact",
    "A": "official_availability_impact",
}

EXPECTED_RECORDS = 1000
EXPECTED_ROWS = EXPECTED_RECORDS * len(PROVIDERS) * len(CONDITIONS)


def pct(num, den):
    return 0.0 if den == 0 else round((num / den) * 100, 2)


def safe_bool(series):
    return series.fillna(False).astype(bool)


def normalise_vector(vector):
    if not isinstance(vector, str) or not vector.strip():
        return None

    vector = vector.strip().replace('"', "").replace("'", "")

    if not vector.startswith("CVSS:3.1/"):
        if vector.startswith("AV:"):
            vector = "CVSS:3.1/" + vector
        else:
            return None

    try:
        CVSS3(vector).scores()[0]
    except Exception:
        return None

    metric_map = {}
    for part in vector.split("/"):
        if ":" in part and not part.startswith("CVSS"):
            key, value = part.split(":", 1)
            metric_map[key] = value

    order = ["AV", "AC", "PR", "UI", "S", "C", "I", "A"]
    if not all(metric in metric_map for metric in order):
        return None

    return "CVSS:3.1/" + "/".join(f"{metric}:{metric_map[metric]}" for metric in order)


def calculated_score_from_vector(vector):
    canonical = normalise_vector(vector)
    if canonical is None:
        return None

    try:
        return float(CVSS3(canonical).scores()[0])
    except Exception:
        return None


def extract_metrics_from_vector(vector, output_columns):
    canonical = normalise_vector(vector)
    if canonical is None:
        return {v: None for v in output_columns.values()}

    metric_map = {}
    for part in canonical.split("/"):
        if ":" in part and not part.startswith("CVSS"):
            key, value = part.split(":", 1)
            metric_map[key] = value

    return {output_columns[metric]: metric_map.get(metric) for metric in output_columns}


def severity_from_score(score):
    if pd.isna(score):
        return None

    score = float(score)

    if score == 0.0:
        return "NONE"
    if score < 4.0:
        return "LOW"
    if score < 7.0:
        return "MEDIUM"
    if score < 9.0:
        return "HIGH"
    return "CRITICAL"


def rmse(series):
    if len(series) == 0:
        return None
    return math.sqrt((series ** 2).mean())


def dataframe_to_markdown(df):
    if df.empty:
        return "_No rows._"
    try:
        return df.to_markdown(index=False)
    except ImportError:
        return df.to_string(index=False)


def spearman_corr(x, y):
    temp = pd.DataFrame({"x": x, "y": y}).dropna()

    if len(temp) < 3:
        return None, None, len(temp)

    if SCIPY_AVAILABLE:
        result = spearmanr(temp["x"], temp["y"])
        return round(float(result.statistic), 4), round(float(result.pvalue), 4), len(temp)

    return round(temp["x"].corr(temp["y"], method="spearman"), 4), None, len(temp)


def load_and_join():
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"Results file not found: {RESULTS_FILE}")

    if not GROUND_TRUTH_FILE.exists():
        raise FileNotFoundError(f"Ground-truth file not found: {GROUND_TRUTH_FILE}")

    results = pd.read_parquet(RESULTS_FILE)
    truth = pd.read_parquet(GROUND_TRUTH_FILE)

    required_results_cols = [
        "record_id",
        "model_name",
        "prompt_condition",
        "api_success",
        "parse_success",
        "compliance_category",
        "predicted_vector",
        "predicted_base_score",
        "calculated_base_score",
        "vector_score_consistent",
        "vector_score_delta",
        *METRIC_COLUMNS.values(),
    ]

    required_truth_cols = [
        "record_id",
        "cve_id",
        "official_cvss_vector",
        "official_base_score",
        "official_severity",
        "epss_score",
        "epss_percentile",
        "published_year",
        "cvss_selection_method",
    ]

    missing_results = [col for col in required_results_cols if col not in results.columns]
    missing_truth = [col for col in required_truth_cols if col not in truth.columns]

    if missing_results:
        raise ValueError(f"Results file missing columns: {missing_results}")
    if missing_truth:
        raise ValueError(f"Ground-truth file missing columns: {missing_truth}")

    official_metrics = truth["official_cvss_vector"].apply(
        lambda v: extract_metrics_from_vector(v, OFFICIAL_METRIC_COLUMNS)
    )
    # index=truth.index forces row-wise alignment on concat, so official
    # metric columns can never attach to the wrong ground-truth rows.
    official_metrics_df = pd.DataFrame(list(official_metrics), index=truth.index)
    truth = pd.concat([truth, official_metrics_df], axis=1)

    joined = results.merge(
        truth[
            [
                "record_id",
                "cve_id",
                "official_cvss_vector",
                "official_base_score",
                "official_severity",
                "epss_score",
                "epss_percentile",
                "published_year",
                "cvss_selection_method",
                *OFFICIAL_METRIC_COLUMNS.values(),
            ]
        ],
        on="record_id",
        how="left",
        validate="many_to_one",
    )

    if len(joined) != EXPECTED_ROWS:
        raise ValueError(f"Joined row count mismatch: expected {EXPECTED_ROWS}, got {len(joined)}")

    null_official_vectors = int(joined["official_cvss_vector"].isna().sum())
    if null_official_vectors != 0:
        raise ValueError(f"Join produced {null_official_vectors} rows with missing official CVSS vectors")

    joined["api_ok"] = safe_bool(joined["api_success"])
    joined["parse_ok"] = safe_bool(joined["parse_success"])

    joined["canonical_predicted_vector"] = joined["predicted_vector"].apply(normalise_vector)
    joined["canonical_official_vector"] = joined["official_cvss_vector"].apply(normalise_vector)

    joined["analysis_calculated_base_score"] = joined["canonical_predicted_vector"].apply(
        calculated_score_from_vector
    )

    joined["runtime_calculated_base_score_numeric"] = pd.to_numeric(
        joined["calculated_base_score"], errors="coerce"
    )

    joined["analysis_vs_runtime_score_delta"] = (
        joined["analysis_calculated_base_score"]
        - joined["runtime_calculated_base_score_numeric"]
    )

    joined["analysis_runtime_score_match"] = (
        joined["analysis_calculated_base_score"].notna()
        & joined["runtime_calculated_base_score_numeric"].notna()
        & (joined["analysis_vs_runtime_score_delta"].abs() <= 0.0001)
    )

    joined["official_base_score"] = pd.to_numeric(joined["official_base_score"], errors="coerce")

    joined["canonical_vector_match"] = (
        joined["parse_ok"]
        & joined["canonical_predicted_vector"].notna()
        & joined["canonical_official_vector"].notna()
        & (joined["canonical_predicted_vector"] == joined["canonical_official_vector"])
    )

    joined["score_error"] = joined["analysis_calculated_base_score"] - joined["official_base_score"]
    joined["absolute_score_error"] = joined["score_error"].abs()

    joined["predicted_severity_from_analysis_score"] = joined["analysis_calculated_base_score"].apply(
        severity_from_score
    )

    joined["severity_match"] = (
        joined["parse_ok"]
        & joined["predicted_severity_from_analysis_score"].notna()
        & joined["official_severity"].notna()
        & (
            joined["predicted_severity_from_analysis_score"].astype(str).str.upper()
            == joined["official_severity"].astype(str).str.upper()
        )
    )

    for metric, pred_col in METRIC_COLUMNS.items():
        official_col = OFFICIAL_METRIC_COLUMNS[metric]
        joined[f"{metric}_match"] = (
            joined["parse_ok"]
            & joined[pred_col].notna()
            & joined[official_col].notna()
            & (joined[pred_col].astype(str) == joined[official_col].astype(str))
        )

    return joined


def parsed_only(df):
    return df[df["parse_ok"]].copy()


def subset_for(df, provider, condition):
    return df[(df["model_name"] == provider) & (df["prompt_condition"] == condition)]


def create_overall_summary(df):
    truth_unique = df[
        [
            "record_id",
            "cve_id",
            "official_cvss_vector",
            "official_base_score",
            "official_severity",
            "epss_score",
            "epss_percentile",
            "published_year",
            "cvss_selection_method",
        ]
    ].drop_duplicates("record_id")

    return pd.DataFrame([
        {
            "results_file": str(RESULTS_FILE),
            "ground_truth_file": str(GROUND_TRUTH_FILE),
            "total_joined_rows": len(df),
            "expected_rows": EXPECTED_ROWS,
            "distinct_records": df["record_id"].nunique(),
            "ground_truth_distinct_records": truth_unique["record_id"].nunique(),
            "api_failures": int((~df["api_ok"]).sum()),
            "parse_failures": int((~df["parse_ok"]).sum()),
            "parsed_rows": int(df["parse_ok"].sum()),
            "unparseable_rows": int((~df["parse_ok"]).sum()),
            "score_used_for_error_metrics": "analysis_calculated_base_score_from_predicted_vector",
            "match_rate_denominators": "parsed_only and all_attempted",
            "error_metric_denominator": "parsed_only_with_score",
            "official_vector_nulls_after_join": int(df["official_cvss_vector"].isna().sum()),
            "official_score_nulls_after_join": int(df["official_base_score"].isna().sum()),
            "primary_type_records": int((truth_unique["cvss_selection_method"] == "primary_type").sum()),
            "nvd_source_records": int((truth_unique["cvss_selection_method"] == "nvd_source").sum()),
        }
    ])


def create_ground_truth_provenance_summary(df):
    truth_unique = df.drop_duplicates("record_id")
    return (
        truth_unique.groupby(["cvss_selection_method", "official_severity"], dropna=False)
        .size()
        .reset_index(name="record_count")
        .sort_values(["cvss_selection_method", "official_severity"])
    )


def create_parse_denominator_summary(df):
    rows = []

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            sub = subset_for(df, provider, condition)
            parsed = sub[sub["parse_ok"]]
            rows.append({
                "provider": provider,
                "condition": condition,
                "all_attempted_rows": len(sub),
                "parsed_rows": len(parsed),
                "unparseable_rows": len(sub) - len(parsed),
                "parse_rate_percent": pct(len(parsed), len(sub)),
            })

    return pd.DataFrame(rows)


def create_metric_agreement_summary(df, denominator_mode):
    rows = []

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            sub_all = subset_for(df, provider, condition)
            sub = sub_all[sub_all["parse_ok"]] if denominator_mode == "parsed_only" else sub_all
            denom = len(sub)

            row = {
                "denominator_mode": denominator_mode,
                "provider": provider,
                "condition": condition,
                "n": denom,
                "unparseable_rows_in_denominator": int((~sub["parse_ok"]).sum()) if len(sub) else 0,
            }

            for metric in METRIC_COLUMNS:
                match_col = f"{metric}_match"
                matches = int(sub[match_col].sum())
                row[f"{metric}_matches"] = matches
                row[f"{metric}_agreement_percent"] = pct(matches, denom)

            rows.append(row)

    return pd.DataFrame(rows)


def create_vector_match_summary(df, denominator_mode):
    rows = []

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            sub_all = subset_for(df, provider, condition)
            sub = sub_all[sub_all["parse_ok"]] if denominator_mode == "parsed_only" else sub_all
            n = len(sub)
            matches = int(sub["canonical_vector_match"].sum())

            rows.append({
                "denominator_mode": denominator_mode,
                "provider": provider,
                "condition": condition,
                "n": n,
                "unparseable_rows_in_denominator": int((~sub["parse_ok"]).sum()) if len(sub) else 0,
                "exact_canonical_vector_matches": matches,
                "exact_vector_match_percent": pct(matches, n),
            })

    return pd.DataFrame(rows)


def create_severity_match_summary(df, denominator_mode):
    rows = []

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            sub_all = subset_for(df, provider, condition)
            sub = sub_all[sub_all["parse_ok"]] if denominator_mode == "parsed_only" else sub_all
            n = len(sub)
            matches = int(sub["severity_match"].sum())

            rows.append({
                "denominator_mode": denominator_mode,
                "provider": provider,
                "condition": condition,
                "n": n,
                "unparseable_rows_in_denominator": int((~sub["parse_ok"]).sum()) if len(sub) else 0,
                "severity_matches": matches,
                "severity_match_percent": pct(matches, n),
            })

    return pd.DataFrame(rows)


def create_score_error_summary(df):
    rows = []

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            sub_all = subset_for(df, provider, condition)
            parsed = sub_all[sub_all["parse_ok"]]
            scored = parsed.dropna(subset=["score_error"])

            rows.append({
                "provider": provider,
                "condition": condition,
                "attempted_rows": len(sub_all),
                "parsed_rows": len(parsed),
                "unparseable_rows_excluded": len(sub_all) - len(parsed),
                "rows_used_for_error_metrics": len(scored),
                "rows_excluded_from_error_metrics": len(sub_all) - len(scored),
                "mean_signed_error": round(scored["score_error"].mean(), 4) if len(scored) else None,
                "mae": round(scored["absolute_score_error"].mean(), 4) if len(scored) else None,
                "rmse": round(rmse(scored["score_error"]), 4) if len(scored) else None,
                "min_error": round(scored["score_error"].min(), 4) if len(scored) else None,
                "max_error": round(scored["score_error"].max(), 4) if len(scored) else None,
            })

    return pd.DataFrame(rows)


def create_condition_flip_summary(df):
    parsed = parsed_only(df)
    rows = []

    for provider in PROVIDERS:
        provider_df = parsed[parsed["model_name"] == provider]

        conv = provider_df[provider_df["prompt_condition"] == "conventional"]
        struct = provider_df[provider_df["prompt_condition"] == "structured"]

        merged = conv.merge(
            struct,
            on="record_id",
            suffixes=("_conventional", "_structured"),
        )

        for metric, col in METRIC_COLUMNS.items():
            conv_col = f"{col}_conventional"
            struct_col = f"{col}_structured"

            available = merged[conv_col].notna() & merged[struct_col].notna()
            denom = int(available.sum())

            flips = int(
                (
                    merged.loc[available, conv_col].astype(str)
                    != merged.loc[available, struct_col].astype(str)
                ).sum()
            )

            rows.append({
                "provider": provider,
                "metric": metric,
                "paired_parseable_records": denom,
                "condition_flips": flips,
                "flip_rate_percent": pct(flips, denom),
            })

    return pd.DataFrame(rows)


def create_epss_correlation_summary(df):
    rows = []

    baseline = df[["record_id", "official_base_score", "epss_score"]].drop_duplicates("record_id")
    rho, p_value, n = spearman_corr(baseline["official_base_score"], baseline["epss_score"])

    rows.append({
        "provider": "official_cvss",
        "condition": "baseline",
        "score_used": "official_base_score",
        "n": n,
        "spearman_rho": rho,
        "p_value": p_value,
    })

    parsed = parsed_only(df)

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            sub = subset_for(parsed, provider, condition)
            rho, p_value, n = spearman_corr(sub["analysis_calculated_base_score"], sub["epss_score"])

            rows.append({
                "provider": provider,
                "condition": condition,
                "score_used": "analysis_calculated_base_score_from_predicted_vector",
                "n": n,
                "spearman_rho": rho,
                "p_value": p_value,
            })

    return pd.DataFrame(rows)


def create_internal_score_consistency_summary(df):
    rows = []

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            sub = subset_for(df, provider, condition)
            parsed = sub[sub["parse_ok"]]
            checkable = parsed[
                parsed["predicted_base_score"].notna()
                & parsed["analysis_calculated_base_score"].notna()
            ].copy()

            model_score = pd.to_numeric(checkable["predicted_base_score"], errors="coerce")
            analysis_score = pd.to_numeric(checkable["analysis_calculated_base_score"], errors="coerce")
            delta = model_score - analysis_score

            consistent = (delta.abs() <= 0.15)

            rows.append({
                "provider": provider,
                "condition": condition,
                "parsed_rows": len(parsed),
                "rows_with_model_score_and_vector_score": int(delta.notna().sum()),
                "internally_consistent_rows_tolerance_0_15": int(consistent.sum()),
                "internally_inconsistent_rows_tolerance_0_15": int((~consistent & delta.notna()).sum()),
                "internal_consistency_rate_percent": pct(int(consistent.sum()), int(delta.notna().sum())),
                "mean_model_minus_vector_score_delta": round(delta.mean(), 4) if int(delta.notna().sum()) else None,
                "max_abs_model_minus_vector_score_delta": round(delta.abs().max(), 4) if int(delta.notna().sum()) else None,
            })

    return pd.DataFrame(rows)


def create_runtime_recompute_check(df):
    parsed = df[df["parse_ok"]].copy()
    checkable = parsed[
        parsed["analysis_calculated_base_score"].notna()
        & parsed["runtime_calculated_base_score_numeric"].notna()
    ]

    mismatches = checkable[checkable["analysis_vs_runtime_score_delta"].abs() > 0.0001]

    summary = pd.DataFrame([
        {
            "parsed_rows": len(parsed),
            "rows_with_analysis_and_runtime_scores": len(checkable),
            "matching_scores": len(checkable) - len(mismatches),
            "mismatching_scores": len(mismatches),
            "max_abs_delta": round(checkable["analysis_vs_runtime_score_delta"].abs().max(), 6) if len(checkable) else None,
        }
    ])

    inventory_cols = [
        "record_id",
        "model_name",
        "prompt_condition",
        "predicted_vector",
        "analysis_calculated_base_score",
        "runtime_calculated_base_score_numeric",
        "analysis_vs_runtime_score_delta",
    ]

    return summary, mismatches[inventory_cols].sort_values(["model_name", "prompt_condition", "record_id"])


def create_unparseable_inventory(df):
    cols = [
        "record_id",
        "cve_id",
        "model_name",
        "prompt_condition",
        "compliance_category",
        "official_cvss_vector",
        "official_base_score",
        "official_severity",
        "cvss_selection_method",
        "predicted_vector",
        "predicted_base_score",
    ]
    return df[~df["parse_ok"]][cols].sort_values(["model_name", "prompt_condition", "record_id"])


def write_report(
    overall,
    gt_provenance,
    parse_denominators,
    metric_agreement,
    vector_match,
    severity_match,
    score_error,
    condition_flips,
    epss_correlation,
    internal_consistency,
    runtime_check,
    runtime_mismatch_inventory,
    unparseable_inventory,
):
    lines = []

    lines.append("# Main Accuracy Report\n")

    lines.append("## Purpose\n")
    lines.append(
        "This report evaluates the main experiment by comparing LLM-generated CVSS outputs with the official NVD-grounded CVSS values in the verification dataset. "
        "It includes metric-level agreement, exact vector match, base-score error, severity agreement, prompt-condition flips, EPSS correlation, and internal vector-score consistency.\n"
    )

    lines.append("## Methodological Notes\n")
    lines.append(
        "- The analysis joins the combined result file to `main_record_verification_v1.parquet` using `record_id`.\n"
        "- All 1,000 records are retained. The verification dataset contains both `primary_type` and `nvd_source` values in `cvss_selection_method`; these are carried through for auditability.\n"
        "- Exact vector match uses canonicalised CVSS v3.1 vectors rather than raw string equality.\n"
        "- Base-score error uses a score recomputed from the predicted vector inside this analysis script. This avoids relying on the model-reported numeric score.\n"
        "- Match-rate tables are reported using both parsed-only and all-attempted denominators. In all-attempted mode, unparseable rows remain in the denominator and count as non-matches.\n"
        "- Mean signed error, MAE, and RMSE are calculated only where a valid parsed vector and numeric official score are available. Unparseable rows are reported as exclusions rather than assigned an artificial error value.\n"
        "- Spearman's rho is used for CVSS-EPSS correlation, with official CVSS versus EPSS included as a baseline.\n"
    )

    tables = [
        ("Table 1: Overall Accuracy Dataset Summary", overall),
        ("Table 2: Ground-Truth Provenance Summary", gt_provenance),
        ("Table 3: Parse Denominator Summary", parse_denominators),
        ("Table 4: Per-Metric Agreement Summary", metric_agreement),
        ("Table 5: Exact Canonical Vector Match Summary", vector_match),
        ("Table 6: Severity Match Summary", severity_match),
        ("Table 7: Base Score Error Summary", score_error),
        ("Table 8: Prompt Condition Flip Summary", condition_flips),
        ("Table 9: CVSS-EPSS Spearman Correlation Summary", epss_correlation),
        ("Table 10: Internal Vector-Score Consistency Summary", internal_consistency),
        ("Table 11: Runtime Recompute Cross-Check", runtime_check),
        ("Table 12: Runtime Recompute Mismatch Inventory", runtime_mismatch_inventory),
        ("Table 13: Unparseable Output Inventory", unparseable_inventory),
    ]

    for title, table in tables:
        lines.append(f"## {title}\n")
        lines.append(dataframe_to_markdown(table))
        lines.append("\n")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    joined = load_and_join()

    overall = create_overall_summary(joined)
    gt_provenance = create_ground_truth_provenance_summary(joined)
    parse_denominators = create_parse_denominator_summary(joined)

    metric_agreement = pd.concat(
        [
            create_metric_agreement_summary(joined, "parsed_only"),
            create_metric_agreement_summary(joined, "all_attempted"),
        ],
        ignore_index=True,
    )

    vector_match = pd.concat(
        [
            create_vector_match_summary(joined, "parsed_only"),
            create_vector_match_summary(joined, "all_attempted"),
        ],
        ignore_index=True,
    )

    severity_match = pd.concat(
        [
            create_severity_match_summary(joined, "parsed_only"),
            create_severity_match_summary(joined, "all_attempted"),
        ],
        ignore_index=True,
    )

    score_error = create_score_error_summary(joined)
    condition_flips = create_condition_flip_summary(joined)
    epss_correlation = create_epss_correlation_summary(joined)
    internal_consistency = create_internal_score_consistency_summary(joined)
    runtime_check, runtime_mismatch_inventory = create_runtime_recompute_check(joined)
    unparseable_inventory = create_unparseable_inventory(joined)

    joined.to_parquet(JOINED_PARQUET_FILE, index=False)
    joined.to_csv(JOINED_CSV_FILE, index=False)
    joined.to_excel(JOINED_XLSX_FILE, index=False)

    with pd.ExcelWriter(SUMMARY_FILE, engine="openpyxl") as writer:
        overall.to_excel(writer, sheet_name="overall", index=False)
        gt_provenance.to_excel(writer, sheet_name="gt_provenance", index=False)
        parse_denominators.to_excel(writer, sheet_name="parse_denominators", index=False)
        metric_agreement.to_excel(writer, sheet_name="metric_agreement", index=False)
        vector_match.to_excel(writer, sheet_name="vector_match", index=False)
        severity_match.to_excel(writer, sheet_name="severity_match", index=False)
        score_error.to_excel(writer, sheet_name="score_error", index=False)
        condition_flips.to_excel(writer, sheet_name="condition_flips", index=False)
        epss_correlation.to_excel(writer, sheet_name="epss_correlation", index=False)
        internal_consistency.to_excel(writer, sheet_name="internal_consistency", index=False)
        runtime_check.to_excel(writer, sheet_name="runtime_recompute_check", index=False)
        runtime_mismatch_inventory.to_excel(writer, sheet_name="runtime_mismatches", index=False)
        unparseable_inventory.to_excel(writer, sheet_name="unparseable", index=False)

    write_report(
        overall,
        gt_provenance,
        parse_denominators,
        metric_agreement,
        vector_match,
        severity_match,
        score_error,
        condition_flips,
        epss_correlation,
        internal_consistency,
        runtime_check,
        runtime_mismatch_inventory,
        unparseable_inventory,
    )

    print("=" * 80)
    print("Main accuracy analysis complete")
    print("=" * 80)
    print(f"Results file: {RESULTS_FILE}")
    print(f"Ground-truth file: {GROUND_TRUTH_FILE}")
    print(f"Joined rows written to: {JOINED_PARQUET_FILE}")
    print(f"Excel summary written to: {SUMMARY_FILE}")
    print(f"Markdown report written to: {REPORT_FILE}")

    print("\nKey checks:")
    print(f"- Joined rows: {len(joined)}")
    print(f"- Distinct records: {joined['record_id'].nunique()}")
    print(f"- Official vector nulls: {int(joined['official_cvss_vector'].isna().sum())}")
    print(f"- Parse failures: {int((~joined['parse_ok']).sum())}")
    print(f"- Runtime recompute mismatches: {int(runtime_check.iloc[0]['mismatching_scores'])}")
    print(f"- Unparseable rows carried as non-matches in all-attempted tables: {len(unparseable_inventory)}")


if __name__ == "__main__":
    main()