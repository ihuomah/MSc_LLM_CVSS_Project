# Main Experiment Completion Record

**Date Completed:** 24 June 2026

## Purpose

This document records the successful completion of the Main Study inference execution across all three Large Language Models (LLMs) used in the dissertation.

---

# Experimental Configuration

## Dataset

* Frozen Main Study dataset
* 1,000 sanitised CVEs

## Prompt Conditions

* Conventional Prompt
* Structured Prompt

## Models

* GPT-5.5 (OpenAI)
* Gemini 2.5 Pro (Google)
* Llama 3 8B (Ollama)

Each CVE was evaluated under both prompting conditions by all three models.

Total planned inferences:

```
1,000 CVEs
× 2 Prompt Conditions
× 3 Models
=
6,000 model inferences
```

---

# Execution Summary

## OpenAI GPT-5.5

Status:

* Completed successfully

Summary:

* Expected tasks: 2,000
* Completed tasks: 2,000
* Parse failures: 0
* API failures: 0
* Outstanding tasks: 0

Notes:

The OpenAI capability probe confirmed that the model rejected both `temperature` and `seed` parameters. The experiment therefore executed using the provider's default generation settings. This behaviour is documented within the provenance manifest.

---

## Gemini 2.5 Pro

Status:

* Completed successfully

Summary:

* Expected tasks: 2,000
* Completed tasks: 2,000
* Parse failures: 0
* API failures: 0 (final state)

Execution Notes:

During the initial execution, the Gemini API reached the provider's daily request quota, resulting in HTTP 429 (`RESOURCE_EXHAUSTED`) responses after approximately 490 records had been processed.

The experiment was resumed after the quota reset using the existing resume mechanism.

Only incomplete tasks were executed during the second session.

Resume statistics:

* Newly completed tasks: 126
* Previously completed tasks skipped: 1,874

This confirms that the filesystem-based resume mechanism functioned as designed.

---

## Llama 3 8B (Ollama)

Status:

* Completed successfully

Summary:

* Expected tasks: 2,000
* Completed tasks: 2,000
* Parse failures: 60
* API failures: 0
* Outstanding tasks: 0

Notes:

All parse failures resulted from successful model execution followed by parser validation failure. Consistent with the frozen experimental protocol, these records were retained as completed observations and will be analysed as part of the RQ5 failure-mode analysis. No parse-failure records were re-executed.

---

# Overall Experiment Status

| Provider       | Completed | Parse Failures | API Failures | Outstanding |
| -------------- | --------: | -------------: | -----------: | ----------: |
| GPT-5.5        |     2,000 |              0 |            0 |           0 |
| Gemini 2.5 Pro |     2,000 |              0 |            0 |           0 |
| Llama 3 8B     |     2,000 |             60 |            0 |           0 |
| **Total**      | **6,000** |         **60** |        **0** |       **0** |

---

# Experimental Outcome

The Main Study inference phase completed successfully.

All planned model executions were completed and provider-specific outputs were exported to the canonical results directory.

The resulting dataset forms the basis of the quantitative and qualitative analyses presented in Chapters 4 and 5 of the dissertation.

---

# Status

Version: v1

Status: Main Experiment Complete
