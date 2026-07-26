# Main Study Pipeline Inventory v1

## Project

MSc LLM-CVSS Project

## Date

2026-06-21

---

# Purpose

This document records the Main Study pipeline, scripts, datasets, audit files, and current project status.

It is intended to support traceability, reproducibility, and clear explanation of the dissertation workflow.

---

# Phase 1 — Protocol and Structure

## Purpose

Defined the Main Study workflow, dataset rules, sampling logic, and folder structure.

## Key Documents

* `main_study/docs/main_dataset_generation_protocol_v1.md`
* `main_study/docs/main_dataset_specification_v1.md`
* `main_study/docs/fetch_main_dataset_design_v1.md`

---

# Phase 2 — Candidate Pool Construction

## Script

* `main_study/scripts/fetch_main_dataset.py`

## Purpose

Fetched CVE records from NVD, extracted CVSS v3.1 fields, CPE metadata, severity, publication year, and candidate-pool fields.

## Outputs

* `main_study/datasets/raw/main_candidate_pool_raw.parquet`
* `main_study/datasets/raw/main_candidate_pool_raw.csv`
* `main_study/datasets/raw/nvd_json_pages/`

## Audit

* `main_study/audit/main_cvss_source_distribution.xlsx`
* `main_study/audit/main_fallback_cvss_details.xlsx`
* `main_study/audit/main_excel_truncation_inspection.xlsx`

## Notebook

* `main_study/notebooks/candidate_pool_observations_v1.md`

---

# Phase 3 — EPSS Enrichment

## Scripts

* `main_study/scripts/enrich_main_with_epss.py`
* `main_study/scripts/verify_main_epss_enrichment.py`
* `main_study/scripts/inspect_main_epss_metadata.py`

## Outputs

* `main_study/datasets/processed/main_candidate_pool_with_epss.parquet`
* `main_study/datasets/processed/main_candidate_pool_with_epss.csv`

## Frozen EPSS Snapshot

* `main_study/datasets/frozen/epss/epss_scores_v2026.06.15_2026-06-19.csv.gz`

## Audit

* `main_study/audit/main_epss_enrichment_log.txt`
* `main_study/audit/main_epss_coverage_summary.xlsx`
* `main_study/audit/main_epss_snapshot_metadata.txt`

## Notebook

* `main_study/notebooks/epss_enrichment_observations_v1.md`

---

# Phase 4 — Sampling

## Scripts

* `main_study/scripts/sample_main_dataset.py`
* `main_study/scripts/inspect_pilot_cvss_source_distribution.py`
* `main_study/scripts/verify_main_frozen_cpe_lengths.py`

## Final Sample

* Total: 1,000 CVEs
* Critical: 250
* High: 250
* Medium: 250
* Low: 250

## Outputs

* `main_study/datasets/frozen/main_dataset_frozen_v1.parquet`
* `main_study/datasets/frozen/main_dataset_frozen_v1.csv`
* `main_study/datasets/frozen/main_dataset_frozen_v1.xlsx`

## Notebook

* `main_study/notebooks/main_sampling_observations_v1.md`

---

# Phase 5 — Sanitisation and Manual Review

## Scripts

* `main_study/scripts/sanitise_main_dataset.py`
* `main_study/scripts/inspect_main_sanitisation_review.py`
* `main_study/scripts/flag_main_heavy_review_risks.py`
* `main_study/scripts/apply_manual_redactions_main.py`
* `main_study/scripts/verify_main_manual_sanitisation.py`
* `main_study/scripts/freeze_main_sanitised_dataset.py`
* `main_study/scripts/apply_inference_leak_redactions.py`

## Review Files

* `main_study/datasets/sanitised/review/main_manual_review_v1.xlsx`
* `main_study/datasets/sanitised/review/main_inference_leak_review_v1.xlsx`

## Final Frozen Master Dataset

The final master dataset is:

* `main_study/datasets/frozen/main_dataset_sanitised_final_v2.parquet`
* `main_study/datasets/frozen/main_dataset_sanitised_final_v2.csv`
* `main_study/datasets/frozen/main_dataset_sanitised_final_v2.xlsx`

Important lineage note:

* `main_dataset_sanitised_final_v1` was superseded by `main_dataset_sanitised_final_v2`.
* `final_v2` includes the additional inference-leak redactions identified by the hard-gate validator.
* All experiment input files were generated from `main_dataset_sanitised_final_v2.parquet`.

## Notebook

* `main_study/notebooks/manual_redaction_validation_v1.md`

---

# Phase 6 — Experiment Input Preparation

## Scripts

* `main_study/scripts/create_main_experiment_inputs.py`
* `main_study/scripts/verify_main_inference_dataset.py`
* `main_study/scripts/inspect_failed_inference_validation.py`

## Experiment Input Folder

* `main_study/experiment_inputs/`

## Inference Dataset

This is the only dataset sent to the models.

* `main_study/experiment_inputs/main_inference_dataset_v1.parquet`
* `main_study/experiment_inputs/main_inference_dataset_v1.csv`
* `main_study/experiment_inputs/main_inference_dataset_v1.xlsx`

Columns:

* `record_id`
* `description_for_model`

Rule:

* `description_for_model = final_description`
* Source master: `main_dataset_sanitised_final_v2.parquet`

## Record Mapping File

Used to reconnect model outputs to CVE IDs after inference.

* `main_study/experiment_inputs/main_record_mapping_v1.parquet`
* `main_study/experiment_inputs/main_record_mapping_v1.csv`
* `main_study/experiment_inputs/main_record_mapping_v1.xlsx`

Columns:

* `record_id`
* `cve_id`

## Verification File

Used during analysis only. Never sent to models.

* `main_study/experiment_inputs/main_record_verification_v1.parquet`
* `main_study/experiment_inputs/main_record_verification_v1.csv`
* `main_study/experiment_inputs/main_record_verification_v1.xlsx`

Columns:

* `record_id`
* `cve_id`
* `official_cvss_vector`
* `official_base_score`
* `official_severity`
* `epss_score`
* `epss_percentile`
* `published_year`
* `cvss_selection_method`

## Validation Result

Hard-gate validation passed.

Confirmed:

* 1000 inference rows
* 1000 mapping rows
* 1000 verification rows
* record IDs aligned across all files
* `description_for_model` matches `final_description`
* no CVE ID leakage
* no CVSS vector leakage
* no base score leakage in CVSS context
* no EPSS score or percentile leakage
* no empty descriptions

---

# Phase 7 — Main Experiment Execution

## Pending Script

* `main_study/scripts/run_main_experiment.py`

## Required Dependencies Before Running

Confirm the following exist before writing or running the experiment runner:

### Frozen Prompts

Use the same frozen prompts as the pilot.

* Conventional prompt
* Structured prompt

These must remain unchanged to preserve the prompt-condition comparison.

### Parser

Reuse the validated pilot parser:

* `parse_model_response.py`

### Configuration

Confirm:

* OpenAI model identifier
* Gemini model identifier
* Ollama model identifier
* `.env` API keys
* temperature = 0
* seed = 42

### Pre-flight Test

Before the full run, run each provider on 2 records from the main inference dataset to confirm:

* prompt loading works
* model authentication works
* model call works
* response parsing works

---

# Main Experiment Design

The Main Study requires repeated runs to support repeatability and reliability analysis.

Design:

* 1,000 CVEs
* 3 providers
* 2 prompt conditions
* 3 repeated runs

Expected inference records:

```text
1000 × 3 × 2 × 3 = 18,000
```

Providers:

* OpenAI GPT-5.5
* Gemini 2.5 Pro
* Ollama Llama 3 8B

Prompt conditions:

* Conventional
* Structured

Runs:

* run_001
* run_002
* run_003

---

# Required Experiment Runner Features

The runner must include:

* `run_id`
* provider tracking
* prompt-condition tracking
* checkpoint/resume
* skip-if-existing logic
* raw response saving
* parsed response saving
* error logging
* retry/backoff handling
* progress logging
* model identifier recording
* temperature and seed recording

---

# Current Status

Dataset preparation is complete.

Experiment input validation is complete.

The project is ready to confirm Phase 7 dependencies, then write the main experiment runner.
