# Main Study Completeness Validation

**Date:** 29 June 2026

## Objective

The purpose of this stage was to verify that the combined results from the main experiment were complete and internally consistent before performing the accuracy, prompt sensitivity, EPSS correlation, and failure mode analyses. This validation ensures that the experimental outputs accurately represent the completed inference runs and that no records were lost or duplicated during result aggregation.

---

# Inputs

Combined results generated using:

```bash
python main_study\scripts\run_main_experiment.py --run-id run_001 --combine-only
```

Input dataset:

```text
main_study/results/raw_results/run_001_results.parquet
```

Total combined rows:

* Expected: 6,000
* Actual: 6,000

---

# Completeness Validation Script

Created:

```text
main_study/scripts/analyse_main_completeness.py
```

Outputs:

```text
main_study/results/analysis/completeness/
```

Generated artefacts:

* main_completeness_summary.xlsx
* main_completeness_report.md

---

# Validation Performed

The completeness script verified:

* Total row count
* Distinct record count
* Provider counts
* Prompt condition counts
* Provider × Prompt distributions
* API success/failure counts
* Parse success/failure counts
* State 1 / State 2 / State 3 classification
* Compliance category distribution
* Parse success × compliance category consistency
* Duplicate detection
* Missing provider/record/prompt combinations
* Unexpected labels
* Retry statistics
* Latency summary
* Internal vector–score consistency

---

# Validation Results

## Dataset Integrity

| Check                | Result |
| -------------------- | ------ |
| Expected rows        | 6,000  |
| Actual rows          | 6,000  |
| Distinct records     | 1,000  |
| Missing combinations | 0      |
| Duplicate rows       | 0      |
| API failures         | 0      |
| Overall completeness | PASS   |

The combined dataset successfully passed all completeness validation checks.

---

# Parse Validation Results

Overall parse failures:

* Total: 65

Provider distribution:

| Provider | Parse Failures |
| -------- | -------------: |
| OpenAI   |              0 |
| Gemini   |              5 |
| Ollama   |             60 |

Prompt distribution:

| Prompt       | Parse Failures |
| ------------ | -------------: |
| Conventional |              0 |
| Structured   |             65 |

Compliance categories:

| Category         | Count |
| ---------------- | ----: |
| Invalid          |    64 |
| Parser Exception |     1 |

The parse success and compliance category cross-tabulation showed complete agreement. All successful parses were classified as either **Strict**, **Fenced**, or **Embedded**, while every parse failure was classified as either **Invalid** or **Parser Exception**. No contradictory classifications were observed.

---

# Failure Investigation

Following completeness validation, representative examples of the parse failures were manually examined.

Findings:

* Representative Ollama failures consisted primarily of narrative responses that did not follow the required structured JSON output format.
* Representative Gemini failures generally produced the expected JSON structure but contained isolated token insertions that rendered the JSON invalid.
* The observed failures were attributable to model output behaviour rather than evidence of inconsistent parser behaviour.

These observations will be discussed further in the Failure Mode Analysis section of Chapter 4.

---

# Decisions Made

The following methodological decisions were confirmed:

1. The Parquet export will be treated as the authoritative experiment dataset.
2. No additional inference runs are required.
3. The completeness stage is considered complete and frozen.
4. The identified parse failures will be retained as observed outputs and analysed as part of RQ5 rather than repaired or regenerated.
5. Subsequent analyses (accuracy, prompt sensitivity, EPSS correlation, and failure mode analysis) will use the validated combined Parquet dataset.

---

# Outcome

The main experiment dataset successfully passed completeness validation and is considered suitable for quantitative analysis.

The next phase of the project is the implementation of the main accuracy analysis using the validated combined dataset together with the official NVD CVSS ground truth.
