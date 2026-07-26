# Main Dataset Generation Protocol v1

## Dissertation

**Title:**

Evaluating the Reliability of LLM-Based Vulnerability Scoring using the Common Vulnerability Scoring System (CVSS) and the Exploit Prediction Scoring System (EPSS)

---

# Purpose

This document defines the dataset generation protocol for the Main Study.

The purpose of this protocol is to ensure that dataset construction is reproducible, auditable, and consistent with the methodology established during the pilot study.

No dataset-generation script should be executed unless it conforms to this protocol.

---

# Relationship to Pilot Study

The pilot study successfully validated:

* NVD retrieval workflow
* CPE extraction workflow
* EPSS enrichment workflow
* Description sanitisation workflow
* Manual redaction workflow
* Inference pipeline
* Parsing pipeline
* Completeness analysis workflow
* Accuracy analysis workflow

The Main Study reuses the validated pilot methodology while increasing dataset scale.

The pilot dataset remains frozen and must not be modified.

---

# Main Study Workflow

The Main Study shall be executed in the following phases.

## Phase 1 – Protocol Freeze

1. Freeze folder structure
2. Freeze dataset generation protocol
3. Freeze experiment protocol
4. Freeze analysis protocol

---

## Phase 2 – Candidate Pool Construction

1. Retrieve CVEs from NVD
2. Extract CVSS v3.1 data
3. Extract CPE metadata
4. Build candidate pool
5. Freeze candidate pool

---

## Phase 3 – EPSS Integration

1. Download EPSS snapshot
2. Merge EPSS with candidate pool
3. Measure EPSS coverage
4. Measure EPSS coverage by severity
5. Record EPSS snapshot metadata
6. Freeze enriched candidate pool

---

   ## Phase 4 – Sampling

1. Measure candidate-pool severity distribution
2. Exclude pilot-study CVEs
3. Assess EPSS coverage suitability for sampling
4. Confirm severity distribution
5. Confirm sample size
6. Perform stratified random sampling
7. Freeze sampled dataset

### Notes

The final sample size and severity distribution shall not be frozen until the enriched candidate pool has been constructed and analysed.

This ensures that sampling decisions are based on the actual characteristics of the candidate pool rather than assumptions made before data collection.

If EPSS coverage is effectively complete across all severity strata, a fully EPSS-covered dataset may be selected.

If meaningful EPSS coverage gaps exist, the final sampling strategy shall be documented in the dataset specification and applied consistently throughout the study.

The final sampling decision shall be recorded in:

main_study/docs/main_dataset_specification_v1.md


---

## Phase 5 – Sanitisation

1. Run automated sanitisation
2. Generate sanitisation review files
3. Review residual leakage candidates
4. Apply manual redactions
5. Validate sanitised dataset
6. Freeze final dataset

---

## Phase 6 – Experiment Preparation

1. Create inference dataset
2. Create record mapping file
3. Create verification dataset
4. Freeze experiment inputs

---

## Phase 7 – Experiment Execution

1. Execute Conventional Prompt condition
2. Execute Structured Prompt condition
3. Execute OpenAI GPT-5.5
4. Execute Gemini 2.5 Pro
5. Execute Ollama Llama 3 8B
6. Parse responses
7. Validate responses
8. Calculate CVSS scores
9. Save experiment outputs

---

## Phase 8 – Analysis

1. Completeness analysis
2. Accuracy analysis
3. Prompt-condition analysis
4. EPSS correlation analysis
5. Failure-mode analysis
6. Chapter 4 interpretation

---

# Data Sources

## NVD

Source:

NVD CVE API v2.0

Ground Truth:

NVD CVSS v3.1 Base Metrics

The primary NVD CVSS v3.1 assessment shall be used as the ground-truth reference.

---

## EPSS

Source:

FIRST EPSS Daily CSV

The EPSS snapshot used during enrichment shall be frozen and recorded.

---

# Reproducibility Requirements

The following artefacts must be frozen:

* Candidate pool
* EPSS snapshot metadata
* Sampled dataset
* Sanitised dataset
* Final dataset
* Inference dataset
* Mapping dataset
* Verification dataset

Random seed shall be fixed at:

42

for all sampling operations.

---

# Pilot Independence Rule

The 50 pilot-study CVEs shall be excluded from the Main Study candidate pool before final sampling.

This ensures that pilot observations and main-study findings remain independent.

---

# Governance

docs/
Records decisions and frozen protocols.

notebooks/
Records observations, findings, and interpretation notes.

audit/
Records machine-generated logs and audit evidence.

---

# Status

Version: v1

Status: Frozen Pending Main Dataset Construction