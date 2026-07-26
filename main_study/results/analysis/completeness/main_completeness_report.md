# Main Experiment Completeness Report

## Verdict

- Row count complete: True
- Distinct record count complete: True
- No API failures: True
- No duplicate record/model/prompt rows: True
- No missing record/model/prompt combinations: True
- No unexpected labels: True
- Overall completeness pass: True

## Purpose

This report checks whether the combined main experiment output is complete and internally consistent before accuracy, prompt sensitivity, EPSS correlation, and failure-mode analyses are performed. It does not make claims about correctness against official CVSS ground truth.

## Summary

The main experiment expected 6000 inference rows and produced 6000 rows across 1000 distinct records. The combined dataset contains 6000 API-successful rows and 0 API failure(s). There were 5935 successful parses and 65 parse failure(s), giving an overall parse rate of 98.92%. State 2 rows, where the API call succeeded but parsing failed, totalled 65 and are retained as observed evidence for failure-mode analysis.

## Table 1: Verdict Summary

|   row_count_pass |   distinct_record_count_pass |   api_failure_pass |   duplicate_check_pass |   missing_combination_pass |   unexpected_values_pass |   overall_completeness_pass |
|-----------------:|-----------------------------:|-------------------:|-----------------------:|---------------------------:|-------------------------:|----------------------------:|
|                1 |                            1 |                  1 |                      1 |                          1 |                        1 |                           1 |


## Table 2: Overall Completion

|   expected_rows |   actual_rows | row_count_pass   |   expected_distinct_records |   actual_distinct_records | distinct_record_count_pass   |   api_successes |   api_failures | api_failure_pass   |   parse_successes |   parse_failures |   state_1_clean_rows |   state_2_parse_failure_rq5_rows |   state_3_api_failure_rows |   overall_api_success_rate_percent |   overall_parse_rate_percent |   total_retries |   rows_with_retries |
|----------------:|--------------:|:-----------------|----------------------------:|--------------------------:|:-----------------------------|----------------:|---------------:|:-------------------|------------------:|-----------------:|---------------------:|---------------------------------:|---------------------------:|-----------------------------------:|-----------------------------:|----------------:|--------------------:|
|            6000 |          6000 | True             |                        1000 |                      1000 | True                         |            6000 |              0 | True               |              5935 |               65 |                 5935 |                               65 |                          0 |                                100 |                        98.92 |             180 |                 121 |


## Table 3: Provider Summary

| provider   |   expected_rows |   actual_rows | row_count_pass   |   api_successes |   api_failures |   parse_successes |   parse_failures |   state_2_parse_failure_rq5_rows |   parse_rate_percent |
|:-----------|----------------:|--------------:|:-----------------|----------------:|---------------:|------------------:|-----------------:|---------------------------------:|---------------------:|
| openai     |            2000 |          2000 | True             |            2000 |              0 |              2000 |                0 |                                0 |               100    |
| gemini     |            2000 |          2000 | True             |            2000 |              0 |              1995 |                5 |                                5 |                99.75 |
| ollama     |            2000 |          2000 | True             |            2000 |              0 |              1940 |               60 |                               60 |                97    |


## Table 4: Prompt Condition Summary

| condition    |   expected_rows |   actual_rows | row_count_pass   |   api_successes |   api_failures |   parse_successes |   parse_failures |   state_2_parse_failure_rq5_rows |   parse_rate_percent |
|:-------------|----------------:|--------------:|:-----------------|----------------:|---------------:|------------------:|-----------------:|---------------------------------:|---------------------:|
| conventional |            3000 |          3000 | True             |            3000 |              0 |              3000 |                0 |                                0 |               100    |
| structured   |            3000 |          3000 | True             |            3000 |              0 |              2935 |               65 |                               65 |                97.83 |


## Table 5: Provider × Prompt Condition Summary

| provider   | condition    |   expected_rows |   actual_rows | row_count_pass   |   api_successes |   api_failures |   parse_successes |   parse_failures |   state_2_parse_failure_rq5_rows |   parse_rate_percent |
|:-----------|:-------------|----------------:|--------------:|:-----------------|----------------:|---------------:|------------------:|-----------------:|---------------------------------:|---------------------:|
| openai     | conventional |            1000 |          1000 | True             |            1000 |              0 |              1000 |                0 |                                0 |                100   |
| openai     | structured   |            1000 |          1000 | True             |            1000 |              0 |              1000 |                0 |                                0 |                100   |
| gemini     | conventional |            1000 |          1000 | True             |            1000 |              0 |              1000 |                0 |                                0 |                100   |
| gemini     | structured   |            1000 |          1000 | True             |            1000 |              0 |               995 |                5 |                                5 |                 99.5 |
| ollama     | conventional |            1000 |          1000 | True             |            1000 |              0 |              1000 |                0 |                                0 |                100   |
| ollama     | structured   |            1000 |          1000 | True             |            1000 |              0 |               940 |               60 |                               60 |                 94   |


## Table 6: State Summary

| model_name   | prompt_condition   | state                            |   count |
|:-------------|:-------------------|:---------------------------------|--------:|
| gemini       | conventional       | S1_api_success_parse_success     |    1000 |
| gemini       | structured         | S1_api_success_parse_success     |     995 |
| gemini       | structured         | S2_api_success_parse_failure_rq5 |       5 |
| ollama       | conventional       | S1_api_success_parse_success     |    1000 |
| ollama       | structured         | S1_api_success_parse_success     |     940 |
| ollama       | structured         | S2_api_success_parse_failure_rq5 |      60 |
| openai       | conventional       | S1_api_success_parse_success     |    1000 |
| openai       | structured         | S1_api_success_parse_success     |    1000 |


## Table 7: Compliance Category Summary

| provider   | condition    |   total_rows |   strict |   fenced |   embedded |   invalid |   parser_exception |   other_or_missing |
|:-----------|:-------------|-------------:|---------:|---------:|-----------:|----------:|-------------------:|-------------------:|
| openai     | conventional |         1000 |     1000 |        0 |          0 |         0 |                  0 |                  0 |
| openai     | structured   |         1000 |     1000 |        0 |          0 |         0 |                  0 |                  0 |
| gemini     | conventional |         1000 |        0 |     1000 |          0 |         0 |                  0 |                  0 |
| gemini     | structured   |         1000 |        0 |      995 |          0 |         5 |                  0 |                  0 |
| ollama     | conventional |         1000 |     1000 |        0 |          0 |         0 |                  0 |                  0 |
| ollama     | structured   |         1000 |        0 |      887 |         53 |        59 |                  1 |                  0 |


## Table 8: Parse Success × Compliance Category Crosstab

| parse_success_flag   |   embedded |   fenced |   invalid |   parser_exception |   strict |   All |
|:---------------------|-----------:|---------:|----------:|-------------------:|---------:|------:|
| False                |          0 |        0 |        64 |                  1 |        0 |    65 |
| True                 |         53 |     2882 |         0 |                  0 |     3000 |  5935 |
| All                  |         53 |     2882 |        64 |                  1 |     3000 |  6000 |


## Table 9: Vector-Score Consistency Summary

| provider   | condition    |   rows_with_valid_vector_and_score |   consistent |   inconsistent |   consistency_rate_percent |
|:-----------|:-------------|-----------------------------------:|-------------:|---------------:|---------------------------:|
| openai     | conventional |                               1000 |          985 |             15 |                      98.5  |
| openai     | structured   |                               1000 |          968 |             32 |                      96.8  |
| gemini     | conventional |                               1000 |          877 |            123 |                      87.7  |
| gemini     | structured   |                                995 |          854 |            141 |                      85.83 |
| ollama     | conventional |                               1000 |          256 |            744 |                      25.6  |
| ollama     | structured   |                                887 |           63 |            824 |                       7.1  |


## Table 10: Retry Summary

| provider   | condition    |   total_retry_count |   rows_with_retry |   max_retry_count |   total_retry_wait_ms |
|:-----------|:-------------|--------------------:|------------------:|------------------:|----------------------:|
| openai     | conventional |                   0 |                 0 |                 0 |                     0 |
| openai     | structured   |                   0 |                 0 |                 0 |                     0 |
| gemini     | conventional |                  98 |                64 |                 5 |                880000 |
| gemini     | structured   |                  82 |                57 |                 5 |                725000 |
| ollama     | conventional |                   0 |                 0 |                 0 |                     0 |
| ollama     | structured   |                   0 |                 0 |                 0 |                     0 |


## Table 11: Latency Summary

| provider   | condition    |   rows_with_latency |   mean_latency_ms |   median_latency_ms |   min_latency_ms |   max_latency_ms |   std_dev_latency_ms |
|:-----------|:-------------|--------------------:|------------------:|--------------------:|-----------------:|-----------------:|---------------------:|
| openai     | conventional |                1000 |           18276   |             13516   |             3481 |           122877 |             14268    |
| openai     | structured   |                1000 |           20345.4 |             14919   |             3833 |           177875 |             16577.6  |
| gemini     | conventional |                1000 |           25444.7 |             20798.5 |             8835 |           359855 |             17550.3  |
| gemini     | structured   |                1000 |           27700.1 |             23013   |             9732 |           113040 |             15430.8  |
| ollama     | conventional |                1000 |           17011.4 |             16225.5 |            14717 |            53057 |              3482.83 |
| ollama     | structured   |                1000 |           59022.6 |             56943   |            27730 |           122363 |              9442.31 |


## Table 12: Duplicate Summary

|   duplicate_rows_found |   duplicate_key_count | duplicate_check_pass   |
|-----------------------:|----------------------:|:-----------------------|
|                      0 |                     0 | True                   |


## Table 13: Duplicate Inventory

_No rows._


## Table 14: Missing Combination Inventory

_No rows._


## Table 15: Unexpected Values Summary

| unexpected_providers   | unexpected_conditions   | unexpected_compliance_categories   | unexpected_values_pass   |
|:-----------------------|:------------------------|:-----------------------------------|:-------------------------|
|                        |                         |                                    | True                     |


## Table 16: Observed Issue Inventory

|   record_id | model_name   | prompt_condition   | api_success   | parse_success   | state                            | compliance_category   | error_type   | error_message   | raw_response_file                                                                                                       | parsed_output_file                                                                                                          |
|------------:|:-------------|:-------------------|:--------------|:----------------|:---------------------------------|:----------------------|:-------------|:----------------|:------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------|
|         426 | gemini       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0426_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0426_structured_parsed.json |
|         555 | gemini       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0555_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0555_structured_parsed.json |
|         565 | gemini       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0565_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0565_structured_parsed.json |
|         592 | gemini       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0592_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0592_structured_parsed.json |
|         901 | gemini       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0901_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0901_structured_parsed.json |
|          29 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | parser_exception      |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0029_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0029_structured_parsed.json |
|          66 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0066_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0066_structured_parsed.json |
|          72 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0072_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0072_structured_parsed.json |
|          80 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0080_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0080_structured_parsed.json |
|          81 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0081_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0081_structured_parsed.json |
|         109 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0109_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0109_structured_parsed.json |
|         118 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0118_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0118_structured_parsed.json |
|         130 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0130_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0130_structured_parsed.json |
|         147 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0147_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0147_structured_parsed.json |
|         196 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0196_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0196_structured_parsed.json |
|         222 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0222_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0222_structured_parsed.json |
|         233 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0233_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0233_structured_parsed.json |
|         248 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0248_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0248_structured_parsed.json |
|         289 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0289_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0289_structured_parsed.json |
|         293 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0293_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0293_structured_parsed.json |
|         297 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0297_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0297_structured_parsed.json |
|         302 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0302_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0302_structured_parsed.json |
|         305 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0305_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0305_structured_parsed.json |
|         327 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0327_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0327_structured_parsed.json |
|         359 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0359_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0359_structured_parsed.json |
|         365 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0365_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0365_structured_parsed.json |
|         372 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0372_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0372_structured_parsed.json |
|         375 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0375_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0375_structured_parsed.json |
|         377 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0377_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0377_structured_parsed.json |
|         392 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0392_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0392_structured_parsed.json |
|         407 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0407_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0407_structured_parsed.json |
|         418 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0418_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0418_structured_parsed.json |
|         443 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0443_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0443_structured_parsed.json |
|         469 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0469_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0469_structured_parsed.json |
|         490 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0490_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0490_structured_parsed.json |
|         508 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0508_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0508_structured_parsed.json |
|         523 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0523_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0523_structured_parsed.json |
|         529 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0529_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0529_structured_parsed.json |
|         552 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0552_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0552_structured_parsed.json |
|         553 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0553_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0553_structured_parsed.json |
|         569 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0569_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0569_structured_parsed.json |
|         574 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0574_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0574_structured_parsed.json |
|         593 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0593_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0593_structured_parsed.json |
|         601 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0601_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0601_structured_parsed.json |
|         608 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0608_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0608_structured_parsed.json |
|         624 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0624_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0624_structured_parsed.json |
|         658 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0658_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0658_structured_parsed.json |
|         707 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0707_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0707_structured_parsed.json |
|         731 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0731_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0731_structured_parsed.json |
|         736 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0736_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0736_structured_parsed.json |
|         741 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0741_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0741_structured_parsed.json |
|         753 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0753_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0753_structured_parsed.json |
|         757 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0757_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0757_structured_parsed.json |
|         780 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0780_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0780_structured_parsed.json |
|         781 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0781_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0781_structured_parsed.json |
|         793 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0793_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0793_structured_parsed.json |
|         837 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0837_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0837_structured_parsed.json |
|         847 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0847_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0847_structured_parsed.json |
|         882 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0882_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0882_structured_parsed.json |
|         896 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0896_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0896_structured_parsed.json |
|         930 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0930_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0930_structured_parsed.json |
|         931 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0931_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0931_structured_parsed.json |
|         953 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0953_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0953_structured_parsed.json |
|         960 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0960_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0960_structured_parsed.json |
|         984 | ollama       | structured         | True          | False           | S2_api_success_parse_failure_rq5 | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0984_structured_raw.txt | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0984_structured_parsed.json |


## Table 17: Per-Record Issue Summary

|   record_id |   total_inferences |   observed_issue_count |   clean_inferences |
|------------:|-------------------:|-----------------------:|-------------------:|
|          29 |                  6 |                      1 |                  5 |
|          66 |                  6 |                      1 |                  5 |
|          72 |                  6 |                      1 |                  5 |
|          80 |                  6 |                      1 |                  5 |
|          81 |                  6 |                      1 |                  5 |
|         109 |                  6 |                      1 |                  5 |
|         118 |                  6 |                      1 |                  5 |
|         130 |                  6 |                      1 |                  5 |
|         147 |                  6 |                      1 |                  5 |
|         196 |                  6 |                      1 |                  5 |
|         222 |                  6 |                      1 |                  5 |
|         233 |                  6 |                      1 |                  5 |
|         248 |                  6 |                      1 |                  5 |
|         289 |                  6 |                      1 |                  5 |
|         293 |                  6 |                      1 |                  5 |
|         297 |                  6 |                      1 |                  5 |
|         302 |                  6 |                      1 |                  5 |
|         305 |                  6 |                      1 |                  5 |
|         327 |                  6 |                      1 |                  5 |
|         359 |                  6 |                      1 |                  5 |
|         365 |                  6 |                      1 |                  5 |
|         372 |                  6 |                      1 |                  5 |
|         375 |                  6 |                      1 |                  5 |
|         377 |                  6 |                      1 |                  5 |
|         392 |                  6 |                      1 |                  5 |
|         407 |                  6 |                      1 |                  5 |
|         418 |                  6 |                      1 |                  5 |
|         426 |                  6 |                      1 |                  5 |
|         443 |                  6 |                      1 |                  5 |
|         469 |                  6 |                      1 |                  5 |
|         490 |                  6 |                      1 |                  5 |
|         508 |                  6 |                      1 |                  5 |
|         523 |                  6 |                      1 |                  5 |
|         529 |                  6 |                      1 |                  5 |
|         552 |                  6 |                      1 |                  5 |
|         553 |                  6 |                      1 |                  5 |
|         555 |                  6 |                      1 |                  5 |
|         565 |                  6 |                      1 |                  5 |
|         569 |                  6 |                      1 |                  5 |
|         574 |                  6 |                      1 |                  5 |
|         592 |                  6 |                      1 |                  5 |
|         593 |                  6 |                      1 |                  5 |
|         601 |                  6 |                      1 |                  5 |
|         608 |                  6 |                      1 |                  5 |
|         624 |                  6 |                      1 |                  5 |
|         658 |                  6 |                      1 |                  5 |
|         707 |                  6 |                      1 |                  5 |
|         731 |                  6 |                      1 |                  5 |
|         736 |                  6 |                      1 |                  5 |
|         741 |                  6 |                      1 |                  5 |
|         753 |                  6 |                      1 |                  5 |
|         757 |                  6 |                      1 |                  5 |
|         780 |                  6 |                      1 |                  5 |
|         781 |                  6 |                      1 |                  5 |
|         793 |                  6 |                      1 |                  5 |
|         837 |                  6 |                      1 |                  5 |
|         847 |                  6 |                      1 |                  5 |
|         882 |                  6 |                      1 |                  5 |
|         896 |                  6 |                      1 |                  5 |
|         901 |                  6 |                      1 |                  5 |
|         930 |                  6 |                      1 |                  5 |
|         931 |                  6 |                      1 |                  5 |
|         953 |                  6 |                      1 |                  5 |
|         960 |                  6 |                      1 |                  5 |
|         984 |                  6 |                      1 |                  5 |
|           1 |                  6 |                      0 |                  6 |
|           2 |                  6 |                      0 |                  6 |
|           3 |                  6 |                      0 |                  6 |
|           4 |                  6 |                      0 |                  6 |
|           5 |                  6 |                      0 |                  6 |
|           6 |                  6 |                      0 |                  6 |
|           7 |                  6 |                      0 |                  6 |
|           8 |                  6 |                      0 |                  6 |
|           9 |                  6 |                      0 |                  6 |
|          10 |                  6 |                      0 |                  6 |
|          11 |                  6 |                      0 |                  6 |
|          12 |                  6 |                      0 |                  6 |
|          13 |                  6 |                      0 |                  6 |
|          14 |                  6 |                      0 |                  6 |
|          15 |                  6 |                      0 |                  6 |
|          16 |                  6 |                      0 |                  6 |
|          17 |                  6 |                      0 |                  6 |
|          18 |                  6 |                      0 |                  6 |
|          19 |                  6 |                      0 |                  6 |
|          20 |                  6 |                      0 |                  6 |
|          21 |                  6 |                      0 |                  6 |
|          22 |                  6 |                      0 |                  6 |
|          23 |                  6 |                      0 |                  6 |
|          24 |                  6 |                      0 |                  6 |
|          25 |                  6 |                      0 |                  6 |
|          26 |                  6 |                      0 |                  6 |
|          27 |                  6 |                      0 |                  6 |
|          28 |                  6 |                      0 |                  6 |
|          30 |                  6 |                      0 |                  6 |
|          31 |                  6 |                      0 |                  6 |
|          32 |                  6 |                      0 |                  6 |
|          33 |                  6 |                      0 |                  6 |
|          34 |                  6 |                      0 |                  6 |
|          35 |                  6 |                      0 |                  6 |
|          36 |                  6 |                      0 |                  6 |
|          37 |                  6 |                      0 |                  6 |
|          38 |                  6 |                      0 |                  6 |
|          39 |                  6 |                      0 |                  6 |
|          40 |                  6 |                      0 |                  6 |
|          41 |                  6 |                      0 |                  6 |
|          42 |                  6 |                      0 |                  6 |
|          43 |                  6 |                      0 |                  6 |
|          44 |                  6 |                      0 |                  6 |
|          45 |                  6 |                      0 |                  6 |
|          46 |                  6 |                      0 |                  6 |
|          47 |                  6 |                      0 |                  6 |
|          48 |                  6 |                      0 |                  6 |
|          49 |                  6 |                      0 |                  6 |
|          50 |                  6 |                      0 |                  6 |
|          51 |                  6 |                      0 |                  6 |
|          52 |                  6 |                      0 |                  6 |
|          53 |                  6 |                      0 |                  6 |
|          54 |                  6 |                      0 |                  6 |
|          55 |                  6 |                      0 |                  6 |
|          56 |                  6 |                      0 |                  6 |
|          57 |                  6 |                      0 |                  6 |
|          58 |                  6 |                      0 |                  6 |
|          59 |                  6 |                      0 |                  6 |
|          60 |                  6 |                      0 |                  6 |
|          61 |                  6 |                      0 |                  6 |
|          62 |                  6 |                      0 |                  6 |
|          63 |                  6 |                      0 |                  6 |
|          64 |                  6 |                      0 |                  6 |
|          65 |                  6 |                      0 |                  6 |
|          67 |                  6 |                      0 |                  6 |
|          68 |                  6 |                      0 |                  6 |
|          69 |                  6 |                      0 |                  6 |
|          70 |                  6 |                      0 |                  6 |
|          71 |                  6 |                      0 |                  6 |
|          73 |                  6 |                      0 |                  6 |
|          74 |                  6 |                      0 |                  6 |
|          75 |                  6 |                      0 |                  6 |
|          76 |                  6 |                      0 |                  6 |
|          77 |                  6 |                      0 |                  6 |
|          78 |                  6 |                      0 |                  6 |
|          79 |                  6 |                      0 |                  6 |
|          82 |                  6 |                      0 |                  6 |
|          83 |                  6 |                      0 |                  6 |
|          84 |                  6 |                      0 |                  6 |
|          85 |                  6 |                      0 |                  6 |
|          86 |                  6 |                      0 |                  6 |
|          87 |                  6 |                      0 |                  6 |
|          88 |                  6 |                      0 |                  6 |
|          89 |                  6 |                      0 |                  6 |
|          90 |                  6 |                      0 |                  6 |
|          91 |                  6 |                      0 |                  6 |
|          92 |                  6 |                      0 |                  6 |
|          93 |                  6 |                      0 |                  6 |
|          94 |                  6 |                      0 |                  6 |
|          95 |                  6 |                      0 |                  6 |
|          96 |                  6 |                      0 |                  6 |
|          97 |                  6 |                      0 |                  6 |
|          98 |                  6 |                      0 |                  6 |
|          99 |                  6 |                      0 |                  6 |
|         100 |                  6 |                      0 |                  6 |
|         101 |                  6 |                      0 |                  6 |
|         102 |                  6 |                      0 |                  6 |
|         103 |                  6 |                      0 |                  6 |
|         104 |                  6 |                      0 |                  6 |
|         105 |                  6 |                      0 |                  6 |
|         106 |                  6 |                      0 |                  6 |
|         107 |                  6 |                      0 |                  6 |
|         108 |                  6 |                      0 |                  6 |
|         110 |                  6 |                      0 |                  6 |
|         111 |                  6 |                      0 |                  6 |
|         112 |                  6 |                      0 |                  6 |
|         113 |                  6 |                      0 |                  6 |
|         114 |                  6 |                      0 |                  6 |
|         115 |                  6 |                      0 |                  6 |
|         116 |                  6 |                      0 |                  6 |
|         117 |                  6 |                      0 |                  6 |
|         119 |                  6 |                      0 |                  6 |
|         120 |                  6 |                      0 |                  6 |
|         121 |                  6 |                      0 |                  6 |
|         122 |                  6 |                      0 |                  6 |
|         123 |                  6 |                      0 |                  6 |
|         124 |                  6 |                      0 |                  6 |
|         125 |                  6 |                      0 |                  6 |
|         126 |                  6 |                      0 |                  6 |
|         127 |                  6 |                      0 |                  6 |
|         128 |                  6 |                      0 |                  6 |
|         129 |                  6 |                      0 |                  6 |
|         131 |                  6 |                      0 |                  6 |
|         132 |                  6 |                      0 |                  6 |
|         133 |                  6 |                      0 |                  6 |
|         134 |                  6 |                      0 |                  6 |
|         135 |                  6 |                      0 |                  6 |
|         136 |                  6 |                      0 |                  6 |
|         137 |                  6 |                      0 |                  6 |
|         138 |                  6 |                      0 |                  6 |
|         139 |                  6 |                      0 |                  6 |
|         140 |                  6 |                      0 |                  6 |
|         141 |                  6 |                      0 |                  6 |
|         142 |                  6 |                      0 |                  6 |
|         143 |                  6 |                      0 |                  6 |
|         144 |                  6 |                      0 |                  6 |
|         145 |                  6 |                      0 |                  6 |
|         146 |                  6 |                      0 |                  6 |
|         148 |                  6 |                      0 |                  6 |
|         149 |                  6 |                      0 |                  6 |
|         150 |                  6 |                      0 |                  6 |
|         151 |                  6 |                      0 |                  6 |
|         152 |                  6 |                      0 |                  6 |
|         153 |                  6 |                      0 |                  6 |
|         154 |                  6 |                      0 |                  6 |
|         155 |                  6 |                      0 |                  6 |
|         156 |                  6 |                      0 |                  6 |
|         157 |                  6 |                      0 |                  6 |
|         158 |                  6 |                      0 |                  6 |
|         159 |                  6 |                      0 |                  6 |
|         160 |                  6 |                      0 |                  6 |
|         161 |                  6 |                      0 |                  6 |
|         162 |                  6 |                      0 |                  6 |
|         163 |                  6 |                      0 |                  6 |
|         164 |                  6 |                      0 |                  6 |
|         165 |                  6 |                      0 |                  6 |
|         166 |                  6 |                      0 |                  6 |
|         167 |                  6 |                      0 |                  6 |
|         168 |                  6 |                      0 |                  6 |
|         169 |                  6 |                      0 |                  6 |
|         170 |                  6 |                      0 |                  6 |
|         171 |                  6 |                      0 |                  6 |
|         172 |                  6 |                      0 |                  6 |
|         173 |                  6 |                      0 |                  6 |
|         174 |                  6 |                      0 |                  6 |
|         175 |                  6 |                      0 |                  6 |
|         176 |                  6 |                      0 |                  6 |
|         177 |                  6 |                      0 |                  6 |
|         178 |                  6 |                      0 |                  6 |
|         179 |                  6 |                      0 |                  6 |
|         180 |                  6 |                      0 |                  6 |
|         181 |                  6 |                      0 |                  6 |
|         182 |                  6 |                      0 |                  6 |
|         183 |                  6 |                      0 |                  6 |
|         184 |                  6 |                      0 |                  6 |
|         185 |                  6 |                      0 |                  6 |
|         186 |                  6 |                      0 |                  6 |
|         187 |                  6 |                      0 |                  6 |
|         188 |                  6 |                      0 |                  6 |
|         189 |                  6 |                      0 |                  6 |
|         190 |                  6 |                      0 |                  6 |
|         191 |                  6 |                      0 |                  6 |
|         192 |                  6 |                      0 |                  6 |
|         193 |                  6 |                      0 |                  6 |
|         194 |                  6 |                      0 |                  6 |
|         195 |                  6 |                      0 |                  6 |
|         197 |                  6 |                      0 |                  6 |
|         198 |                  6 |                      0 |                  6 |
|         199 |                  6 |                      0 |                  6 |
|         200 |                  6 |                      0 |                  6 |
|         201 |                  6 |                      0 |                  6 |
|         202 |                  6 |                      0 |                  6 |
|         203 |                  6 |                      0 |                  6 |
|         204 |                  6 |                      0 |                  6 |
|         205 |                  6 |                      0 |                  6 |
|         206 |                  6 |                      0 |                  6 |
|         207 |                  6 |                      0 |                  6 |
|         208 |                  6 |                      0 |                  6 |
|         209 |                  6 |                      0 |                  6 |
|         210 |                  6 |                      0 |                  6 |
|         211 |                  6 |                      0 |                  6 |
|         212 |                  6 |                      0 |                  6 |
|         213 |                  6 |                      0 |                  6 |
|         214 |                  6 |                      0 |                  6 |
|         215 |                  6 |                      0 |                  6 |
|         216 |                  6 |                      0 |                  6 |
|         217 |                  6 |                      0 |                  6 |
|         218 |                  6 |                      0 |                  6 |
|         219 |                  6 |                      0 |                  6 |
|         220 |                  6 |                      0 |                  6 |
|         221 |                  6 |                      0 |                  6 |
|         223 |                  6 |                      0 |                  6 |
|         224 |                  6 |                      0 |                  6 |
|         225 |                  6 |                      0 |                  6 |
|         226 |                  6 |                      0 |                  6 |
|         227 |                  6 |                      0 |                  6 |
|         228 |                  6 |                      0 |                  6 |
|         229 |                  6 |                      0 |                  6 |
|         230 |                  6 |                      0 |                  6 |
|         231 |                  6 |                      0 |                  6 |
|         232 |                  6 |                      0 |                  6 |
|         234 |                  6 |                      0 |                  6 |
|         235 |                  6 |                      0 |                  6 |
|         236 |                  6 |                      0 |                  6 |
|         237 |                  6 |                      0 |                  6 |
|         238 |                  6 |                      0 |                  6 |
|         239 |                  6 |                      0 |                  6 |
|         240 |                  6 |                      0 |                  6 |
|         241 |                  6 |                      0 |                  6 |
|         242 |                  6 |                      0 |                  6 |
|         243 |                  6 |                      0 |                  6 |
|         244 |                  6 |                      0 |                  6 |
|         245 |                  6 |                      0 |                  6 |
|         246 |                  6 |                      0 |                  6 |
|         247 |                  6 |                      0 |                  6 |
|         249 |                  6 |                      0 |                  6 |
|         250 |                  6 |                      0 |                  6 |
|         251 |                  6 |                      0 |                  6 |
|         252 |                  6 |                      0 |                  6 |
|         253 |                  6 |                      0 |                  6 |
|         254 |                  6 |                      0 |                  6 |
|         255 |                  6 |                      0 |                  6 |
|         256 |                  6 |                      0 |                  6 |
|         257 |                  6 |                      0 |                  6 |
|         258 |                  6 |                      0 |                  6 |
|         259 |                  6 |                      0 |                  6 |
|         260 |                  6 |                      0 |                  6 |
|         261 |                  6 |                      0 |                  6 |
|         262 |                  6 |                      0 |                  6 |
|         263 |                  6 |                      0 |                  6 |
|         264 |                  6 |                      0 |                  6 |
|         265 |                  6 |                      0 |                  6 |
|         266 |                  6 |                      0 |                  6 |
|         267 |                  6 |                      0 |                  6 |
|         268 |                  6 |                      0 |                  6 |
|         269 |                  6 |                      0 |                  6 |
|         270 |                  6 |                      0 |                  6 |
|         271 |                  6 |                      0 |                  6 |
|         272 |                  6 |                      0 |                  6 |
|         273 |                  6 |                      0 |                  6 |
|         274 |                  6 |                      0 |                  6 |
|         275 |                  6 |                      0 |                  6 |
|         276 |                  6 |                      0 |                  6 |
|         277 |                  6 |                      0 |                  6 |
|         278 |                  6 |                      0 |                  6 |
|         279 |                  6 |                      0 |                  6 |
|         280 |                  6 |                      0 |                  6 |
|         281 |                  6 |                      0 |                  6 |
|         282 |                  6 |                      0 |                  6 |
|         283 |                  6 |                      0 |                  6 |
|         284 |                  6 |                      0 |                  6 |
|         285 |                  6 |                      0 |                  6 |
|         286 |                  6 |                      0 |                  6 |
|         287 |                  6 |                      0 |                  6 |
|         288 |                  6 |                      0 |                  6 |
|         290 |                  6 |                      0 |                  6 |
|         291 |                  6 |                      0 |                  6 |
|         292 |                  6 |                      0 |                  6 |
|         294 |                  6 |                      0 |                  6 |
|         295 |                  6 |                      0 |                  6 |
|         296 |                  6 |                      0 |                  6 |
|         298 |                  6 |                      0 |                  6 |
|         299 |                  6 |                      0 |                  6 |
|         300 |                  6 |                      0 |                  6 |
|         301 |                  6 |                      0 |                  6 |
|         303 |                  6 |                      0 |                  6 |
|         304 |                  6 |                      0 |                  6 |
|         306 |                  6 |                      0 |                  6 |
|         307 |                  6 |                      0 |                  6 |
|         308 |                  6 |                      0 |                  6 |
|         309 |                  6 |                      0 |                  6 |
|         310 |                  6 |                      0 |                  6 |
|         311 |                  6 |                      0 |                  6 |
|         312 |                  6 |                      0 |                  6 |
|         313 |                  6 |                      0 |                  6 |
|         314 |                  6 |                      0 |                  6 |
|         315 |                  6 |                      0 |                  6 |
|         316 |                  6 |                      0 |                  6 |
|         317 |                  6 |                      0 |                  6 |
|         318 |                  6 |                      0 |                  6 |
|         319 |                  6 |                      0 |                  6 |
|         320 |                  6 |                      0 |                  6 |
|         321 |                  6 |                      0 |                  6 |
|         322 |                  6 |                      0 |                  6 |
|         323 |                  6 |                      0 |                  6 |
|         324 |                  6 |                      0 |                  6 |
|         325 |                  6 |                      0 |                  6 |
|         326 |                  6 |                      0 |                  6 |
|         328 |                  6 |                      0 |                  6 |
|         329 |                  6 |                      0 |                  6 |
|         330 |                  6 |                      0 |                  6 |
|         331 |                  6 |                      0 |                  6 |
|         332 |                  6 |                      0 |                  6 |
|         333 |                  6 |                      0 |                  6 |
|         334 |                  6 |                      0 |                  6 |
|         335 |                  6 |                      0 |                  6 |
|         336 |                  6 |                      0 |                  6 |
|         337 |                  6 |                      0 |                  6 |
|         338 |                  6 |                      0 |                  6 |
|         339 |                  6 |                      0 |                  6 |
|         340 |                  6 |                      0 |                  6 |
|         341 |                  6 |                      0 |                  6 |
|         342 |                  6 |                      0 |                  6 |
|         343 |                  6 |                      0 |                  6 |
|         344 |                  6 |                      0 |                  6 |
|         345 |                  6 |                      0 |                  6 |
|         346 |                  6 |                      0 |                  6 |
|         347 |                  6 |                      0 |                  6 |
|         348 |                  6 |                      0 |                  6 |
|         349 |                  6 |                      0 |                  6 |
|         350 |                  6 |                      0 |                  6 |
|         351 |                  6 |                      0 |                  6 |
|         352 |                  6 |                      0 |                  6 |
|         353 |                  6 |                      0 |                  6 |
|         354 |                  6 |                      0 |                  6 |
|         355 |                  6 |                      0 |                  6 |
|         356 |                  6 |                      0 |                  6 |
|         357 |                  6 |                      0 |                  6 |
|         358 |                  6 |                      0 |                  6 |
|         360 |                  6 |                      0 |                  6 |
|         361 |                  6 |                      0 |                  6 |
|         362 |                  6 |                      0 |                  6 |
|         363 |                  6 |                      0 |                  6 |
|         364 |                  6 |                      0 |                  6 |
|         366 |                  6 |                      0 |                  6 |
|         367 |                  6 |                      0 |                  6 |
|         368 |                  6 |                      0 |                  6 |
|         369 |                  6 |                      0 |                  6 |
|         370 |                  6 |                      0 |                  6 |
|         371 |                  6 |                      0 |                  6 |
|         373 |                  6 |                      0 |                  6 |
|         374 |                  6 |                      0 |                  6 |
|         376 |                  6 |                      0 |                  6 |
|         378 |                  6 |                      0 |                  6 |
|         379 |                  6 |                      0 |                  6 |
|         380 |                  6 |                      0 |                  6 |
|         381 |                  6 |                      0 |                  6 |
|         382 |                  6 |                      0 |                  6 |
|         383 |                  6 |                      0 |                  6 |
|         384 |                  6 |                      0 |                  6 |
|         385 |                  6 |                      0 |                  6 |
|         386 |                  6 |                      0 |                  6 |
|         387 |                  6 |                      0 |                  6 |
|         388 |                  6 |                      0 |                  6 |
|         389 |                  6 |                      0 |                  6 |
|         390 |                  6 |                      0 |                  6 |
|         391 |                  6 |                      0 |                  6 |
|         393 |                  6 |                      0 |                  6 |
|         394 |                  6 |                      0 |                  6 |
|         395 |                  6 |                      0 |                  6 |
|         396 |                  6 |                      0 |                  6 |
|         397 |                  6 |                      0 |                  6 |
|         398 |                  6 |                      0 |                  6 |
|         399 |                  6 |                      0 |                  6 |
|         400 |                  6 |                      0 |                  6 |
|         401 |                  6 |                      0 |                  6 |
|         402 |                  6 |                      0 |                  6 |
|         403 |                  6 |                      0 |                  6 |
|         404 |                  6 |                      0 |                  6 |
|         405 |                  6 |                      0 |                  6 |
|         406 |                  6 |                      0 |                  6 |
|         408 |                  6 |                      0 |                  6 |
|         409 |                  6 |                      0 |                  6 |
|         410 |                  6 |                      0 |                  6 |
|         411 |                  6 |                      0 |                  6 |
|         412 |                  6 |                      0 |                  6 |
|         413 |                  6 |                      0 |                  6 |
|         414 |                  6 |                      0 |                  6 |
|         415 |                  6 |                      0 |                  6 |
|         416 |                  6 |                      0 |                  6 |
|         417 |                  6 |                      0 |                  6 |
|         419 |                  6 |                      0 |                  6 |
|         420 |                  6 |                      0 |                  6 |
|         421 |                  6 |                      0 |                  6 |
|         422 |                  6 |                      0 |                  6 |
|         423 |                  6 |                      0 |                  6 |
|         424 |                  6 |                      0 |                  6 |
|         425 |                  6 |                      0 |                  6 |
|         427 |                  6 |                      0 |                  6 |
|         428 |                  6 |                      0 |                  6 |
|         429 |                  6 |                      0 |                  6 |
|         430 |                  6 |                      0 |                  6 |
|         431 |                  6 |                      0 |                  6 |
|         432 |                  6 |                      0 |                  6 |
|         433 |                  6 |                      0 |                  6 |
|         434 |                  6 |                      0 |                  6 |
|         435 |                  6 |                      0 |                  6 |
|         436 |                  6 |                      0 |                  6 |
|         437 |                  6 |                      0 |                  6 |
|         438 |                  6 |                      0 |                  6 |
|         439 |                  6 |                      0 |                  6 |
|         440 |                  6 |                      0 |                  6 |
|         441 |                  6 |                      0 |                  6 |
|         442 |                  6 |                      0 |                  6 |
|         444 |                  6 |                      0 |                  6 |
|         445 |                  6 |                      0 |                  6 |
|         446 |                  6 |                      0 |                  6 |
|         447 |                  6 |                      0 |                  6 |
|         448 |                  6 |                      0 |                  6 |
|         449 |                  6 |                      0 |                  6 |
|         450 |                  6 |                      0 |                  6 |
|         451 |                  6 |                      0 |                  6 |
|         452 |                  6 |                      0 |                  6 |
|         453 |                  6 |                      0 |                  6 |
|         454 |                  6 |                      0 |                  6 |
|         455 |                  6 |                      0 |                  6 |
|         456 |                  6 |                      0 |                  6 |
|         457 |                  6 |                      0 |                  6 |
|         458 |                  6 |                      0 |                  6 |
|         459 |                  6 |                      0 |                  6 |
|         460 |                  6 |                      0 |                  6 |
|         461 |                  6 |                      0 |                  6 |
|         462 |                  6 |                      0 |                  6 |
|         463 |                  6 |                      0 |                  6 |
|         464 |                  6 |                      0 |                  6 |
|         465 |                  6 |                      0 |                  6 |
|         466 |                  6 |                      0 |                  6 |
|         467 |                  6 |                      0 |                  6 |
|         468 |                  6 |                      0 |                  6 |
|         470 |                  6 |                      0 |                  6 |
|         471 |                  6 |                      0 |                  6 |
|         472 |                  6 |                      0 |                  6 |
|         473 |                  6 |                      0 |                  6 |
|         474 |                  6 |                      0 |                  6 |
|         475 |                  6 |                      0 |                  6 |
|         476 |                  6 |                      0 |                  6 |
|         477 |                  6 |                      0 |                  6 |
|         478 |                  6 |                      0 |                  6 |
|         479 |                  6 |                      0 |                  6 |
|         480 |                  6 |                      0 |                  6 |
|         481 |                  6 |                      0 |                  6 |
|         482 |                  6 |                      0 |                  6 |
|         483 |                  6 |                      0 |                  6 |
|         484 |                  6 |                      0 |                  6 |
|         485 |                  6 |                      0 |                  6 |
|         486 |                  6 |                      0 |                  6 |
|         487 |                  6 |                      0 |                  6 |
|         488 |                  6 |                      0 |                  6 |
|         489 |                  6 |                      0 |                  6 |
|         491 |                  6 |                      0 |                  6 |
|         492 |                  6 |                      0 |                  6 |
|         493 |                  6 |                      0 |                  6 |
|         494 |                  6 |                      0 |                  6 |
|         495 |                  6 |                      0 |                  6 |
|         496 |                  6 |                      0 |                  6 |
|         497 |                  6 |                      0 |                  6 |
|         498 |                  6 |                      0 |                  6 |
|         499 |                  6 |                      0 |                  6 |
|         500 |                  6 |                      0 |                  6 |
|         501 |                  6 |                      0 |                  6 |
|         502 |                  6 |                      0 |                  6 |
|         503 |                  6 |                      0 |                  6 |
|         504 |                  6 |                      0 |                  6 |
|         505 |                  6 |                      0 |                  6 |
|         506 |                  6 |                      0 |                  6 |
|         507 |                  6 |                      0 |                  6 |
|         509 |                  6 |                      0 |                  6 |
|         510 |                  6 |                      0 |                  6 |
|         511 |                  6 |                      0 |                  6 |
|         512 |                  6 |                      0 |                  6 |
|         513 |                  6 |                      0 |                  6 |
|         514 |                  6 |                      0 |                  6 |
|         515 |                  6 |                      0 |                  6 |
|         516 |                  6 |                      0 |                  6 |
|         517 |                  6 |                      0 |                  6 |
|         518 |                  6 |                      0 |                  6 |
|         519 |                  6 |                      0 |                  6 |
|         520 |                  6 |                      0 |                  6 |
|         521 |                  6 |                      0 |                  6 |
|         522 |                  6 |                      0 |                  6 |
|         524 |                  6 |                      0 |                  6 |
|         525 |                  6 |                      0 |                  6 |
|         526 |                  6 |                      0 |                  6 |
|         527 |                  6 |                      0 |                  6 |
|         528 |                  6 |                      0 |                  6 |
|         530 |                  6 |                      0 |                  6 |
|         531 |                  6 |                      0 |                  6 |
|         532 |                  6 |                      0 |                  6 |
|         533 |                  6 |                      0 |                  6 |
|         534 |                  6 |                      0 |                  6 |
|         535 |                  6 |                      0 |                  6 |
|         536 |                  6 |                      0 |                  6 |
|         537 |                  6 |                      0 |                  6 |
|         538 |                  6 |                      0 |                  6 |
|         539 |                  6 |                      0 |                  6 |
|         540 |                  6 |                      0 |                  6 |
|         541 |                  6 |                      0 |                  6 |
|         542 |                  6 |                      0 |                  6 |
|         543 |                  6 |                      0 |                  6 |
|         544 |                  6 |                      0 |                  6 |
|         545 |                  6 |                      0 |                  6 |
|         546 |                  6 |                      0 |                  6 |
|         547 |                  6 |                      0 |                  6 |
|         548 |                  6 |                      0 |                  6 |
|         549 |                  6 |                      0 |                  6 |
|         550 |                  6 |                      0 |                  6 |
|         551 |                  6 |                      0 |                  6 |
|         554 |                  6 |                      0 |                  6 |
|         556 |                  6 |                      0 |                  6 |
|         557 |                  6 |                      0 |                  6 |
|         558 |                  6 |                      0 |                  6 |
|         559 |                  6 |                      0 |                  6 |
|         560 |                  6 |                      0 |                  6 |
|         561 |                  6 |                      0 |                  6 |
|         562 |                  6 |                      0 |                  6 |
|         563 |                  6 |                      0 |                  6 |
|         564 |                  6 |                      0 |                  6 |
|         566 |                  6 |                      0 |                  6 |
|         567 |                  6 |                      0 |                  6 |
|         568 |                  6 |                      0 |                  6 |
|         570 |                  6 |                      0 |                  6 |
|         571 |                  6 |                      0 |                  6 |
|         572 |                  6 |                      0 |                  6 |
|         573 |                  6 |                      0 |                  6 |
|         575 |                  6 |                      0 |                  6 |
|         576 |                  6 |                      0 |                  6 |
|         577 |                  6 |                      0 |                  6 |
|         578 |                  6 |                      0 |                  6 |
|         579 |                  6 |                      0 |                  6 |
|         580 |                  6 |                      0 |                  6 |
|         581 |                  6 |                      0 |                  6 |
|         582 |                  6 |                      0 |                  6 |
|         583 |                  6 |                      0 |                  6 |
|         584 |                  6 |                      0 |                  6 |
|         585 |                  6 |                      0 |                  6 |
|         586 |                  6 |                      0 |                  6 |
|         587 |                  6 |                      0 |                  6 |
|         588 |                  6 |                      0 |                  6 |
|         589 |                  6 |                      0 |                  6 |
|         590 |                  6 |                      0 |                  6 |
|         591 |                  6 |                      0 |                  6 |
|         594 |                  6 |                      0 |                  6 |
|         595 |                  6 |                      0 |                  6 |
|         596 |                  6 |                      0 |                  6 |
|         597 |                  6 |                      0 |                  6 |
|         598 |                  6 |                      0 |                  6 |
|         599 |                  6 |                      0 |                  6 |
|         600 |                  6 |                      0 |                  6 |
|         602 |                  6 |                      0 |                  6 |
|         603 |                  6 |                      0 |                  6 |
|         604 |                  6 |                      0 |                  6 |
|         605 |                  6 |                      0 |                  6 |
|         606 |                  6 |                      0 |                  6 |
|         607 |                  6 |                      0 |                  6 |
|         609 |                  6 |                      0 |                  6 |
|         610 |                  6 |                      0 |                  6 |
|         611 |                  6 |                      0 |                  6 |
|         612 |                  6 |                      0 |                  6 |
|         613 |                  6 |                      0 |                  6 |
|         614 |                  6 |                      0 |                  6 |
|         615 |                  6 |                      0 |                  6 |
|         616 |                  6 |                      0 |                  6 |
|         617 |                  6 |                      0 |                  6 |
|         618 |                  6 |                      0 |                  6 |
|         619 |                  6 |                      0 |                  6 |
|         620 |                  6 |                      0 |                  6 |
|         621 |                  6 |                      0 |                  6 |
|         622 |                  6 |                      0 |                  6 |
|         623 |                  6 |                      0 |                  6 |
|         625 |                  6 |                      0 |                  6 |
|         626 |                  6 |                      0 |                  6 |
|         627 |                  6 |                      0 |                  6 |
|         628 |                  6 |                      0 |                  6 |
|         629 |                  6 |                      0 |                  6 |
|         630 |                  6 |                      0 |                  6 |
|         631 |                  6 |                      0 |                  6 |
|         632 |                  6 |                      0 |                  6 |
|         633 |                  6 |                      0 |                  6 |
|         634 |                  6 |                      0 |                  6 |
|         635 |                  6 |                      0 |                  6 |
|         636 |                  6 |                      0 |                  6 |
|         637 |                  6 |                      0 |                  6 |
|         638 |                  6 |                      0 |                  6 |
|         639 |                  6 |                      0 |                  6 |
|         640 |                  6 |                      0 |                  6 |
|         641 |                  6 |                      0 |                  6 |
|         642 |                  6 |                      0 |                  6 |
|         643 |                  6 |                      0 |                  6 |
|         644 |                  6 |                      0 |                  6 |
|         645 |                  6 |                      0 |                  6 |
|         646 |                  6 |                      0 |                  6 |
|         647 |                  6 |                      0 |                  6 |
|         648 |                  6 |                      0 |                  6 |
|         649 |                  6 |                      0 |                  6 |
|         650 |                  6 |                      0 |                  6 |
|         651 |                  6 |                      0 |                  6 |
|         652 |                  6 |                      0 |                  6 |
|         653 |                  6 |                      0 |                  6 |
|         654 |                  6 |                      0 |                  6 |
|         655 |                  6 |                      0 |                  6 |
|         656 |                  6 |                      0 |                  6 |
|         657 |                  6 |                      0 |                  6 |
|         659 |                  6 |                      0 |                  6 |
|         660 |                  6 |                      0 |                  6 |
|         661 |                  6 |                      0 |                  6 |
|         662 |                  6 |                      0 |                  6 |
|         663 |                  6 |                      0 |                  6 |
|         664 |                  6 |                      0 |                  6 |
|         665 |                  6 |                      0 |                  6 |
|         666 |                  6 |                      0 |                  6 |
|         667 |                  6 |                      0 |                  6 |
|         668 |                  6 |                      0 |                  6 |
|         669 |                  6 |                      0 |                  6 |
|         670 |                  6 |                      0 |                  6 |
|         671 |                  6 |                      0 |                  6 |
|         672 |                  6 |                      0 |                  6 |
|         673 |                  6 |                      0 |                  6 |
|         674 |                  6 |                      0 |                  6 |
|         675 |                  6 |                      0 |                  6 |
|         676 |                  6 |                      0 |                  6 |
|         677 |                  6 |                      0 |                  6 |
|         678 |                  6 |                      0 |                  6 |
|         679 |                  6 |                      0 |                  6 |
|         680 |                  6 |                      0 |                  6 |
|         681 |                  6 |                      0 |                  6 |
|         682 |                  6 |                      0 |                  6 |
|         683 |                  6 |                      0 |                  6 |
|         684 |                  6 |                      0 |                  6 |
|         685 |                  6 |                      0 |                  6 |
|         686 |                  6 |                      0 |                  6 |
|         687 |                  6 |                      0 |                  6 |
|         688 |                  6 |                      0 |                  6 |
|         689 |                  6 |                      0 |                  6 |
|         690 |                  6 |                      0 |                  6 |
|         691 |                  6 |                      0 |                  6 |
|         692 |                  6 |                      0 |                  6 |
|         693 |                  6 |                      0 |                  6 |
|         694 |                  6 |                      0 |                  6 |
|         695 |                  6 |                      0 |                  6 |
|         696 |                  6 |                      0 |                  6 |
|         697 |                  6 |                      0 |                  6 |
|         698 |                  6 |                      0 |                  6 |
|         699 |                  6 |                      0 |                  6 |
|         700 |                  6 |                      0 |                  6 |
|         701 |                  6 |                      0 |                  6 |
|         702 |                  6 |                      0 |                  6 |
|         703 |                  6 |                      0 |                  6 |
|         704 |                  6 |                      0 |                  6 |
|         705 |                  6 |                      0 |                  6 |
|         706 |                  6 |                      0 |                  6 |
|         708 |                  6 |                      0 |                  6 |
|         709 |                  6 |                      0 |                  6 |
|         710 |                  6 |                      0 |                  6 |
|         711 |                  6 |                      0 |                  6 |
|         712 |                  6 |                      0 |                  6 |
|         713 |                  6 |                      0 |                  6 |
|         714 |                  6 |                      0 |                  6 |
|         715 |                  6 |                      0 |                  6 |
|         716 |                  6 |                      0 |                  6 |
|         717 |                  6 |                      0 |                  6 |
|         718 |                  6 |                      0 |                  6 |
|         719 |                  6 |                      0 |                  6 |
|         720 |                  6 |                      0 |                  6 |
|         721 |                  6 |                      0 |                  6 |
|         722 |                  6 |                      0 |                  6 |
|         723 |                  6 |                      0 |                  6 |
|         724 |                  6 |                      0 |                  6 |
|         725 |                  6 |                      0 |                  6 |
|         726 |                  6 |                      0 |                  6 |
|         727 |                  6 |                      0 |                  6 |
|         728 |                  6 |                      0 |                  6 |
|         729 |                  6 |                      0 |                  6 |
|         730 |                  6 |                      0 |                  6 |
|         732 |                  6 |                      0 |                  6 |
|         733 |                  6 |                      0 |                  6 |
|         734 |                  6 |                      0 |                  6 |
|         735 |                  6 |                      0 |                  6 |
|         737 |                  6 |                      0 |                  6 |
|         738 |                  6 |                      0 |                  6 |
|         739 |                  6 |                      0 |                  6 |
|         740 |                  6 |                      0 |                  6 |
|         742 |                  6 |                      0 |                  6 |
|         743 |                  6 |                      0 |                  6 |
|         744 |                  6 |                      0 |                  6 |
|         745 |                  6 |                      0 |                  6 |
|         746 |                  6 |                      0 |                  6 |
|         747 |                  6 |                      0 |                  6 |
|         748 |                  6 |                      0 |                  6 |
|         749 |                  6 |                      0 |                  6 |
|         750 |                  6 |                      0 |                  6 |
|         751 |                  6 |                      0 |                  6 |
|         752 |                  6 |                      0 |                  6 |
|         754 |                  6 |                      0 |                  6 |
|         755 |                  6 |                      0 |                  6 |
|         756 |                  6 |                      0 |                  6 |
|         758 |                  6 |                      0 |                  6 |
|         759 |                  6 |                      0 |                  6 |
|         760 |                  6 |                      0 |                  6 |
|         761 |                  6 |                      0 |                  6 |
|         762 |                  6 |                      0 |                  6 |
|         763 |                  6 |                      0 |                  6 |
|         764 |                  6 |                      0 |                  6 |
|         765 |                  6 |                      0 |                  6 |
|         766 |                  6 |                      0 |                  6 |
|         767 |                  6 |                      0 |                  6 |
|         768 |                  6 |                      0 |                  6 |
|         769 |                  6 |                      0 |                  6 |
|         770 |                  6 |                      0 |                  6 |
|         771 |                  6 |                      0 |                  6 |
|         772 |                  6 |                      0 |                  6 |
|         773 |                  6 |                      0 |                  6 |
|         774 |                  6 |                      0 |                  6 |
|         775 |                  6 |                      0 |                  6 |
|         776 |                  6 |                      0 |                  6 |
|         777 |                  6 |                      0 |                  6 |
|         778 |                  6 |                      0 |                  6 |
|         779 |                  6 |                      0 |                  6 |
|         782 |                  6 |                      0 |                  6 |
|         783 |                  6 |                      0 |                  6 |
|         784 |                  6 |                      0 |                  6 |
|         785 |                  6 |                      0 |                  6 |
|         786 |                  6 |                      0 |                  6 |
|         787 |                  6 |                      0 |                  6 |
|         788 |                  6 |                      0 |                  6 |
|         789 |                  6 |                      0 |                  6 |
|         790 |                  6 |                      0 |                  6 |
|         791 |                  6 |                      0 |                  6 |
|         792 |                  6 |                      0 |                  6 |
|         794 |                  6 |                      0 |                  6 |
|         795 |                  6 |                      0 |                  6 |
|         796 |                  6 |                      0 |                  6 |
|         797 |                  6 |                      0 |                  6 |
|         798 |                  6 |                      0 |                  6 |
|         799 |                  6 |                      0 |                  6 |
|         800 |                  6 |                      0 |                  6 |
|         801 |                  6 |                      0 |                  6 |
|         802 |                  6 |                      0 |                  6 |
|         803 |                  6 |                      0 |                  6 |
|         804 |                  6 |                      0 |                  6 |
|         805 |                  6 |                      0 |                  6 |
|         806 |                  6 |                      0 |                  6 |
|         807 |                  6 |                      0 |                  6 |
|         808 |                  6 |                      0 |                  6 |
|         809 |                  6 |                      0 |                  6 |
|         810 |                  6 |                      0 |                  6 |
|         811 |                  6 |                      0 |                  6 |
|         812 |                  6 |                      0 |                  6 |
|         813 |                  6 |                      0 |                  6 |
|         814 |                  6 |                      0 |                  6 |
|         815 |                  6 |                      0 |                  6 |
|         816 |                  6 |                      0 |                  6 |
|         817 |                  6 |                      0 |                  6 |
|         818 |                  6 |                      0 |                  6 |
|         819 |                  6 |                      0 |                  6 |
|         820 |                  6 |                      0 |                  6 |
|         821 |                  6 |                      0 |                  6 |
|         822 |                  6 |                      0 |                  6 |
|         823 |                  6 |                      0 |                  6 |
|         824 |                  6 |                      0 |                  6 |
|         825 |                  6 |                      0 |                  6 |
|         826 |                  6 |                      0 |                  6 |
|         827 |                  6 |                      0 |                  6 |
|         828 |                  6 |                      0 |                  6 |
|         829 |                  6 |                      0 |                  6 |
|         830 |                  6 |                      0 |                  6 |
|         831 |                  6 |                      0 |                  6 |
|         832 |                  6 |                      0 |                  6 |
|         833 |                  6 |                      0 |                  6 |
|         834 |                  6 |                      0 |                  6 |
|         835 |                  6 |                      0 |                  6 |
|         836 |                  6 |                      0 |                  6 |
|         838 |                  6 |                      0 |                  6 |
|         839 |                  6 |                      0 |                  6 |
|         840 |                  6 |                      0 |                  6 |
|         841 |                  6 |                      0 |                  6 |
|         842 |                  6 |                      0 |                  6 |
|         843 |                  6 |                      0 |                  6 |
|         844 |                  6 |                      0 |                  6 |
|         845 |                  6 |                      0 |                  6 |
|         846 |                  6 |                      0 |                  6 |
|         848 |                  6 |                      0 |                  6 |
|         849 |                  6 |                      0 |                  6 |
|         850 |                  6 |                      0 |                  6 |
|         851 |                  6 |                      0 |                  6 |
|         852 |                  6 |                      0 |                  6 |
|         853 |                  6 |                      0 |                  6 |
|         854 |                  6 |                      0 |                  6 |
|         855 |                  6 |                      0 |                  6 |
|         856 |                  6 |                      0 |                  6 |
|         857 |                  6 |                      0 |                  6 |
|         858 |                  6 |                      0 |                  6 |
|         859 |                  6 |                      0 |                  6 |
|         860 |                  6 |                      0 |                  6 |
|         861 |                  6 |                      0 |                  6 |
|         862 |                  6 |                      0 |                  6 |
|         863 |                  6 |                      0 |                  6 |
|         864 |                  6 |                      0 |                  6 |
|         865 |                  6 |                      0 |                  6 |
|         866 |                  6 |                      0 |                  6 |
|         867 |                  6 |                      0 |                  6 |
|         868 |                  6 |                      0 |                  6 |
|         869 |                  6 |                      0 |                  6 |
|         870 |                  6 |                      0 |                  6 |
|         871 |                  6 |                      0 |                  6 |
|         872 |                  6 |                      0 |                  6 |
|         873 |                  6 |                      0 |                  6 |
|         874 |                  6 |                      0 |                  6 |
|         875 |                  6 |                      0 |                  6 |
|         876 |                  6 |                      0 |                  6 |
|         877 |                  6 |                      0 |                  6 |
|         878 |                  6 |                      0 |                  6 |
|         879 |                  6 |                      0 |                  6 |
|         880 |                  6 |                      0 |                  6 |
|         881 |                  6 |                      0 |                  6 |
|         883 |                  6 |                      0 |                  6 |
|         884 |                  6 |                      0 |                  6 |
|         885 |                  6 |                      0 |                  6 |
|         886 |                  6 |                      0 |                  6 |
|         887 |                  6 |                      0 |                  6 |
|         888 |                  6 |                      0 |                  6 |
|         889 |                  6 |                      0 |                  6 |
|         890 |                  6 |                      0 |                  6 |
|         891 |                  6 |                      0 |                  6 |
|         892 |                  6 |                      0 |                  6 |
|         893 |                  6 |                      0 |                  6 |
|         894 |                  6 |                      0 |                  6 |
|         895 |                  6 |                      0 |                  6 |
|         897 |                  6 |                      0 |                  6 |
|         898 |                  6 |                      0 |                  6 |
|         899 |                  6 |                      0 |                  6 |
|         900 |                  6 |                      0 |                  6 |
|         902 |                  6 |                      0 |                  6 |
|         903 |                  6 |                      0 |                  6 |
|         904 |                  6 |                      0 |                  6 |
|         905 |                  6 |                      0 |                  6 |
|         906 |                  6 |                      0 |                  6 |
|         907 |                  6 |                      0 |                  6 |
|         908 |                  6 |                      0 |                  6 |
|         909 |                  6 |                      0 |                  6 |
|         910 |                  6 |                      0 |                  6 |
|         911 |                  6 |                      0 |                  6 |
|         912 |                  6 |                      0 |                  6 |
|         913 |                  6 |                      0 |                  6 |
|         914 |                  6 |                      0 |                  6 |
|         915 |                  6 |                      0 |                  6 |
|         916 |                  6 |                      0 |                  6 |
|         917 |                  6 |                      0 |                  6 |
|         918 |                  6 |                      0 |                  6 |
|         919 |                  6 |                      0 |                  6 |
|         920 |                  6 |                      0 |                  6 |
|         921 |                  6 |                      0 |                  6 |
|         922 |                  6 |                      0 |                  6 |
|         923 |                  6 |                      0 |                  6 |
|         924 |                  6 |                      0 |                  6 |
|         925 |                  6 |                      0 |                  6 |
|         926 |                  6 |                      0 |                  6 |
|         927 |                  6 |                      0 |                  6 |
|         928 |                  6 |                      0 |                  6 |
|         929 |                  6 |                      0 |                  6 |
|         932 |                  6 |                      0 |                  6 |
|         933 |                  6 |                      0 |                  6 |
|         934 |                  6 |                      0 |                  6 |
|         935 |                  6 |                      0 |                  6 |
|         936 |                  6 |                      0 |                  6 |
|         937 |                  6 |                      0 |                  6 |
|         938 |                  6 |                      0 |                  6 |
|         939 |                  6 |                      0 |                  6 |
|         940 |                  6 |                      0 |                  6 |
|         941 |                  6 |                      0 |                  6 |
|         942 |                  6 |                      0 |                  6 |
|         943 |                  6 |                      0 |                  6 |
|         944 |                  6 |                      0 |                  6 |
|         945 |                  6 |                      0 |                  6 |
|         946 |                  6 |                      0 |                  6 |
|         947 |                  6 |                      0 |                  6 |
|         948 |                  6 |                      0 |                  6 |
|         949 |                  6 |                      0 |                  6 |
|         950 |                  6 |                      0 |                  6 |
|         951 |                  6 |                      0 |                  6 |
|         952 |                  6 |                      0 |                  6 |
|         954 |                  6 |                      0 |                  6 |
|         955 |                  6 |                      0 |                  6 |
|         956 |                  6 |                      0 |                  6 |
|         957 |                  6 |                      0 |                  6 |
|         958 |                  6 |                      0 |                  6 |
|         959 |                  6 |                      0 |                  6 |
|         961 |                  6 |                      0 |                  6 |
|         962 |                  6 |                      0 |                  6 |
|         963 |                  6 |                      0 |                  6 |
|         964 |                  6 |                      0 |                  6 |
|         965 |                  6 |                      0 |                  6 |
|         966 |                  6 |                      0 |                  6 |
|         967 |                  6 |                      0 |                  6 |
|         968 |                  6 |                      0 |                  6 |
|         969 |                  6 |                      0 |                  6 |
|         970 |                  6 |                      0 |                  6 |
|         971 |                  6 |                      0 |                  6 |
|         972 |                  6 |                      0 |                  6 |
|         973 |                  6 |                      0 |                  6 |
|         974 |                  6 |                      0 |                  6 |
|         975 |                  6 |                      0 |                  6 |
|         976 |                  6 |                      0 |                  6 |
|         977 |                  6 |                      0 |                  6 |
|         978 |                  6 |                      0 |                  6 |
|         979 |                  6 |                      0 |                  6 |
|         980 |                  6 |                      0 |                  6 |
|         981 |                  6 |                      0 |                  6 |
|         982 |                  6 |                      0 |                  6 |
|         983 |                  6 |                      0 |                  6 |
|         985 |                  6 |                      0 |                  6 |
|         986 |                  6 |                      0 |                  6 |
|         987 |                  6 |                      0 |                  6 |
|         988 |                  6 |                      0 |                  6 |
|         989 |                  6 |                      0 |                  6 |
|         990 |                  6 |                      0 |                  6 |
|         991 |                  6 |                      0 |                  6 |
|         992 |                  6 |                      0 |                  6 |
|         993 |                  6 |                      0 |                  6 |
|         994 |                  6 |                      0 |                  6 |
|         995 |                  6 |                      0 |                  6 |
|         996 |                  6 |                      0 |                  6 |
|         997 |                  6 |                      0 |                  6 |
|         998 |                  6 |                      0 |                  6 |
|         999 |                  6 |                      0 |                  6 |
|        1000 |                  6 |                      0 |                  6 |


## Methodological Notes

- The Parquet export is used as the authoritative input because it preserves the combined results without Excel truncation issues.
- State 1 means API success and parse success.
- State 2 means API success but parse failure. These rows are retained as observed evidence for failure-mode analysis.
- State 3 means API failure. No State 3 rows are expected in the final main experiment output.
- The parse/compliance crosstab is included to check whether parser flags and compliance categories are coherent.
- Accuracy against official CVSS values is assessed separately in the main accuracy analysis.
