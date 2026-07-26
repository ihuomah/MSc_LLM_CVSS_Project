# Pilot Accuracy Report

## Purpose

This report evaluates pilot accuracy by comparing parsed LLM-generated CVSS outputs against official CVSS ground truth and EPSS scores. Rows that failed parsing were excluded from accuracy calculations because no valid structured prediction was available.

## Methodological Notes

- Exact vector match uses canonicalised CVSS vectors rather than raw string equality.
- Base score accuracy uses `calculated_base_score` as the primary predicted score, derived from the predicted vector.
- Mean Absolute Error (MAE), Mean Signed Error, and Root Mean Squared Error (RMSE) are reported for base-score error.
- Spearman's rho is used for CVSS-EPSS correlation.
- Official CVSS versus EPSS is included as a baseline.
- EPSS score column used: `epss_score`.

## Table 1: Overall Accuracy Dataset Summary

|   total_rows |   parsed_rows_used_for_accuracy |   excluded_parse_failures | ground_truth_file                                                  | primary_score_used    | epss_column_used   |
|-------------:|--------------------------------:|--------------------------:|:-------------------------------------------------------------------|:----------------------|:-------------------|
|          300 |                             297 |                         3 | data\frozen_pilot_v2\datasets\pilot_record_id_verification_v2.xlsx | calculated_base_score | epss_score         |


## Table 2: Per-Metric Agreement Summary

| provider   | condition    |   n |   AV_agreement_percent |   AC_agreement_percent |   PR_agreement_percent |   UI_agreement_percent |   S_agreement_percent |   C_agreement_percent |   I_agreement_percent |   A_agreement_percent |
|:-----------|:-------------|----:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|----------------------:|----------------------:|----------------------:|----------------------:|
| ollama     | conventional |  50 |                  20    |                   96   |                  60    |                  80    |                 82    |                 52    |                 46    |                 50    |
| ollama     | structured   |  48 |                  39.58 |                   87.5 |                  64.58 |                  64.58 |                 72.92 |                 50    |                 52.08 |                 43.75 |
| openai     | conventional |  50 |                  90    |                   92   |                  70    |                  86    |                 90    |                 74    |                 78    |                 74    |
| openai     | structured   |  50 |                  88    |                   90   |                  66    |                  86    |                 90    |                 68    |                 76    |                 76    |
| gemini     | conventional |  50 |                  86    |                   92   |                  72    |                  84    |                 74    |                 64    |                 82    |                 76    |
| gemini     | structured   |  49 |                  89.8  |                   89.8 |                  69.39 |                  85.71 |                 61.22 |                 71.43 |                 81.63 |                 77.55 |


## Table 3: Exact Canonical Vector Match Summary

| provider   | condition    |   n |   exact_canonical_vector_matches |   exact_vector_match_percent |
|:-----------|:-------------|----:|---------------------------------:|-----------------------------:|
| ollama     | conventional |  50 |                                3 |                         6    |
| ollama     | structured   |  48 |                                2 |                         4.17 |
| openai     | conventional |  50 |                               15 |                        30    |
| openai     | structured   |  50 |                               15 |                        30    |
| gemini     | conventional |  50 |                               11 |                        22    |
| gemini     | structured   |  49 |                               10 |                        20.41 |


## Table 4: Base Score Error Summary

| provider   | condition    |   n |   mean_signed_error |    mae |   rmse |   min_error |   max_error |
|:-----------|:-------------|----:|--------------------:|-------:|-------:|------------:|------------:|
| ollama     | conventional |  50 |              1.764  | 2.16   | 2.881  |        -3.3 |         7.1 |
| ollama     | structured   |  48 |              0.9146 | 1.9771 | 2.4226 |        -2.5 |         5.9 |
| openai     | conventional |  50 |             -0.286  | 1.134  | 1.6827 |        -4.7 |         4.8 |
| openai     | structured   |  50 |             -0.42   | 1.312  | 1.9561 |        -5.5 |         4.8 |
| gemini     | conventional |  50 |              0.252  | 1.28   | 1.8065 |        -3.7 |         4.8 |
| gemini     | structured   |  49 |              0.249  | 1.3061 | 1.8133 |        -3.2 |         4.8 |


## Table 5: Severity Match Summary

| provider   | condition    |   n |   severity_matches |   severity_match_percent |
|:-----------|:-------------|----:|-------------------:|-------------------------:|
| ollama     | conventional |  50 |                 15 |                    30    |
| ollama     | structured   |  48 |                 16 |                    33.33 |
| openai     | conventional |  50 |                 30 |                    60    |
| openai     | structured   |  50 |                 29 |                    58    |
| gemini     | conventional |  50 |                 24 |                    48    |
| gemini     | structured   |  49 |                 23 |                    46.94 |


## Table 6: Prompt Condition Flip Summary

| provider   | metric   |   paired_records |   condition_flips |   flip_rate_percent |
|:-----------|:---------|-----------------:|------------------:|--------------------:|
| ollama     | AV       |               48 |                20 |               41.67 |
| ollama     | AC       |               48 |                 6 |               12.5  |
| ollama     | PR       |               48 |                 9 |               18.75 |
| ollama     | UI       |               48 |                10 |               20.83 |
| ollama     | S        |               48 |                 4 |                8.33 |
| ollama     | C        |               48 |                18 |               37.5  |
| ollama     | I        |               47 |                 5 |               10.64 |
| ollama     | A        |               47 |                28 |               59.57 |
| openai     | AV       |               50 |                 1 |                2    |
| openai     | AC       |               50 |                 1 |                2    |
| openai     | PR       |               50 |                 2 |                4    |
| openai     | UI       |               50 |                 2 |                4    |
| openai     | S        |               50 |                 0 |                0    |
| openai     | C        |               50 |                 3 |                6    |
| openai     | I        |               50 |                 1 |                2    |
| openai     | A        |               50 |                 1 |                2    |
| gemini     | AV       |               49 |                 4 |                8.16 |
| gemini     | AC       |               49 |                 1 |                2.04 |
| gemini     | PR       |               49 |                 2 |                4.08 |
| gemini     | UI       |               49 |                 3 |                6.12 |
| gemini     | S        |               49 |                12 |               24.49 |
| gemini     | C        |               49 |                 7 |               14.29 |
| gemini     | I        |               49 |                 6 |               12.24 |
| gemini     | A        |               49 |                 3 |                6.12 |


## Table 7: CVSS-EPSS Spearman Correlation Summary

| provider      | condition    | score_used            |   n |   spearman_rho |   p_value |
|:--------------|:-------------|:----------------------|----:|---------------:|----------:|
| official_cvss | baseline     | official_base_score   |  50 |         0.2695 |    0.0584 |
| ollama        | conventional | calculated_base_score |  50 |        -0.1078 |    0.456  |
| ollama        | structured   | calculated_base_score |  48 |         0.1546 |    0.294  |
| openai        | conventional | calculated_base_score |  50 |         0.285  |    0.0448 |
| openai        | structured   | calculated_base_score |  50 |         0.2172 |    0.1297 |
| gemini        | conventional | calculated_base_score |  50 |         0.355  |    0.0114 |
| gemini        | structured   | calculated_base_score |  49 |         0.4415 |    0.0015 |

