# Run Single Inference Retry Validation v1

## Objective

To validate that the integrated inference pipeline can handle transient provider failures before scaling beyond a single record.

This retry-enabled script was created after the first integrated pipeline validation succeeded. The purpose was to add resilience before running larger batches such as the 5-record test and 50-record pilot.

---

## Why Retry Logic Was Added

The experiment uses cloud API providers as well as a local model. Cloud APIs can occasionally return temporary errors such as:

```text
503 UNAVAILABLE
429 RATE LIMIT
Temporary network failure
```

A Gemini 2.5 Pro connectivity attempt previously returned a temporary `503 UNAVAILABLE` error and then succeeded when retried later.

This showed that transient provider failures are possible and should be handled by the inference pipeline before scaling.

---

## Validation Scope

The retry-enabled script was tested using:

```text
record_id = 1
```

across:

```text
3 providers × 2 prompt conditions = 6 inference runs
```

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

## Script Tested

```text
scripts/run_single_inference_retry.py
```

---

## Output Location

Outputs were saved under:

```text
results/test_runs/run_single_inference_retry_record1/
```

The retry-enabled validation used a separate folder from the first integration validation to avoid overwriting earlier evidence.

---

## Retry Configuration

The retry-enabled script uses:

```text
MAX_RETRIES = 5
RETRY_WAIT_SECONDS = [5, 10, 20, 30, 60]
```

This means that if a provider call fails, the script waits and retries before giving up.

The maximum wait time across retries is:

```text
5 + 10 + 20 + 30 + 60 = 125 seconds
```

---

## New Metadata Fields

The retry-enabled version adds the following fields to each result row:

| Field                 | Meaning                                                 |
| --------------------- | ------------------------------------------------------- |
| `retry_count`         | Number of retry attempts used before success or failure |
| `total_retry_wait_ms` | Total time spent waiting between retries                |
| `error_type`          | Type of error encountered if the provider call failed   |
| `error_message`       | Full error message if the provider call failed          |

These fields make transient provider failures visible in the audit trail.

---

## Validation Result

The retry-enabled script completed all six inference runs successfully.

No retries were required during this validation run.

```text
Rows written: 6
Retry count: 0 for all runs
Total retry wait ms: 0 for all runs
Error type: None for all runs
```

---

## Summary of Results

| Provider | Condition    | Parse Success | Compliance | Predicted Score | Calculated Score | Consistent | Retry Count |
| -------- | ------------ | ------------- | ---------- | --------------: | ---------------: | ---------- | ----------: |
| Ollama   | conventional | True          | strict     |             9.8 |              8.8 | False      |           0 |
| Ollama   | structured   | True          | fenced     |             9.0 |              8.1 | False      |           0 |
| OpenAI   | conventional | True          | strict     |             7.2 |              7.2 | True       |           0 |
| OpenAI   | structured   | True          | strict     |             7.2 |              7.2 | True       |           0 |
| Gemini   | conventional | True          | fenced     |             9.1 |              9.1 | True       |           0 |
| Gemini   | structured   | True          | fenced     |             9.1 |              9.1 | True       |           0 |

---

## Interpretation

The retry-enabled pipeline reproduced the same outputs as the non-retry integration pipeline.

This confirms that adding retry handling did not alter the inference, parsing, or CVSS validation behaviour.

Although no retries were triggered during this validation run, the retry mechanism is now available for larger runs where transient provider failures are more likely.

---

## Conclusion

The retry-enabled single-record validation confirms that the integrated inference pipeline remains operational after adding resilience logic.

This stage provides confidence that the pipeline can proceed to the 5-record pre-pilot test while preserving retry-related metadata for auditability.
