# Main Accuracy Analysis Design

**Date:** 29 June 2026

## Purpose

This document records the methodological decisions made before implementing the main accuracy analysis for the dissertation. The purpose is to ensure that the implementation follows the agreed experimental design and that the rationale behind each decision is documented before any results are generated.

---

# Input Data

## Model Results

Combined inference results:

```text
main_study/results/raw_results/run_001_results.parquet
```

Expected rows:

* 6,000

Completed completeness validation:

* PASS

---

## Ground Truth

Ground truth source:

```text
main_study/experiment_inputs/main_record_verification_v1.parquet
```

Verified contents:

* record_id
* cve_id
* official_cvss_vector
* official_base_score
* official_severity
* epss_score
* epss_percentile
* published_year
* cvss_selection_method

Dataset characteristics:

* 1,000 records
* 0 missing official CVSS vectors
* 993 records labelled `primary_type`
* 7 records labelled `nvd_source`

The seven `nvd_source` records contain complete official CVSS vectors and scores and remain part of the frozen verification dataset. They will therefore be retained in the analysis to preserve consistency with the predefined 1,000-record experimental dataset. The `cvss_selection_method` column will be retained for auditability.

---

# Join Strategy

The analysis joins the combined inference results to the verification dataset using:

```text
record_id
```

Following the join:

* no official vectors should be missing
* row count should remain 6,000

The analysis script will explicitly verify this before continuing.

---

# Accuracy Measures

The analysis evaluates multiple complementary measures of reliability.

These include:

* Exact CVSS vector agreement
* Per-metric agreement
* Base-score error
* Severity agreement
* Prompt-condition differences
* EPSS correlation

No single metric is treated as sufficient on its own.

---

# Base Score Decision

The analysis uses the CVSS score calculated from the predicted vector rather than relying solely on the numeric score written by the model.

This ensures that the evaluation measures the correctness of the predicted CVSS assessment rather than the model's arithmetic.

The recomputed score will be cross-checked against the stored `calculated_base_score` column for validation.

---

# Treatment of Parse Failures

The completeness analysis identified:

* 65 State 2 rows
* API successful
* Parsing unsuccessful

These rows are handled differently depending on the metric.

## Match-rate metrics

The following are reported twice:

* Parsed rows only
* All attempted inferences

For the all-attempted analysis, State 2 rows contribute to the denominator but cannot contribute to the numerator because no valid prediction exists.

## Error metrics

Mean Signed Error

MAE

RMSE

These metrics are calculated only on successfully parsed predictions because no numeric prediction exists for unparseable outputs.

The number of excluded rows will be reported explicitly.

---

# Continuity with the Pilot Study

The main analysis preserves the evaluation methodology established during the pilot study.

Changes from the pilot are limited to:

* scaling from 50 to 1,000 CVEs
* use of the validated combined Parquet dataset
* explicit handling of State 2 parse failures
* additional verification of ground-truth provenance

---

# Expected Outputs

The analysis will generate:

* Joined analysis dataset
* Overall accuracy summaries
* Per-metric accuracy tables
* Exact vector agreement
* Base-score error summaries
* Severity agreement
* Prompt-condition comparison
* EPSS correlation analysis
* Markdown summary report

These outputs form the primary quantitative evidence used to answer Research Questions 1–4.

---

# Status

The methodology for the main accuracy analysis is considered frozen.

The next step is execution of:

```text
main_study/scripts/analyse_main_accuracy.py
```
