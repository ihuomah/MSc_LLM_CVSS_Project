# Phase 7 Pre-Flight Validation Results

**Project:** Evaluating the Reliability of LLM-Based Vulnerability Scoring using CVSS and EPSS
**Date:** June 2026
**Runner:** `main_study/scripts/run_main_experiment.py`
**Validation Run ID:** `run_001` archived as validation output before the main run

---

# Purpose

The purpose of this pre-flight validation was to confirm that the Phase 7 main experiment runner worked correctly before launching the full 1000-record main study.

The pre-flight used the production runner itself rather than a separate test script.

---

# Pre-Flight Command

```powershell
python main_study\scripts\run_main_experiment.py --run-id run_001 --records 1,2
```

This executed:

```text
2 records
3 providers
2 prompt conditions
=
12 inference tasks
```

---

# Resume Test Command

```powershell
python main_study\scripts\run_main_experiment.py --run-id run_001 --records 1,2,3
```

Expected behaviour:

```text
Records 1 and 2 skipped
Record 3 executed
```

Observed result:

```text
Success this session: 6
Skipped this session: 12
Canonical completed rows: 18
Outstanding incomplete tasks: 0
```

This confirmed that filesystem-based resume and skip-if-existing logic worked correctly.

---

# Combine Export Test

```powershell
python main_study\scripts\run_main_experiment.py --run-id run_001 --combine-only
```

Observed result:

```text
Combined exports rebuilt. Rows exported: 18
```

This confirmed that the combined export step worked correctly.

---

# Capability Probe Results

OpenAI:

```text
temperature = unsupported_or_rejected
seed = unsupported_or_rejected
```

Reason:

```text
gpt-5.5 rejected temperature as unsupported.
OpenAI Responses API did not accept seed.
```

Gemini:

```text
temperature = accepted_unconfirmed
seed = accepted_unconfirmed
```

Ollama:

```text
temperature = accepted_unconfirmed
seed = accepted_unconfirmed
```

---

# Runtime Integrity Results

The runtime parser and prompts matched the frozen originals.

The following were hash-verified:

```text
runtime parser
runtime conventional prompt
runtime structured prompt
input dataset
frozen parser
frozen conventional prompt
frozen structured prompt
```

No integrity mismatch occurred.

---

# Pre-Flight Output Summary

The pre-flight produced:

```text
18 canonical result rows
0 outstanding tasks
0 API failures
0 parse failures
```

The generated outputs included:

```text
raw responses
API responses
parsed result files
provider-specific exports
combined Parquet/CSV/XLSX exports
provenance manifest
log files
```

---

# Archiving Action

The validation outputs were archived before launching the real main experiment.

Archive location:

```text
main_study/validation_runs_archive/run_001_validation/
```

The active `main_study/results/` folders were then cleared but preserved.

This ensures that the real main study can use a clean `run_001` without mixing validation outputs with experiment outputs.

---

# Conclusion

The Phase 7 runner passed pre-flight validation.

The following were confirmed:

```text
provider connectivity
prompt loading
parser loading
runtime integrity verification
capability probing
canonical file writing
resume logic
skip-if-existing logic
provider-specific exports
combined export generation
provenance logging
```

The main study is ready to launch using provider-specific terminals.
