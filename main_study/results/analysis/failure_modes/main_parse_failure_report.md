# Main Parse Failure Extraction Report

## Purpose

This report extracts State 2 rows from the main experiment. State 2 means that the model API call succeeded, but the response did not parse successfully. These rows are retained as observed evidence for failure-mode analysis and prompt-sensitivity interpretation.

## Summary

The combined result file contains 65 State 2 parse-failure rows. This script expected 65 rows based on the completeness analysis. Expectation match: True.

## Table 1: Provider Summary

| model_name   |   state2_parse_failures |
|:-------------|------------------------:|
| gemini       |                       5 |
| ollama       |                      60 |


## Table 2: Prompt Condition Summary

| prompt_condition   |   state2_parse_failures |
|:-------------------|------------------------:|
| structured         |                      65 |


## Table 3: Provider × Prompt Condition Summary

| model_name   | prompt_condition   |   state2_parse_failures |
|:-------------|:-------------------|------------------------:|
| gemini       | structured         |                       5 |
| ollama       | structured         |                      60 |


## Table 4: Compliance Category Summary

| compliance_category   |   state2_parse_failures |
|:----------------------|------------------------:|
| invalid               |                      64 |
| parser_exception      |                       1 |


## Table 5: Error Message Summary

| model_name   | prompt_condition   | compliance_category   | error_type_clean   | error_message_clean   |   count |
|:-------------|:-------------------|:----------------------|:-------------------|:----------------------|--------:|
| ollama       | structured         | invalid               | no_error_type      | no_error_message      |      59 |
| gemini       | structured         | invalid               | no_error_type      | no_error_message      |       5 |
| ollama       | structured         | parser_exception      | no_error_type      | no_error_message      |       1 |


## Table 6: Failure Group Summary

| failure_group                                          |   count |
|:-------------------------------------------------------|--------:|
| ollama | structured | invalid | no_error_type          |      59 |
| gemini | structured | invalid | no_error_type          |       5 |
| ollama | structured | parser_exception | no_error_type |       1 |


## Table 7: Representative Raw Response Samples Copied

| failure_group                                          |   record_id | model_name   | prompt_condition   | compliance_category   | error_type   | error_message   | raw_response_file                                                                                                       | copied_sample_file                                                                                                                                 | copy_status   |
|:-------------------------------------------------------|------------:|:-------------|:-------------------|:----------------------|:-------------|:----------------|:------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|:--------------|
| gemini | structured | invalid | no_error_type          |         426 | gemini       | structured         | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0426_structured_raw.txt | main_study\results\analysis\failure_modes\raw_response_samples\record_426_gemini_structured_gemini__structured__invalid__no_error_type.txt         | copied        |
| gemini | structured | invalid | no_error_type          |         555 | gemini       | structured         | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0555_structured_raw.txt | main_study\results\analysis\failure_modes\raw_response_samples\record_555_gemini_structured_gemini__structured__invalid__no_error_type.txt         | copied        |
| gemini | structured | invalid | no_error_type          |         565 | gemini       | structured         | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\gemini\structured\run_001\R0565_structured_raw.txt | main_study\results\analysis\failure_modes\raw_response_samples\record_565_gemini_structured_gemini__structured__invalid__no_error_type.txt         | copied        |
| ollama | structured | invalid | no_error_type          |          66 | ollama       | structured         | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0066_structured_raw.txt | main_study\results\analysis\failure_modes\raw_response_samples\record_66_ollama_structured_ollama__structured__invalid__no_error_type.txt          | copied        |
| ollama | structured | invalid | no_error_type          |          72 | ollama       | structured         | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0072_structured_raw.txt | main_study\results\analysis\failure_modes\raw_response_samples\record_72_ollama_structured_ollama__structured__invalid__no_error_type.txt          | copied        |
| ollama | structured | invalid | no_error_type          |          80 | ollama       | structured         | invalid               |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0080_structured_raw.txt | main_study\results\analysis\failure_modes\raw_response_samples\record_80_ollama_structured_ollama__structured__invalid__no_error_type.txt          | copied        |
| ollama | structured | parser_exception | no_error_type |          29 | ollama       | structured         | parser_exception      |              |                 | C:\Users\uwach\MSc_LLM_CVSS_Project\main_study\results\raw_responses\ollama\structured\run_001\R0029_structured_raw.txt | main_study\results\analysis\failure_modes\raw_response_samples\record_29_ollama_structured_ollama__structured__parser_exception__no_error_type.txt | copied        |


## Methodological Notes

- This script does not modify or repair any model output.
- The extracted failures remain part of the observed experimental results.
- Representative raw responses are copied only for inspection; the original raw response files remain the source files.
- The next manual step is to inspect representative raw responses and classify whether failures appear to be model output near-misses, hard invalid outputs, parser exceptions, or potential parser-asymmetry artefacts.
