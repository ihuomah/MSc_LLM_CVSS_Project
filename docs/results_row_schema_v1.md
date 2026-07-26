# Results Row Schema v1

## Purpose

This document defines the structure of the experiment results produced during the LLM-CVSS evaluation.

The aim is to separate:

1. Raw model-output results
2. Analysis-ready results

This separation preserves the boundary between what the model produced and the ground-truth data used later for evaluation.

---

## Design Rule

The inference script writes only raw model-output results.

Ground truth, EPSS values, and derived accuracy metrics are added later during analysis by joining raw results to the frozen Pilot v2 verification file.

This avoids mixing model output with evaluation data at inference time.

---

## Raw Results Table

The raw results table contains one row per:

```text
record_id + model_name + prompt_condition + run_index
```

For the pilot experiment:

```text
50 CVEs × 3 models × 2 prompt conditions × 1 run = 300 rows
```

---

## Raw Results Columns

| Column                  | Description                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------- |
| record_id               | Frozen pilot record identifier. Used to link back to the verification file.                             |
| model_name              | Model provider/category, e.g. openai, gemini, ollama.                                                   |
| model_snapshot          | Exact model identifier used at inference time.                                                          |
| prompt_condition        | Prompt condition used. Valid values: standard, structured.                                              |
| run_index               | Run number. For pilot this is 1. For repeatability tests this may be 1, 2, 3, etc.                      |
| timestamp               | Date and time inference completed, in ISO 8601 format.                                                  |
| inference_latency_ms    | Time taken for model response, in milliseconds.                                                         |
| provider_fingerprint    | Provider-specific reproducibility identifier, if available. Otherwise blank/null.                       |
| raw_response_file       | Path to the saved raw model response text file.                                                         |
| parse_success           | Whether the parser successfully extracted valid JSON.                                                   |
| compliance_category     | Output compliance category: strict, fenced, embedded, invalid.                                          |
| all_keys_present        | Whether all expected JSON keys were present.                                                            |
| valid_metric_values     | Whether all CVSS metric values were from the allowed sets.                                              |
| base_score_numeric      | Whether the reported base score was numeric.                                                            |
| vector_string_present   | Whether a valid CVSS vector string was present.                                                         |
| attack_vector           | Model-generated CVSS Attack Vector value.                                                               |
| attack_complexity       | Model-generated CVSS Attack Complexity value.                                                           |
| privileges_required     | Model-generated CVSS Privileges Required value.                                                         |
| user_interaction        | Model-generated CVSS User Interaction value.                                                            |
| scope                   | Model-generated CVSS Scope value.                                                                       |
| confidentiality_impact  | Model-generated CVSS Confidentiality Impact value.                                                      |
| integrity_impact        | Model-generated CVSS Integrity Impact value.                                                            |
| availability_impact     | Model-generated CVSS Availability Impact value.                                                         |
| predicted_vector        | Model-generated CVSS v3.1 vector string.                                                                |
| predicted_base_score    | Model-reported CVSS base score.                                                                         |
| calculated_base_score   | CVSS base score recalculated from the model-generated vector using the validated CVSS library.          |
| vector_score_delta      | Difference between model-reported score and recalculated score.                                         |
| vector_score_consistent | Whether the model-reported score is consistent with the recalculated score within the chosen tolerance. |
| parser_error            | Error message if parsing or validation failed. Blank/null if no error.                                  |

---

## Compliance Categories

| Category | Meaning                                                              |
| -------- | -------------------------------------------------------------------- |
| strict   | The response is exactly one JSON object with no extra text.          |
| fenced   | The response is only markdown-fenced JSON with no surrounding prose. |
| embedded | Valid JSON appears inside surrounding text or explanation.           |
| invalid  | No valid JSON object can be extracted.                               |

---

## Analysis-Ready Results Table

The analysis-ready table is derived later by joining:

```text
raw_results
+
pilot_record_id_verification_v2.xlsx
```

using:

```text
record_id
```

The verification file provides:

```text
cve_id
final_description
official_cvss_vector
official_base_score
official_severity
epss_score
epss_percentile
has_epss
epss_date
epss_source
```

---

## Analysis-Ready Derived Columns

The analysis stage may add columns such as:

| Column                       | Description                                                                   |
| ---------------------------- | ----------------------------------------------------------------------------- |
| cve_id                       | CVE identifier retrieved through the frozen record mapping/verification file. |
| final_description            | Sanitised vulnerability description used for inference.                       |
| official_cvss_vector         | Ground-truth CVSS vector from NVD.                                            |
| official_base_score          | Ground-truth CVSS base score from NVD.                                        |
| official_severity            | Ground-truth CVSS severity band from NVD.                                     |
| epss_score                   | EPSS probability score from the enrichment snapshot.                          |
| epss_percentile              | EPSS percentile from the enrichment snapshot.                                 |
| score_difference             | Difference between predicted_base_score and official_base_score.              |
| absolute_score_error         | Absolute value of score_difference.                                           |
| vector_exact_match           | Whether predicted_vector exactly matches official_cvss_vector.                |
| severity_match               | Whether predicted severity band matches official_severity.                    |
| attack_vector_match          | Whether attack_vector matches the official AV value.                          |
| attack_complexity_match      | Whether attack_complexity matches the official AC value.                      |
| privileges_required_match    | Whether privileges_required matches the official PR value.                    |
| user_interaction_match       | Whether user_interaction matches the official UI value.                       |
| scope_match                  | Whether scope matches the official S value.                                   |
| confidentiality_impact_match | Whether confidentiality_impact matches the official C value.                  |
| integrity_impact_match       | Whether integrity_impact matches the official I value.                        |
| availability_impact_match    | Whether availability_impact matches the official A value.                     |

---

## Project Rule

Raw model responses are immutable evidence.

Each raw response must be saved to disk exactly as returned by the model before parsing.

The raw results table stores the path to each raw response file.

If parser logic changes later, the raw responses should be re-parsed rather than re-running the models.

---

## Prompt Condition Labels

The accepted prompt condition labels are:

```text
conventional
structured
```

The term `pdl` should not be used as a prompt condition label because Condition 2 is a `structured prompt` submitted as plain text, not a prompt executed through a PDL runtime.

---

## Status

Schema status: v1 locked for pilot inference pipeline development.
