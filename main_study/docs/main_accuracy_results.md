# Main Accuracy Analysis Results

**Date:** 2 July 2026

## Purpose

This document records the validated findings from the main accuracy analysis following completion of the 1,000-CVE experiment. It serves as an implementation and analysis log prior to writing Chapters 4 and 5 of the dissertation.

Its purpose is to preserve the methodological decisions, validated outputs, and key observations while they are still fresh, providing an accurate reference for writing the dissertation.

---

# Analysis Inputs

## Inference Results

```text
main_study/results/raw_results/run_001_results.parquet
```

Total inference rows:

* 6,000

Provider–prompt combinations:

* OpenAI × Conventional
* OpenAI × Structured
* Gemini × Conventional
* Gemini × Structured
* Ollama × Conventional
* Ollama × Structured

---

## Ground Truth

```text
main_study/experiment_inputs/main_record_verification_v1.parquet
```

Ground-truth verification:

* 1,000 unique records
* 0 missing official CVSS vectors
* 993 records labelled `primary_type`
* 7 records labelled `nvd_source`

All records were retained because they formed part of the predefined frozen verification dataset. The `cvss_selection_method` field was preserved throughout the analysis for transparency and auditability.

---

# Join Validation

The inference results were successfully joined with the verification dataset.

Validation checks:

* Joined rows: 6,000
* Expected rows: 6,000
* Distinct record IDs: 1,000
* API failures: 0
* Parse failures: 65
* Official vector nulls after join: 0
* Official score nulls after join: 0
* Runtime score recomputation mismatches: 0

These checks confirm that the analysis dataset is complete, internally consistent, and suitable for quantitative evaluation.

---

# Accuracy Methodology

The main analysis preserved the methodology established during the pilot study.

Key design decisions:

* Join inference outputs to the verification dataset using `record_id`.
* Evaluate all 1,000 records contained within the frozen dataset.
* Recompute predicted base scores from the predicted CVSS vectors for analysis.
* Cross-check recomputed scores against the stored `calculated_base_score`.
* Report vector, metric, and severity agreement using both parsed-only and all-attempted denominators.
* Report Mean Signed Error, MAE, and RMSE using successfully scored predictions only.
* Treat State 2 parse failures as non-matches in all-attempted agreement analyses while excluding them from score-error calculations because no valid numeric score exists.

---

# Key Findings

## Exact Canonical Vector Match

OpenAI achieved the highest exact canonical vector agreement under both prompting conditions.

| Provider | Conventional |         Structured |
| -------- | -----------: | -----------------: |
| OpenAI   |        42.3% |              42.0% |
| Gemini   |        26.5% |              24.2% |
| Ollama   |         5.1% | 2.0% (parsed-only) |

Structured prompting did not improve exact vector agreement for any evaluated model.

---

## Base Score Error

OpenAI produced the lowest prediction error across all evaluated models.

| Provider | Conventional MAE | Structured MAE |
| -------- | ---------------: | -------------: |
| OpenAI   |            1.107 |          1.094 |
| Gemini   |            1.303 |          1.282 |
| Ollama   |            2.511 |          2.051 |

OpenAI and Gemini showed only negligible differences between prompting conditions.

Although Ollama's structured MAE was numerically lower, this value was calculated from 887 successfully scored outputs after excluding 113 rows that could not be included in score-error calculations. Consequently, the structured MAE should not be interpreted as evidence that structured prompting improved prediction accuracy.

Mean signed error showed a clear directional trend. OpenAI remained close to unbiased, whereas Gemini and Ollama generally produced positive signed errors, indicating a tendency to assign higher base scores than the official CVSS assessments.

The larger RMSE values relative to MAE across all models indicate that most predictions were reasonably close to the official scores, with a smaller number of substantially larger prediction errors.

---

## Per-Metric Agreement

OpenAI demonstrated consistently high agreement across all eight CVSS metrics.

Gemini produced similar behaviour but exhibited noticeably lower agreement for the Scope metric.

Across both OpenAI and Gemini, **Privileges Required** was the weakest-performing metric, suggesting that reasoning about attacker privilege requirements remained one of the more challenging aspects of CVSS assessment.

Ollama displayed highly uneven performance.

Notable observations included:

* Attack Complexity agreement above 90%.
* Scope agreement above 80%.
* Attack Vector agreement below 35%.

The qualitative failure-mode inspection conducted separately helps explain this result. Representative Ollama failures showed repeated confusion between CVSS Attack Vector categories, including incorrect interpretation of the Adjacent (`A`) and Network (`N`) values. This behaviour is consistent with the low Attack Vector agreement observed across the full evaluation dataset.

The combination of relatively strong performance on several individual metrics but very low exact vector agreement illustrates the strictness of exact vector matching, where every CVSS metric must be predicted correctly simultaneously.

---

## Severity Agreement

Severity agreement exceeded exact vector agreement for every evaluated model.

| Provider | Conventional | Structured (parsed-only) |
| -------- | -----------: | -----------------------: |
| OpenAI   |        57.6% |                    58.1% |
| Gemini   |        55.1% |                    55.8% |
| Ollama   |        21.5% |                    26.9% |

Because severity agreement was also reported using all-attempted denominators, these parsed-only values should be interpreted alongside the corresponding all-attempted results. The observed differences between prompting conditions were generally small and should not be interpreted as evidence that structured prompting consistently improved severity classification.

---

## Prompt Sensitivity

Prompt sensitivity differed substantially between providers.

OpenAI produced highly stable predictions with very low condition-flip rates.

Gemini exhibited moderate prompt sensitivity, particularly for the Scope metric.

Ollama showed the greatest prompt sensitivity.

Largest observed flip rates included:

* Availability: 50.53%
* Confidentiality: 43.62%
* Attack Vector: 35.96%

Unlike the hosted models, Ollama was evaluated under deterministic inference settings (temperature 0 with a fixed seed). Consequently, these prompt-induced changes represent genuine sensitivity to prompt formulation rather than sampling variability.

---

## EPSS Correlation

Official baseline:

* Spearman's ρ = 0.5342

Model correlations:

| Provider | Conventional | Structured |
| -------- | -----------: | ---------: |
| OpenAI   |       0.5290 |     0.5423 |
| Gemini   |       0.4654 |     0.4951 |
| Ollama   |       0.0590 |     0.2407 |

The official CVSS assessment provides the reference relationship between CVSS severity and EPSS exploitability within the evaluation dataset.

OpenAI reproduced this relationship most closely, with correlations essentially matching the official baseline.

Gemini demonstrated moderate positive correlations under both prompting conditions.

Ollama's conventional predictions showed almost no meaningful relationship with EPSS (ρ = 0.059, p = 0.0621), indicating that the observed association was not statistically significant at the conventional 0.05 level.

Although Ollama's structured correlation was numerically higher, it was calculated from 887 successfully scored outputs rather than the full dataset. This value should therefore not be interpreted as evidence that structured prompting improved the relationship with EPSS.

---

## Relationship Between Findings

The independent analyses produced a consistent overall pattern.

Across nearly every evaluation measure:

* OpenAI demonstrated the highest reliability.
* Gemini achieved intermediate performance.
* Ollama demonstrated the lowest reliability and the greatest prompt sensitivity.

Importantly, the independent analyses reinforced one another rather than producing contradictory conclusions. Parseability, exact vector agreement, score error, severity agreement, prompt sensitivity, EPSS correlation, and qualitative failure-mode analysis all converged on the same overall ordering of model reliability.

---

# Research Question Coverage

The completed analyses provide quantitative evidence for all research questions.

**RQ1**

* Exact canonical vector agreement.
* Per-metric agreement across all eight CVSS metrics.

**RQ2**

* Base-score error.
* Severity agreement.

**RQ3**

* EPSS correlation analysis.

**RQ4**

* Prompt sensitivity.
* Condition-flip analysis.

**RQ5**

* Failure-mode analysis documented separately during the completeness investigation.

---

# Notes for Chapter 4

When writing Chapter 4:

* Present quantitative findings before interpretation.
* Distinguish clearly between parseability, exact vector agreement, score error, severity agreement, prompt sensitivity, and EPSS correlation.
* Avoid describing small numerical differences as improvements unless supported by comparable denominators.
* Explain why exact vector agreement is substantially lower than individual metric agreement.
* Emphasise that structured prompting did not produce uniform improvements across providers or evaluation metrics.
* Support interpretation using both the quantitative results and the qualitative failure-mode analysis where appropriate.

---

# Status

The quantitative analysis phase of the dissertation is complete.

The remaining work consists of presenting these validated findings as Chapter 4, interpreting their implications in Chapter 5, and preparing supporting figures and tables for the final dissertation.
