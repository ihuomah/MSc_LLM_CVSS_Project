# Main Accuracy Report

## Purpose

This report evaluates the main experiment by comparing LLM-generated CVSS outputs with the official NVD-grounded CVSS values in the verification dataset. It includes metric-level agreement, exact vector match, base-score error, severity agreement, prompt-condition flips, EPSS correlation, and internal vector-score consistency.

## Methodological Notes

- The analysis joins the combined result file to `main_record_verification_v1.parquet` using `record_id`.
- All 1,000 records are retained. The verification dataset contains both `primary_type` and `nvd_source` values in `cvss_selection_method`; these are carried through for auditability.
- Exact vector match uses canonicalised CVSS v3.1 vectors rather than raw string equality.
- Base-score error uses a score recomputed from the predicted vector inside this analysis script. This avoids relying on the model-reported numeric score.
- Match-rate tables are reported using both parsed-only and all-attempted denominators. In all-attempted mode, unparseable rows remain in the denominator and count as non-matches.
- Mean signed error, MAE, and RMSE are calculated only where a valid parsed vector and numeric official score are available. Unparseable rows are reported as exclusions rather than assigned an artificial error value.
- Spearman's rho is used for CVSS-EPSS correlation, with official CVSS versus EPSS included as a baseline.

## Table 1: Overall Accuracy Dataset Summary

| results_file                                           | ground_truth_file                                                |   total_joined_rows |   expected_rows |   distinct_records |   ground_truth_distinct_records |   api_failures |   parse_failures |   parsed_rows |   unparseable_rows | score_used_for_error_metrics                         | match_rate_denominators       | error_metric_denominator   |   official_vector_nulls_after_join |   official_score_nulls_after_join |   primary_type_records |   nvd_source_records |
|:-------------------------------------------------------|:-----------------------------------------------------------------|--------------------:|----------------:|-------------------:|--------------------------------:|---------------:|-----------------:|--------------:|-------------------:|:-----------------------------------------------------|:------------------------------|:---------------------------|-----------------------------------:|----------------------------------:|-----------------------:|---------------------:|
| main_study\results\raw_results\run_001_results.parquet | main_study\experiment_inputs\main_record_verification_v1.parquet |                6000 |            6000 |               1000 |                            1000 |              0 |               65 |          5935 |                 65 | analysis_calculated_base_score_from_predicted_vector | parsed_only and all_attempted | parsed_only_with_score     |                                  0 |                                 0 |                    993 |                    7 |


## Table 2: Ground-Truth Provenance Summary

| cvss_selection_method   | official_severity   |   record_count |
|:------------------------|:--------------------|---------------:|
| nvd_source              | CRITICAL            |              3 |
| nvd_source              | HIGH                |              1 |
| nvd_source              | LOW                 |              1 |
| nvd_source              | MEDIUM              |              2 |
| primary_type            | CRITICAL            |            247 |
| primary_type            | HIGH                |            249 |
| primary_type            | LOW                 |            249 |
| primary_type            | MEDIUM              |            248 |


## Table 3: Parse Denominator Summary

| provider   | condition    |   all_attempted_rows |   parsed_rows |   unparseable_rows |   parse_rate_percent |
|:-----------|:-------------|---------------------:|--------------:|-------------------:|---------------------:|
| openai     | conventional |                 1000 |          1000 |                  0 |                100   |
| openai     | structured   |                 1000 |          1000 |                  0 |                100   |
| gemini     | conventional |                 1000 |          1000 |                  0 |                100   |
| gemini     | structured   |                 1000 |           995 |                  5 |                 99.5 |
| ollama     | conventional |                 1000 |          1000 |                  0 |                100   |
| ollama     | structured   |                 1000 |           940 |                 60 |                 94   |


## Table 4: Per-Metric Agreement Summary

| denominator_mode   | provider   | condition    |    n |   unparseable_rows_in_denominator |   AV_matches |   AV_agreement_percent |   AC_matches |   AC_agreement_percent |   PR_matches |   PR_agreement_percent |   UI_matches |   UI_agreement_percent |   S_matches |   S_agreement_percent |   C_matches |   C_agreement_percent |   I_matches |   I_agreement_percent |   A_matches |   A_agreement_percent |
|:-------------------|:-----------|:-------------|-----:|----------------------------------:|-------------:|-----------------------:|-------------:|-----------------------:|-------------:|-----------------------:|-------------:|-----------------------:|------------:|----------------------:|------------:|----------------------:|------------:|----------------------:|------------:|----------------------:|
| parsed_only        | openai     | conventional | 1000 |                                 0 |          898 |                  89.8  |          925 |                  92.5  |          737 |                  73.7  |          918 |                  91.8  |         953 |                 95.3  |         793 |                 79.3  |         839 |                 83.9  |         849 |                 84.9  |
| parsed_only        | openai     | structured   | 1000 |                                 0 |          894 |                  89.4  |          918 |                  91.8  |          747 |                  74.7  |          915 |                  91.5  |         951 |                 95.1  |         798 |                 79.8  |         830 |                 83    |         842 |                 84.2  |
| parsed_only        | gemini     | conventional | 1000 |                                 0 |          878 |                  87.8  |          907 |                  90.7  |          724 |                  72.4  |          922 |                  92.2  |         687 |                 68.7  |         770 |                 77    |         797 |                 79.7  |         842 |                 84.2  |
| parsed_only        | gemini     | structured   |  995 |                                 0 |          877 |                  88.14 |          904 |                  90.85 |          728 |                  73.17 |          913 |                  91.76 |         668 |                 67.14 |         770 |                 77.39 |         800 |                 80.4  |         827 |                 83.12 |
| parsed_only        | ollama     | conventional | 1000 |                                 0 |          284 |                  28.4  |          948 |                  94.8  |          489 |                  48.9  |          836 |                  83.6  |         888 |                 88.8  |         528 |                 52.8  |         564 |                 56.4  |         681 |                 68.1  |
| parsed_only        | ollama     | structured   |  940 |                                 0 |          320 |                  34.04 |          777 |                  82.66 |          514 |                  54.68 |          712 |                  75.74 |         769 |                 81.81 |         522 |                 55.53 |         513 |                 54.57 |         487 |                 51.81 |
| all_attempted      | openai     | conventional | 1000 |                                 0 |          898 |                  89.8  |          925 |                  92.5  |          737 |                  73.7  |          918 |                  91.8  |         953 |                 95.3  |         793 |                 79.3  |         839 |                 83.9  |         849 |                 84.9  |
| all_attempted      | openai     | structured   | 1000 |                                 0 |          894 |                  89.4  |          918 |                  91.8  |          747 |                  74.7  |          915 |                  91.5  |         951 |                 95.1  |         798 |                 79.8  |         830 |                 83    |         842 |                 84.2  |
| all_attempted      | gemini     | conventional | 1000 |                                 0 |          878 |                  87.8  |          907 |                  90.7  |          724 |                  72.4  |          922 |                  92.2  |         687 |                 68.7  |         770 |                 77    |         797 |                 79.7  |         842 |                 84.2  |
| all_attempted      | gemini     | structured   | 1000 |                                 5 |          877 |                  87.7  |          904 |                  90.4  |          728 |                  72.8  |          913 |                  91.3  |         668 |                 66.8  |         770 |                 77    |         800 |                 80    |         827 |                 82.7  |
| all_attempted      | ollama     | conventional | 1000 |                                 0 |          284 |                  28.4  |          948 |                  94.8  |          489 |                  48.9  |          836 |                  83.6  |         888 |                 88.8  |         528 |                 52.8  |         564 |                 56.4  |         681 |                 68.1  |
| all_attempted      | ollama     | structured   | 1000 |                                60 |          320 |                  32    |          777 |                  77.7  |          514 |                  51.4  |          712 |                  71.2  |         769 |                 76.9  |         522 |                 52.2  |         513 |                 51.3  |         487 |                 48.7  |


## Table 5: Exact Canonical Vector Match Summary

| denominator_mode   | provider   | condition    |    n |   unparseable_rows_in_denominator |   exact_canonical_vector_matches |   exact_vector_match_percent |
|:-------------------|:-----------|:-------------|-----:|----------------------------------:|---------------------------------:|-----------------------------:|
| parsed_only        | openai     | conventional | 1000 |                                 0 |                              423 |                        42.3  |
| parsed_only        | openai     | structured   | 1000 |                                 0 |                              420 |                        42    |
| parsed_only        | gemini     | conventional | 1000 |                                 0 |                              265 |                        26.5  |
| parsed_only        | gemini     | structured   |  995 |                                 0 |                              241 |                        24.22 |
| parsed_only        | ollama     | conventional | 1000 |                                 0 |                               51 |                         5.1  |
| parsed_only        | ollama     | structured   |  940 |                                 0 |                               19 |                         2.02 |
| all_attempted      | openai     | conventional | 1000 |                                 0 |                              423 |                        42.3  |
| all_attempted      | openai     | structured   | 1000 |                                 0 |                              420 |                        42    |
| all_attempted      | gemini     | conventional | 1000 |                                 0 |                              265 |                        26.5  |
| all_attempted      | gemini     | structured   | 1000 |                                 5 |                              241 |                        24.1  |
| all_attempted      | ollama     | conventional | 1000 |                                 0 |                               51 |                         5.1  |
| all_attempted      | ollama     | structured   | 1000 |                                60 |                               19 |                         1.9  |


## Table 6: Severity Match Summary

| denominator_mode   | provider   | condition    |    n |   unparseable_rows_in_denominator |   severity_matches |   severity_match_percent |
|:-------------------|:-----------|:-------------|-----:|----------------------------------:|-------------------:|-------------------------:|
| parsed_only        | openai     | conventional | 1000 |                                 0 |                576 |                    57.6  |
| parsed_only        | openai     | structured   | 1000 |                                 0 |                581 |                    58.1  |
| parsed_only        | gemini     | conventional | 1000 |                                 0 |                551 |                    55.1  |
| parsed_only        | gemini     | structured   |  995 |                                 0 |                555 |                    55.78 |
| parsed_only        | ollama     | conventional | 1000 |                                 0 |                215 |                    21.5  |
| parsed_only        | ollama     | structured   |  940 |                                 0 |                253 |                    26.91 |
| all_attempted      | openai     | conventional | 1000 |                                 0 |                576 |                    57.6  |
| all_attempted      | openai     | structured   | 1000 |                                 0 |                581 |                    58.1  |
| all_attempted      | gemini     | conventional | 1000 |                                 0 |                551 |                    55.1  |
| all_attempted      | gemini     | structured   | 1000 |                                 5 |                555 |                    55.5  |
| all_attempted      | ollama     | conventional | 1000 |                                 0 |                215 |                    21.5  |
| all_attempted      | ollama     | structured   | 1000 |                                60 |                253 |                    25.3  |


## Table 7: Base Score Error Summary

| provider   | condition    |   attempted_rows |   parsed_rows |   unparseable_rows_excluded |   rows_used_for_error_metrics |   rows_excluded_from_error_metrics |   mean_signed_error |    mae |   rmse |   min_error |   max_error |
|:-----------|:-------------|-----------------:|--------------:|----------------------------:|------------------------------:|-----------------------------------:|--------------------:|-------:|-------:|------------:|------------:|
| openai     | conventional |             1000 |          1000 |                           0 |                          1000 |                                  0 |              0.0534 | 1.107  | 1.7647 |        -7.5 |         6.7 |
| openai     | structured   |             1000 |          1000 |                           0 |                          1000 |                                  0 |             -0.1091 | 1.0941 | 1.7359 |        -7   |         6.7 |
| gemini     | conventional |             1000 |          1000 |                           0 |                          1000 |                                  0 |              0.646  | 1.3028 | 1.9717 |        -5.5 |         7.6 |
| gemini     | structured   |             1000 |           995 |                           5 |                           995 |                                  5 |              0.6382 | 1.282  | 1.9333 |        -6.7 |         7.1 |
| ollama     | conventional |             1000 |          1000 |                           0 |                          1000 |                                  0 |              1.9879 | 2.5107 | 3.174  |        -3.8 |         7.4 |
| ollama     | structured   |             1000 |           940 |                          60 |                           887 |                                113 |              0.768  | 2.0514 | 2.5603 |        -6.7 |         7.7 |


## Table 8: Prompt Condition Flip Summary

| provider   | metric   |   paired_parseable_records |   condition_flips |   flip_rate_percent |
|:-----------|:---------|---------------------------:|------------------:|--------------------:|
| openai     | AV       |                       1000 |                26 |                2.6  |
| openai     | AC       |                       1000 |                27 |                2.7  |
| openai     | PR       |                       1000 |                73 |                7.3  |
| openai     | UI       |                       1000 |                27 |                2.7  |
| openai     | S        |                       1000 |                10 |                1    |
| openai     | C        |                       1000 |                66 |                6.6  |
| openai     | I        |                       1000 |                51 |                5.1  |
| openai     | A        |                       1000 |                56 |                5.6  |
| gemini     | AV       |                        995 |                34 |                3.42 |
| gemini     | AC       |                        995 |                49 |                4.92 |
| gemini     | PR       |                        995 |               107 |               10.75 |
| gemini     | UI       |                        995 |                24 |                2.41 |
| gemini     | S        |                        995 |               179 |               17.99 |
| gemini     | C        |                        995 |                79 |                7.94 |
| gemini     | I        |                        995 |                74 |                7.44 |
| gemini     | A        |                        995 |                69 |                6.93 |
| ollama     | AV       |                        940 |               338 |               35.96 |
| ollama     | AC       |                        940 |               121 |               12.87 |
| ollama     | PR       |                        940 |               158 |               16.81 |
| ollama     | UI       |                        940 |               160 |               17.02 |
| ollama     | S        |                        940 |               109 |               11.6  |
| ollama     | C        |                        940 |               410 |               43.62 |
| ollama     | I        |                        935 |               192 |               20.53 |
| ollama     | A        |                        940 |               475 |               50.53 |


## Table 9: CVSS-EPSS Spearman Correlation Summary

| provider      | condition    | score_used                                           |    n |   spearman_rho |   p_value |
|:--------------|:-------------|:-----------------------------------------------------|-----:|---------------:|----------:|
| official_cvss | baseline     | official_base_score                                  | 1000 |         0.5342 |    0      |
| openai        | conventional | analysis_calculated_base_score_from_predicted_vector | 1000 |         0.529  |    0      |
| openai        | structured   | analysis_calculated_base_score_from_predicted_vector | 1000 |         0.5423 |    0      |
| gemini        | conventional | analysis_calculated_base_score_from_predicted_vector | 1000 |         0.4654 |    0      |
| gemini        | structured   | analysis_calculated_base_score_from_predicted_vector |  995 |         0.4951 |    0      |
| ollama        | conventional | analysis_calculated_base_score_from_predicted_vector | 1000 |         0.059  |    0.0621 |
| ollama        | structured   | analysis_calculated_base_score_from_predicted_vector |  887 |         0.2407 |    0      |


## Table 10: Internal Vector-Score Consistency Summary

| provider   | condition    |   parsed_rows |   rows_with_model_score_and_vector_score |   internally_consistent_rows_tolerance_0_15 |   internally_inconsistent_rows_tolerance_0_15 |   internal_consistency_rate_percent |   mean_model_minus_vector_score_delta |   max_abs_model_minus_vector_score_delta |
|:-----------|:-------------|--------------:|-----------------------------------------:|--------------------------------------------:|----------------------------------------------:|------------------------------------:|--------------------------------------:|-----------------------------------------:|
| openai     | conventional |          1000 |                                     1000 |                                         985 |                                            15 |                               98.5  |                                0.0026 |                                      0.6 |
| openai     | structured   |          1000 |                                     1000 |                                         968 |                                            32 |                               96.8  |                                0.0079 |                                      1.1 |
| gemini     | conventional |          1000 |                                     1000 |                                         877 |                                           123 |                               87.7  |                                0.0187 |                                      9.9 |
| gemini     | structured   |           995 |                                      995 |                                         854 |                                           141 |                               85.83 |                                0.0366 |                                      2.1 |
| ollama     | conventional |          1000 |                                     1000 |                                         256 |                                           744 |                               25.6  |                               -0.7109 |                                      9.8 |
| ollama     | structured   |           940 |                                      887 |                                          63 |                                           824 |                                7.1  |                                0.4699 |                                     33.6 |


## Table 11: Runtime Recompute Cross-Check

|   parsed_rows |   rows_with_analysis_and_runtime_scores |   matching_scores |   mismatching_scores |   max_abs_delta |
|--------------:|----------------------------------------:|------------------:|---------------------:|----------------:|
|          5935 |                                    5882 |              5882 |                    0 |               0 |


## Table 12: Runtime Recompute Mismatch Inventory

_No rows._


## Table 13: Unparseable Output Inventory

|   record_id | cve_id         | model_name   | prompt_condition   | compliance_category   | official_cvss_vector                         |   official_base_score | official_severity   | cvss_selection_method   |   predicted_vector |   predicted_base_score |
|------------:|:---------------|:-------------|:-------------------|:----------------------|:---------------------------------------------|----------------------:|:--------------------|:------------------------|-------------------:|-----------------------:|
|         426 | CVE-2023-1696  | gemini       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H |                   7.5 | HIGH                | primary_type            |                nan |                    nan |
|         555 | CVE-2024-39324 | gemini       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:L |                   3.8 | LOW                 | primary_type            |                nan |                    nan |
|         565 | CVE-2025-7167  | gemini       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H |                   8.8 | HIGH                | primary_type            |                nan |                    nan |
|         592 | CVE-2023-28372 | gemini       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:L |                   2.7 | LOW                 | primary_type            |                nan |                    nan |
|         901 | CVE-2024-23591 | gemini       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:N |                   2.3 | LOW                 | primary_type            |                nan |                    nan |
|          29 | CVE-2022-34452 | ollama       | structured         | parser_exception      | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:N |                   2.7 | LOW                 | primary_type            |                nan |                    nan |
|          66 | CVE-2024-22068 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N |                   6.5 | MEDIUM              | primary_type            |                nan |                    nan |
|          72 | CVE-2015-10091 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H |                   7.2 | HIGH                | primary_type            |                nan |                    nan |
|          80 | CVE-2023-49230 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H |                   8.8 | HIGH                | primary_type            |                nan |                    nan |
|          81 | CVE-2026-33596 | ollama       | structured         | invalid               | CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H |                   6.5 | MEDIUM              | primary_type            |                nan |                    nan |
|         109 | CVE-2023-2531  | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         118 | CVE-2021-44190 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N |                   3.3 | LOW                 | primary_type            |                nan |                    nan |
|         130 | CVE-2023-43295 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N |                   3.5 | LOW                 | primary_type            |                nan |                    nan |
|         147 | CVE-2024-52054 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:N |                   2.7 | LOW                 | primary_type            |                nan |                    nan |
|         196 | CVE-2023-41189 | ollama       | structured         | invalid               | CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   8.8 | HIGH                | primary_type            |                nan |                    nan |
|         222 | CVE-2026-43077 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H |                   5.5 | MEDIUM              | primary_type            |                nan |                    nan |
|         233 | CVE-2025-5353  | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H |                   7.8 | HIGH                | primary_type            |                nan |                    nan |
|         248 | CVE-2023-47248 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         289 | CVE-2023-50000 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         293 | CVE-2024-26738 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H |                   5.5 | MEDIUM              | primary_type            |                nan |                    nan |
|         297 | CVE-2023-3511  | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N |                   3.5 | LOW                 | primary_type            |                nan |                    nan |
|         302 | CVE-2024-39502 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H |                   7.8 | HIGH                | primary_type            |                nan |                    nan |
|         305 | CVE-2023-28428 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L |                   3.3 | LOW                 | primary_type            |                nan |                    nan |
|         327 | CVE-2022-27641 | ollama       | structured         | invalid               | CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   8.8 | HIGH                | primary_type            |                nan |                    nan |
|         359 | CVE-2022-27538 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H |                   7   | HIGH                | primary_type            |                nan |                    nan |
|         365 | CVE-2023-38954 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         372 | CVE-2022-49092 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H |                   5.5 | MEDIUM              | primary_type            |                nan |                    nan |
|         375 | CVE-2025-49836 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         377 | CVE-2023-21093 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H |                   7.8 | HIGH                | primary_type            |                nan |                    nan |
|         392 | CVE-2023-42277 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         407 | CVE-2026-24733 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N |                   3.7 | LOW                 | primary_type            |                nan |                    nan |
|         418 | CVE-2023-2602  | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L |                   3.3 | LOW                 | primary_type            |                nan |                    nan |
|         443 | CVE-2024-34617 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N |                   3.3 | LOW                 | primary_type            |                nan |                    nan |
|         469 | CVE-2024-50079 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H |                   5.5 | MEDIUM              | primary_type            |                nan |                    nan |
|         490 | CVE-2026-33595 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H |                   7.5 | HIGH                | primary_type            |                nan |                    nan |
|         508 | CVE-2024-26619 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H |                   7.8 | HIGH                | primary_type            |                nan |                    nan |
|         523 | CVE-2023-6251  | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N |                   3.5 | LOW                 | primary_type            |                nan |                    nan |
|         529 | CVE-2023-20625 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H |                   6.4 | MEDIUM              | primary_type            |                nan |                    nan |
|         552 | CVE-2024-55885 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N |                   7.5 | HIGH                | primary_type            |                nan |                    nan |
|         553 | CVE-2024-47687 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H |                   5.5 | MEDIUM              | primary_type            |                nan |                    nan |
|         569 | CVE-2023-46589 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N |                   7.5 | HIGH                | primary_type            |                nan |                    nan |
|         574 | CVE-2025-62849 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         593 | CVE-2023-53319 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H |                   5.5 | MEDIUM              | primary_type            |                nan |                    nan |
|         601 | CVE-2023-20965 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         608 | CVE-2024-21480 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         624 | CVE-2023-0744  | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         658 | CVE-2025-5450  | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:N |                   2.7 | LOW                 | primary_type            |                nan |                    nan |
|         707 | CVE-2023-46886 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N |                   9.1 | CRITICAL            | primary_type            |                nan |                    nan |
|         731 | CVE-2023-24165 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         736 | CVE-2023-41044 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:N |                   3.8 | LOW                 | primary_type            |                nan |                    nan |
|         741 | CVE-2024-26992 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N |                   3.3 | LOW                 | primary_type            |                nan |                    nan |
|         753 | CVE-2023-5920  | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N |                   3.3 | LOW                 | primary_type            |                nan |                    nan |
|         757 | CVE-2024-44020 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H |                   8.8 | HIGH                | primary_type            |                nan |                    nan |
|         780 | CVE-2025-21892 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H |                   4.7 | MEDIUM              | primary_type            |                nan |                    nan |
|         781 | CVE-2024-8461  | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N |                   5.3 | MEDIUM              | primary_type            |                nan |                    nan |
|         793 | CVE-2023-5449  | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N |                   3.3 | LOW                 | primary_type            |                nan |                    nan |
|         837 | CVE-2023-50263 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N |                   5.3 | MEDIUM              | primary_type            |                nan |                    nan |
|         847 | CVE-2024-46755 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H |                   5.5 | MEDIUM              | primary_type            |                nan |                    nan |
|         882 | CVE-2025-62848 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H |                   7.5 | HIGH                | primary_type            |                nan |                    nan |
|         896 | CVE-2024-33054 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H |                   7.8 | HIGH                | primary_type            |                nan |                    nan |
|         930 | CVE-2026-28540 | ollama       | structured         | invalid               | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N |                   3.3 | LOW                 | primary_type            |                nan |                    nan |
|         931 | CVE-2023-28180 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H |                   6.5 | MEDIUM              | primary_type            |                nan |                    nan |
|         953 | CVE-2025-55736 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N |                   6.5 | MEDIUM              | primary_type            |                nan |                    nan |
|         960 | CVE-2023-37266 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |
|         984 | CVE-2023-49291 | ollama       | structured         | invalid               | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |                   9.8 | CRITICAL            | primary_type            |                nan |                    nan |

