# Phase 7 Runner Design Decisions

**Project:** Evaluating the Reliability of LLM-Based Vulnerability Scoring using the Common Vulnerability Scoring System (CVSS) and the Exploit Prediction Scoring System (EPSS)

**Date:** June 2026

---

# Purpose

This document records the design decisions agreed before implementation of the Phase 7 experiment runner.

The objective is to document the intended experiment execution architecture before implementation and execution begin.

---

# 1. Pre-Flight Validation Strategy

## Decision

No separate pre-flight script will be created.

Instead, the production experiment runner will support execution of a subset of records.

## Rationale

A separate pre-flight script would validate only a simplified code path and may fail to test the components that are most likely to cause issues during long-running execution.

Examples include:

* run_id path construction
* checkpoint/resume behaviour
* skip-if-existing logic
* results accumulation
* raw response saving
* parsed response saving
* provider metadata recording

Using the production runner for the pre-flight ensures that exactly the same code path is tested before launching the full experiment.

## Implementation

The production runner (`run_main_experiment.py`) will support execution of a subset of records.

Example pre-flight command:

```bash
python run_main_experiment.py --run-id run_001 --records 1,2
```

---

# 2. Runtime Packaging

## Decision

Create a dedicated runtime environment inside the Main Study folder.

## Rationale

This reduces dependency on pilot-study infrastructure and creates a self-contained execution environment for the main experiment.

The pilot assets remain preserved as archival frozen versions.

## Runtime Structure

```text
main_study/runtime/

├── config.py

├── parser/
│   └── parse_model_response_v1.py

└── prompts/
    ├── condition1_conventional_prompt_v1.txt
    └── condition2_structured_prompt_v1.txt
```

---

# 3. Determinism Configuration

## Experimental Target Configuration

```text
Temperature = 0
Seed = 42
```

## Provider Handling

### Ollama

Expected behaviour:

```text
temperature = supported
seed = supported
```

The runner will apply both parameters.

### Gemini

The runner will attempt to apply:

```text
temperature = 0
seed = 42
```

The runner will record whether parameter application was confirmed or unconfirmed.

### OpenAI

The runner will probe supported parameters during startup.

The runner will not assume that:

```text
temperature
seed
```

are accepted by the selected model.

Parameter support and application status will be recorded.

## Note: 
 The pilot runner applied temperature/seed to Ollama only, while the main runner will explicitly record parameter support and application status for all providers.

## Provenance Recording

The runner will record:

```text
requested_temperature
requested_seed

temperature_applied_status
seed_applied_status
```

where supported.

No unsupported parameter will be assumed to have been applied.

---

# 4. Provider Capability Probe

## Decision

Provider parameter support will be determined once at startup.

## Rationale

Repeated capability testing for every record would introduce unnecessary API calls and additional complexity.

A single startup probe allows the runner to:

* determine accepted parameters
* record provider capabilities
* apply a consistent configuration during execution

The capability probe forms part of the pre-flight validation process.

---

# 5. Dataset Handling

## Decision

The inference dataset will be loaded once at startup.

## Rationale

The pilot implementation reloaded the dataset for each inference.

This approach is acceptable for small pilot datasets but becomes inefficient for large-scale execution.

The main experiment contains:

```text
1000 records
```

and therefore the dataset will be loaded once and indexed in memory.

---

# 6. Results Persistence

## Decision

The runner will avoid rewriting the complete Excel workbook after every inference.

## Rationale

At main-study scale:

```text
1000 CVEs
3 providers
2 prompt conditions
```

the total workload becomes:

```text
6000 inference records
```

Repeated full-workbook rewrites increase execution time and create additional corruption risk during interruption.

The runner will use a safer persistence strategy suitable for long-running execution.

---

# 7. Main Experiment Scope

## Current Locked Scope

```text
1000 CVEs
3 Providers
2 Prompt Conditions
```

Providers:

```text
OpenAI GPT-5.5
Gemini 2.5 Pro
Ollama Llama 3 8B
```

Prompt Conditions:

```text
Conventional Prompt
Structured Prompt
```

Total:

```text
1000 × 3 × 2
=
6000 inference records
```

---

# 8. Repeatability Study

Repeatability remains a research objective.

However, the exact repeatability scope has not yet been locked.

The runner will therefore support:

```text
run_id
```

and repeated executions.

Examples:

```text
run_001
run_002
run_003
```

The final repeatability design will be documented separately once approved.

---

# 9. Pre-Flight Scope

The pre-flight validation will execute:

```text
2 records
3 providers
2 prompt conditions
```

Total:

```text
2 × 3 × 2
=
12 inference executions
```

The objective is to validate:

* prompt loading
* parser loading
* provider connectivity
* output folder creation
* raw response saving
* parsed output saving
* results persistence
* metadata recording
* startup capability probe
* run_id handling

before launching the full experiment.

---

# 10. Readiness Status

Current status:

```text
Dataset Preparation        COMPLETE
Sanitisation              COMPLETE
Inference Leakage Review  COMPLETE
Experiment Inputs         COMPLETE
Prompt Freeze             COMPLETE
Parser Freeze             COMPLETE
API Connectivity          COMPLETE
Budget Preparation        COMPLETE
```

Next step:

```text
Implement run_main_experiment.py
Run 2-record pre-flight
Verify outputs
Launch main experiment
```
---


# 11. Resume and Checkpoint Strategy

## Decision

The filesystem will be the canonical source of truth for experiment completion and resume behaviour.

No standalone checkpoint file will be used as the authoritative completion record.

## Rationale

The experiment may run for many hours and may be interrupted due to:

* API failures
* machine restarts
* network interruptions
* user intervention

A single checkpoint file introduces a potential single point of failure.

Using the filesystem as the completion manifest ensures that each completed inference remains independently recoverable.

## Completion Authority

A completed inference is defined as an inference that successfully received a response from the provider API, regardless of whether the response was parseable.

Completion is determined for a specific combination of:

```text
record_id
provider
prompt_condition
run_id
```

Example:

```text
R0001
openai
conventional
run_001
```

## Canonical Result States

### State 1: API Success + Parse Success

```text
api_success = True
parse_success = True
```

Result:

```text
Complete
Skip on resume
```

### State 2: API Success + Parse Failure

```text
api_success = True
parse_success = False
```

Result:

```text
Complete
Skip on resume
```

Rationale:

A malformed or non-compliant model response is still the model's actual response under the locked experimental conditions.

These records represent valid evidence for reliability and failure-mode analysis and must not be re-executed in an attempt to obtain a different response.

### State 3: API Failure

```text
api_success = False
```

Result:

```text
Incomplete
Eligible for re-execution
```

Examples:

```text
Timeout
Rate limit exhaustion
Authentication failure
Network failure
Provider outage
```

## Resume Behaviour

When the runner starts:

1. Existing canonical result files are inspected.
2. Records with API success are skipped.
3. Records without API success remain eligible for execution.
4. Interrupted runs continue from the remaining incomplete records.

This provides:

```text
checkpoint
resume
interrupt recovery
```

without dependence on a separate checkpoint database or manifest.

---


# 12. Failure Handling Strategy

## Decision

Only API failures will be treated as execution failures.

Parse failures will be treated as valid experimental outcomes.

## Rationale

The objective of the study is to evaluate reliability, consistency, and failure modes of LLM-based CVSS scoring.

A response that fails parser validation is still an authentic model output and therefore constitutes valid experimental evidence.

Treating parse failures as execution failures would:

* bias results
* introduce re-roll behaviour
* distort repeatability measurements
* remove important failure-mode evidence

## API Failure Recording

API failures will be recorded separately.

Examples:

```text
Timeout
Rate limit exhaustion
Authentication error
Network failure
Provider service error
```

Failure information will be written to:

```text
main_study/results/failures/run_001_failures.jsonl
```

## Parse Failure Recording

Parse failures remain part of the canonical experiment dataset.

Examples:

```text
Missing fields
Invalid metric values
Non-compliant formatting
Unexpected content
Parser validation failure
```

These records will be stored in the standard results outputs with:

```text
api_success = True
parse_success = False
```

and remain available for:

```text
RQ5 failure-mode analysis
compliance analysis
repeatability analysis
```

## Re-Execution Policy

Only API failures are eligible for future re-execution.

Parse failures are never re-executed.


# 13. Results Persistence Strategy

## Decision

The experiment outputs will be maintained in three formats.

## Output Formats

### Parquet

Primary master dataset.

```text
run_001_results.parquet
```

Used for:

* analysis
* long-term storage
* preservation of full field content

### CSV

Portable backup and interoperability format.

```text
run_001_results.csv
```

### XLSX

Human-readable review format.

```text
run_001_results.xlsx
```

## Important Note

The XLSX file is not the authoritative experiment output.

Excel may truncate very large fields and should be treated as a convenience view only.

The Parquet file remains the authoritative experiment dataset.


## Export Generation Strategy

Canonical per-record output files are the authoritative experiment record.

The aggregate result tables:

```text
run_001_results.parquet
run_001_results.csv
run_001_results.xlsx
```

are derived artefacts generated from the canonical per-record outputs.

### Export Rules

Parquet:

```text
Authoritative aggregate dataset
```

CSV:

```text
Portable backup/export format
```

XLSX:

```text
Human-readable review format
```

### Rebuild Behaviour

Aggregate result tables may be regenerated at any time by scanning the canonical per-record output files.

If an export file becomes corrupted, incomplete, or out of date, it can be rebuilt without loss of experimental data.

The canonical per-record files remain the authoritative source of truth.

---



---

# 14. Runtime Asset Integrity and Provenance Verification

## Decision

Runtime assets and execution environment metadata will be recorded at startup.

## Assets Covered

```text
main_study/runtime/config.py

main_study/runtime/parser/parse_model_response_v1.py

main_study/runtime/prompts/
    condition1_conventional_prompt_v1.txt

main_study/runtime/prompts/
    condition2_structured_prompt_v1.txt

main_study/experiment_inputs/main_inference_dataset_v1.parquet
```

## Recorded Information

For each runtime asset:

```text
asset_path
sha256_hash
```

Additional provenance information:

```text
OpenAI model identifier
Gemini model identifier
Ollama model identifier

Provider capability probe results

requested_temperature
requested_seed

temperature_status
seed_status

Python version

Installed package versions:
    openai
    google-genai
    requests
    pandas
    pyarrow
    cvss
```

## Storage Location

The provenance manifest will be saved to:

```text
main_study/results/logs/run_001_provenance_manifest.json
```

## Rationale

This provides a complete record of:

* datasets used
* prompts used
* parser version used
* model configuration
* provider capabilities
* software environment

and supports reproducibility and auditability of the experiment.

### Frozen Asset Verification

Runtime copies were created to support a self-contained execution environment.

However, the frozen prompts and parser remain the authoritative experiment artefacts.

At startup, the runner will verify that:

```text
runtime asset hash
=
corresponding frozen asset hash




# 15. Pre-Flight Execution Method

## Decision

The pre-flight validation will use the production experiment runner.

No separate validation runner will be created.

## Rationale

Using the production runner validates the exact code path that will be used for the full experiment.

This includes:

* run_id handling
* provider execution
* prompt loading
* parser execution
* output generation
* resume logic
* failure handling

## Example Command

```bash
python run_main_experiment.py --run-id run_001 --records 1,2
```

This executes:

```text
2 records
3 providers
2 prompt conditions

=
12 inference executions
```

using the same execution path as the full experiment.
