# Pilot Completeness Report

## Purpose

This report summarises the completeness and internal reliability of the 50-record pilot run. It does not compare model outputs against ground-truth CVSS values or EPSS scores.

## Summary

The pilot expected 300.0 inference rows and produced 300.0 rows. There were 297.0 successful parses and 3.0 parse failure(s), giving an overall parse rate of 99.0%. No ground-truth accuracy claims are made in this report.

## Table 1: Overall Pilot Completion

|   expected_rows |   actual_rows |   missing_rows |   parse_successes |   parse_failures |   overall_parse_rate_percent |   total_retries |   rows_with_retries |
|----------------:|--------------:|---------------:|------------------:|-----------------:|-----------------------------:|----------------:|--------------------:|
|             300 |           300 |              0 |               297 |                3 |                           99 |               0 |                   0 |


## Table 2: Provider × Condition Parse Summary

| provider   | condition    |   total_rows |   parsed |   failed |   failed_invalid |   failed_other |   parse_rate_percent |
|:-----------|:-------------|-------------:|---------:|---------:|-----------------:|---------------:|---------------------:|
| ollama     | conventional |           50 |       50 |        0 |                0 |              0 |                  100 |
| ollama     | structured   |           50 |       48 |        2 |                2 |              0 |                   96 |
| openai     | conventional |           50 |       50 |        0 |                0 |              0 |                  100 |
| openai     | structured   |           50 |       50 |        0 |                0 |              0 |                  100 |
| gemini     | conventional |           50 |       50 |        0 |                0 |              0 |                  100 |
| gemini     | structured   |           50 |       49 |        1 |                1 |              0 |                   98 |


## Table 3: Compliance Category Summary

| provider   | condition    |   strict |   fenced |   embedded |   invalid |   other |
|:-----------|:-------------|---------:|---------:|-----------:|----------:|--------:|
| ollama     | conventional |       50 |        0 |          0 |         0 |       0 |
| ollama     | structured   |        0 |       48 |          0 |         2 |       0 |
| openai     | conventional |       50 |        0 |          0 |         0 |       0 |
| openai     | structured   |       50 |        0 |          0 |         0 |       0 |
| gemini     | conventional |        0 |       50 |          0 |         0 |       0 |
| gemini     | structured   |        0 |       49 |          0 |         1 |       0 |


## Table 4: Vector-Score Consistency Summary

Vector-score consistency was assessed only where both a predicted vector and predicted base score were available. The tolerance used was ±0.15.

| provider   | condition    |   rows_with_valid_vector_and_score |   consistent |   inconsistent |   consistency_rate_percent |   tolerance_used |
|:-----------|:-------------|-----------------------------------:|-------------:|---------------:|---------------------------:|-----------------:|
| ollama     | conventional |                                 50 |            7 |             43 |                      14    |             0.15 |
| ollama     | structured   |                                 48 |            2 |             46 |                       4.17 |             0.15 |
| openai     | conventional |                                 50 |           49 |              1 |                      98    |             0.15 |
| openai     | structured   |                                 50 |           49 |              1 |                      98    |             0.15 |
| gemini     | conventional |                                 50 |           42 |              8 |                      84    |             0.15 |
| gemini     | structured   |                                 49 |           43 |              6 |                      87.76 |             0.15 |


## Table 5: Retry Summary

| provider   | condition    |   total_retry_count |   rows_with_retry |   max_retry_count |   total_retry_wait_ms |
|:-----------|:-------------|--------------------:|------------------:|------------------:|----------------------:|
| ollama     | conventional |                   0 |                 0 |                 0 |                     0 |
| ollama     | structured   |                   0 |                 0 |                 0 |                     0 |
| openai     | conventional |                   0 |                 0 |                 0 |                     0 |
| openai     | structured   |                   0 |                 0 |                 0 |                     0 |
| gemini     | conventional |                   0 |                 0 |                 0 |                     0 |
| gemini     | structured   |                   0 |                 0 |                 0 |                     0 |


## Table 6: Latency Summary

| provider   | condition    |   mean_latency_ms |   median_latency_ms |   min_latency_ms |   max_latency_ms |   std_dev_latency_ms |
|:-----------|:-------------|------------------:|--------------------:|-----------------:|-----------------:|---------------------:|
| ollama     | conventional |           16446.9 |             14972.5 |            13778 |            36495 |               4700.8 |
| ollama     | structured   |           54592.1 |             51118   |            34917 |           102206 |              11795.2 |
| openai     | conventional |           20784.3 |             16153   |             6582 |            57740 |              12535.7 |
| openai     | structured   |           20317.5 |             16522   |             5665 |            68916 |              13459.9 |
| gemini     | conventional |           26117.7 |             23239   |            10334 |            81209 |              12283   |
| gemini     | structured   |           25108.6 |             22323.5 |            12845 |            61922 |              10454.9 |


## Table 7: Failure Inventory

|   record_id | model_name   | prompt_condition   | parse_success   | compliance_category   |   error_type |   error_message | raw_response_file                                                             | parsed_output_file                                                                |
|------------:|:-------------|:-------------------|:----------------|:----------------------|-------------:|----------------:|:------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|
|           6 | ollama       | structured         | False           | invalid               |          nan |             nan | results\pilot\raw_responses\ollama\structured\run_001\R006_structured_raw.txt | results\pilot\raw_responses\ollama\structured\run_001\R006_structured_parsed.json |
|          22 | ollama       | structured         | False           | invalid               |          nan |             nan | results\pilot\raw_responses\ollama\structured\run_001\R022_structured_raw.txt | results\pilot\raw_responses\ollama\structured\run_001\R022_structured_parsed.json |
|          49 | gemini       | structured         | False           | invalid               |          nan |             nan | results\pilot\raw_responses\gemini\structured\run_001\R049_structured_raw.txt | results\pilot\raw_responses\gemini\structured\run_001\R049_structured_parsed.json |


## Table 8: Per-Record Failure Summary

|   record_id |   total_inferences |   failed_inferences |   successful_inferences |
|------------:|-------------------:|--------------------:|------------------------:|
|           6 |                  6 |                   1 |                       5 |
|          22 |                  6 |                   1 |                       5 |
|          49 |                  6 |                   1 |                       5 |
|           1 |                  6 |                   0 |                       6 |
|           2 |                  6 |                   0 |                       6 |
|           3 |                  6 |                   0 |                       6 |
|           4 |                  6 |                   0 |                       6 |
|           5 |                  6 |                   0 |                       6 |
|           7 |                  6 |                   0 |                       6 |
|           8 |                  6 |                   0 |                       6 |
|           9 |                  6 |                   0 |                       6 |
|          10 |                  6 |                   0 |                       6 |
|          11 |                  6 |                   0 |                       6 |
|          12 |                  6 |                   0 |                       6 |
|          13 |                  6 |                   0 |                       6 |
|          14 |                  6 |                   0 |                       6 |
|          15 |                  6 |                   0 |                       6 |
|          16 |                  6 |                   0 |                       6 |
|          17 |                  6 |                   0 |                       6 |
|          18 |                  6 |                   0 |                       6 |
|          19 |                  6 |                   0 |                       6 |
|          20 |                  6 |                   0 |                       6 |
|          21 |                  6 |                   0 |                       6 |
|          23 |                  6 |                   0 |                       6 |
|          24 |                  6 |                   0 |                       6 |
|          25 |                  6 |                   0 |                       6 |
|          26 |                  6 |                   0 |                       6 |
|          27 |                  6 |                   0 |                       6 |
|          28 |                  6 |                   0 |                       6 |
|          29 |                  6 |                   0 |                       6 |
|          30 |                  6 |                   0 |                       6 |
|          31 |                  6 |                   0 |                       6 |
|          32 |                  6 |                   0 |                       6 |
|          33 |                  6 |                   0 |                       6 |
|          34 |                  6 |                   0 |                       6 |
|          35 |                  6 |                   0 |                       6 |
|          36 |                  6 |                   0 |                       6 |
|          37 |                  6 |                   0 |                       6 |
|          38 |                  6 |                   0 |                       6 |
|          39 |                  6 |                   0 |                       6 |
|          40 |                  6 |                   0 |                       6 |
|          41 |                  6 |                   0 |                       6 |
|          42 |                  6 |                   0 |                       6 |
|          43 |                  6 |                   0 |                       6 |
|          44 |                  6 |                   0 |                       6 |
|          45 |                  6 |                   0 |                       6 |
|          46 |                  6 |                   0 |                       6 |
|          47 |                  6 |                   0 |                       6 |
|          48 |                  6 |                   0 |                       6 |
|          50 |                  6 |                   0 |                       6 |


## Methodological Notes

- This report evaluates pilot completeness, parseability, compliance category, retry behaviour, latency, and internal vector-score consistency.
- It does not evaluate correctness against official CVSS vectors or EPSS values.
- Compliance categories are expected to be: strict, fenced, embedded, and invalid.
- Failed or invalid rows are retained as observed data and are not re-run or manually repaired.


## Research Question Mapping

These completeness metrics primarily support RQ4 and RQ5 by documenting reliability, stability, output-format compliance, and observed failure modes under different prompting strategies.
