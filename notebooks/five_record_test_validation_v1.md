# Five-Record Test Validation v1

## Objective

To validate that the retry-enabled inference pipeline can scale beyond a single record before executing the 50-record pilot.

The purpose of this test was operational validation, not accuracy analysis.

---

## Test Scope

The test used the first five sequential records from the frozen pilot input dataset:

```text
record_id = 1, 2, 3, 4, 5
```

This produced:

```text
5 records × 3 providers × 2 prompt conditions = 30 inference runs
```

---

## Providers and Prompt Conditions

Providers:

```text
OpenAI  : gpt-5.5
Gemini  : gemini-2.5-pro
Ollama  : llama3:8b
```

Prompt conditions:

```text
conventional
structured
```

---

## Script Used

```text
scripts/run_five_record_test.py
```

---

## Output Location

```text
results/test_runs/five_record_test/
```

The test outputs were intentionally saved under `results/test_runs/` because this was a validation run, not the locked pilot.

---

## Result Summary

The five-record test completed successfully.

```text
Rows written: 30
Records tested: [1, 2, 3, 4, 5]
Results file: results/test_runs/five_record_test/five_record_test_results.xlsx
```

All 30 inference runs completed and produced saved raw, API, parsed, and tabular outputs.

---

## Validation Evidence

The test confirmed that the pipeline can:

* Load multiple records sequentially
* Render both prompt conditions for each record
* Run all three selected providers
* Save raw model responses
* Save full API responses
* Parse model outputs
* Recalculate CVSS base scores
* Check vector-score consistency
* Write consolidated results to Excel
* Continue saving progress after each inference

---

## Retry Metadata

The retry system was active during the test.

No retries were required during this run:

```text
retry_count = 0
total_retry_wait_ms = 0
error_type = None
```

This indicates that no transient provider failures occurred during the 30 inference calls.

---

## Sequential Record Selection Rationale

The first five records were selected sequentially because this was an operational validation test rather than a performance evaluation.

The purpose was to test whether the pipeline could process multiple records in the same order expected during the pilot and main experiment.

Severity-balanced analysis is reserved for the 50-record pilot dataset, which already contains a predefined mix of Critical, High, Medium, and Low severity vulnerabilities.

---

## Key Observations

All providers produced parseable outputs across all tested records and prompt conditions.

OpenAI and Gemini consistently produced internally vector-score-consistent outputs.

Ollama produced parseable outputs, but several outputs showed inconsistency between the reported base score and the base score recalculated from the predicted CVSS vector.

The test also confirmed that the parser can handle multiple compliance categories, including strict, fenced, and embedded outputs.

---

## Conclusion

The five-record test confirms that the retry-enabled inference pipeline can scale from single-record validation to sequential multi-record execution.

This provides sufficient operational confidence to prepare the locked 50-record pilot script.

The next step is to create the 50-record pilot execution script using the same retry-enabled logic, updating the output paths to the locked pilot folders and adding skip-if-existing logic to protect against partial-run interruption.
