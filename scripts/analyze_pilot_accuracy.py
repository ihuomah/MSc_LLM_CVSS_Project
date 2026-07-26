import math
from pathlib import Path

import pandas as pd
from cvss import CVSS3

try:
    from scipy.stats import spearmanr
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


RESULTS_FILE = Path("results/pilot/raw_results/pilot_run_001_results.xlsx")
GROUND_TRUTH_FILE = Path("data/frozen_pilot_v2/datasets/pilot_record_id_verification_v2.xlsx")

OUTPUT_DIR = Path("results/pilot/analysis/accuracy")
JOINED_FILE = OUTPUT_DIR / "pilot_accuracy_joined_rows.xlsx"
SUMMARY_FILE = OUTPUT_DIR / "pilot_accuracy_summary.xlsx"
REPORT_FILE = OUTPUT_DIR / "pilot_accuracy_report.md"

PROVIDERS = ["ollama", "openai", "gemini"]
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


def pct(num, den):
    return 0.0 if den == 0 else round((num / den) * 100, 2)


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

    parts = vector.split("/")
    metric_map = {}

    for part in parts:
        if ":" in part and not part.startswith("CVSS"):
            key, value = part.split(":", 1)
            metric_map[key] = value

    order = ["AV", "AC", "PR", "UI", "S", "C", "I", "A"]

    if not all(metric in metric_map for metric in order):
        return None

    return "CVSS:3.1/" + "/".join(f"{m}:{metric_map[m]}" for m in order)


def extract_official_metrics(vector):
    canonical = normalise_vector(vector)

    if canonical is None:
        return {v: None for v in OFFICIAL_METRIC_COLUMNS.values()}

    metric_map = {}

    for part in canonical.split("/"):
        if ":" in part and not part.startswith("CVSS"):
            key, value = part.split(":", 1)
            metric_map[key] = value

    return {
        OFFICIAL_METRIC_COLUMNS["AV"]: metric_map.get("AV"),
        OFFICIAL_METRIC_COLUMNS["AC"]: metric_map.get("AC"),
        OFFICIAL_METRIC_COLUMNS["PR"]: metric_map.get("PR"),
        OFFICIAL_METRIC_COLUMNS["UI"]: metric_map.get("UI"),
        OFFICIAL_METRIC_COLUMNS["S"]: metric_map.get("S"),
        OFFICIAL_METRIC_COLUMNS["C"]: metric_map.get("C"),
        OFFICIAL_METRIC_COLUMNS["I"]: metric_map.get("I"),
        OFFICIAL_METRIC_COLUMNS["A"]: metric_map.get("A"),
    }


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
    return df.to_markdown(index=False)


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

    results = pd.read_excel(RESULTS_FILE)
    truth = pd.read_excel(GROUND_TRUTH_FILE)

    required_truth_cols = [
        "record_id",
        "cve_id",
        "official_cvss_vector",
        "official_base_score",
        "official_severity",
        "epss_score",
        "epss_percentile",
    ]

    missing = [col for col in required_truth_cols if col not in truth.columns]
    if missing:
        raise ValueError(f"Ground-truth file missing columns: {missing}")

    official_metrics = truth["official_cvss_vector"].apply(extract_official_metrics)
    official_metrics_df = pd.DataFrame(list(official_metrics))
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
                *OFFICIAL_METRIC_COLUMNS.values(),
            ]
        ],
        on="record_id",
        how="left",
    )

    joined["canonical_predicted_vector"] = joined["predicted_vector"].apply(normalise_vector)
    joined["canonical_official_vector"] = joined["official_cvss_vector"].apply(normalise_vector)

    joined["canonical_vector_match"] = (
        joined["canonical_predicted_vector"].notna()
        & joined["canonical_official_vector"].notna()
        & (joined["canonical_predicted_vector"] == joined["canonical_official_vector"])
    )

    joined["primary_predicted_score"] = pd.to_numeric(
        joined["calculated_base_score"], errors="coerce"
    )

    joined["official_base_score"] = pd.to_numeric(
        joined["official_base_score"], errors="coerce"
    )

    joined["score_error"] = joined["primary_predicted_score"] - joined["official_base_score"]
    joined["absolute_score_error"] = joined["score_error"].abs()
    joined["predicted_severity"] = joined["primary_predicted_score"].apply(severity_from_score)

    joined["severity_match"] = (
        joined["predicted_severity"].notna()
        & joined["official_severity"].notna()
        & (
            joined["predicted_severity"].astype(str).str.upper()
            == joined["official_severity"].astype(str).str.upper()
        )
    )

    for metric, pred_col in METRIC_COLUMNS.items():
        official_col = OFFICIAL_METRIC_COLUMNS[metric]
        joined[f"{metric}_match"] = (
            joined[pred_col].notna()
            & joined[official_col].notna()
            & (joined[pred_col].astype(str) == joined[official_col].astype(str))
        )

    return joined


def parsed_only(df):
    return df[df["parse_success"] == True].copy()


def create_overall_summary(df):
    parsed = parsed_only(df)

    return pd.DataFrame(
        [
            {
                "total_rows": len(df),
                "parsed_rows_used_for_accuracy": len(parsed),
                "excluded_parse_failures": len(df) - len(parsed),
                "ground_truth_file": str(GROUND_TRUTH_FILE),
                "primary_score_used": "calculated_base_score",
                "epss_column_used": "epss_score",
            }
        ]
    )


def create_metric_agreement_summary(df):
    parsed = parsed_only(df)
    rows = []

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            subset = parsed[
                (parsed["model_name"] == provider)
                & (parsed["prompt_condition"] == condition)
            ]

            row = {"provider": provider, "condition": condition, "n": len(subset)}

            for metric in METRIC_COLUMNS:
                match_col = f"{metric}_match"
                matches = int(subset[match_col].sum())
                row[f"{metric}_agreement_percent"] = pct(matches, len(subset))

            rows.append(row)

    return pd.DataFrame(rows)


def create_vector_match_summary(df):
    parsed = parsed_only(df)
    rows = []

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            subset = parsed[
                (parsed["model_name"] == provider)
                & (parsed["prompt_condition"] == condition)
            ]

            n = len(subset)
            matches = int(subset["canonical_vector_match"].sum())

            rows.append(
                {
                    "provider": provider,
                    "condition": condition,
                    "n": n,
                    "exact_canonical_vector_matches": matches,
                    "exact_vector_match_percent": pct(matches, n),
                }
            )

    return pd.DataFrame(rows)


def create_score_error_summary(df):
    parsed = parsed_only(df)
    rows = []

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            subset = parsed[
                (parsed["model_name"] == provider)
                & (parsed["prompt_condition"] == condition)
            ].dropna(subset=["score_error"])

            rows.append(
                {
                    "provider": provider,
                    "condition": condition,
                    "n": len(subset),
                    "mean_signed_error": round(subset["score_error"].mean(), 4) if len(subset) else None,
                    "mae": round(subset["absolute_score_error"].mean(), 4) if len(subset) else None,
                    "rmse": round(rmse(subset["score_error"]), 4) if len(subset) else None,
                    "min_error": round(subset["score_error"].min(), 4) if len(subset) else None,
                    "max_error": round(subset["score_error"].max(), 4) if len(subset) else None,
                }
            )

    return pd.DataFrame(rows)


def create_severity_match_summary(df):
    parsed = parsed_only(df)
    rows = []

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            subset = parsed[
                (parsed["model_name"] == provider)
                & (parsed["prompt_condition"] == condition)
            ]

            n = len(subset)
            matches = int(subset["severity_match"].sum())

            rows.append(
                {
                    "provider": provider,
                    "condition": condition,
                    "n": n,
                    "severity_matches": matches,
                    "severity_match_percent": pct(matches, n),
                }
            )

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

            rows.append(
                {
                    "provider": provider,
                    "metric": metric,
                    "paired_records": denom,
                    "condition_flips": flips,
                    "flip_rate_percent": pct(flips, denom),
                }
            )

    return pd.DataFrame(rows)


def create_epss_correlation_summary(df):
    rows = []

    baseline = df[["record_id", "official_base_score", "epss_score"]].drop_duplicates()
    rho, p_value, n = spearman_corr(
        baseline["official_base_score"],
        baseline["epss_score"],
    )

    rows.append(
        {
            "provider": "official_cvss",
            "condition": "baseline",
            "score_used": "official_base_score",
            "n": n,
            "spearman_rho": rho,
            "p_value": p_value,
        }
    )

    parsed = parsed_only(df)

    for provider in PROVIDERS:
        for condition in CONDITIONS:
            subset = parsed[
                (parsed["model_name"] == provider)
                & (parsed["prompt_condition"] == condition)
            ]

            rho, p_value, n = spearman_corr(
                subset["primary_predicted_score"],
                subset["epss_score"],
            )

            rows.append(
                {
                    "provider": provider,
                    "condition": condition,
                    "score_used": "calculated_base_score",
                    "n": n,
                    "spearman_rho": rho,
                    "p_value": p_value,
                }
            )

    return pd.DataFrame(rows)


def write_report(
    overall,
    metric_agreement,
    vector_match,
    score_error,
    severity_match,
    condition_flips,
    epss_correlation,
):
    lines = []

    lines.append("# Pilot Accuracy Report\n")

    lines.append("## Purpose\n")
    lines.append(
        "This report evaluates pilot accuracy by comparing parsed LLM-generated CVSS outputs against official CVSS ground truth and EPSS scores. "
        "Rows that failed parsing were excluded from accuracy calculations because no valid structured prediction was available.\n"
    )

    lines.append("## Methodological Notes\n")
    lines.append(
        "- Exact vector match uses canonicalised CVSS vectors rather than raw string equality.\n"
        "- Base score accuracy uses `calculated_base_score` as the primary predicted score, derived from the predicted vector.\n"
        "- Mean Absolute Error (MAE), Mean Signed Error, and Root Mean Squared Error (RMSE) are reported for base-score error.\n"
        "- Spearman's rho is used for CVSS-EPSS correlation.\n"
        "- Official CVSS versus EPSS is included as a baseline.\n"
        "- EPSS score column used: `epss_score`.\n"
    )

    lines.append("## Table 1: Overall Accuracy Dataset Summary\n")
    lines.append(dataframe_to_markdown(overall))
    lines.append("\n")

    lines.append("## Table 2: Per-Metric Agreement Summary\n")
    lines.append(dataframe_to_markdown(metric_agreement))
    lines.append("\n")

    lines.append("## Table 3: Exact Canonical Vector Match Summary\n")
    lines.append(dataframe_to_markdown(vector_match))
    lines.append("\n")

    lines.append("## Table 4: Base Score Error Summary\n")
    lines.append(dataframe_to_markdown(score_error))
    lines.append("\n")

    lines.append("## Table 5: Severity Match Summary\n")
    lines.append(dataframe_to_markdown(severity_match))
    lines.append("\n")

    lines.append("## Table 6: Prompt Condition Flip Summary\n")
    lines.append(dataframe_to_markdown(condition_flips))
    lines.append("\n")

    lines.append("## Table 7: CVSS-EPSS Spearman Correlation Summary\n")
    lines.append(dataframe_to_markdown(epss_correlation))
    lines.append("\n")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    joined = load_and_join()

    overall = create_overall_summary(joined)
    metric_agreement = create_metric_agreement_summary(joined)
    vector_match = create_vector_match_summary(joined)
    score_error = create_score_error_summary(joined)
    severity_match = create_severity_match_summary(joined)
    condition_flips = create_condition_flip_summary(joined)
    epss_correlation = create_epss_correlation_summary(joined)

    joined.to_excel(JOINED_FILE, index=False)

    with pd.ExcelWriter(SUMMARY_FILE, engine="openpyxl") as writer:
        overall.to_excel(writer, sheet_name="overall", index=False)
        metric_agreement.to_excel(writer, sheet_name="metric_agreement", index=False)
        vector_match.to_excel(writer, sheet_name="vector_match", index=False)
        score_error.to_excel(writer, sheet_name="score_error", index=False)
        severity_match.to_excel(writer, sheet_name="severity_match", index=False)
        condition_flips.to_excel(writer, sheet_name="condition_flips", index=False)
        epss_correlation.to_excel(writer, sheet_name="epss_correlation", index=False)

    write_report(
        overall,
        metric_agreement,
        vector_match,
        score_error,
        severity_match,
        condition_flips,
        epss_correlation,
    )

    print("=" * 80)
    print("Pilot accuracy analysis complete")
    print("=" * 80)
    print(f"Joined rows written to: {JOINED_FILE}")
    print(f"Excel summary written to: {SUMMARY_FILE}")
    print(f"Markdown report written to: {REPORT_FILE}")


if __name__ == "__main__":
    main()