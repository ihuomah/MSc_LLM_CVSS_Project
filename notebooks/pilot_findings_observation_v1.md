# Pilot Findings Observation v1

**Date:** [Insert Date]
**Dataset:** Frozen Pilot v2 (50 CVEs)
**Run ID:** pilot_run_001
**Script:** scripts/run_pilot_50.py
**Models:** OpenAI GPT-5.5, Gemini 2.5 Pro, Ollama Llama3:8B
**Conditions:** Conventional, Structured

---

## Purpose

This document records observations from the 50-record pilot experiment before scaling to the main dataset.

These observations are preliminary and are intended to guide interpretation, discussion, and decisions regarding the main experiment. They should not be treated as final dissertation conclusions.

---

## Observation 1: Pilot Infrastructure Successfully Executed End-to-End

The pilot experiment completed successfully across all three providers and both prompting conditions.

Expected observations:

```text
50 CVEs × 3 providers × 2 conditions = 300 rows
```

Final completeness analysis confirmed:

```text
300 rows generated
297 valid parsed rows
3 invalid outputs
99.0% parse success rate
0 missing rows
0 retries
```

The invalid outputs were:

| Record ID | Provider | Condition  | Failure Type                |
| --------- | -------- | ---------- | --------------------------- |
| R006      | Ollama   | Structured | Instruction non-compliance  |
| R022      | Ollama   | Structured | Instruction non-compliance  |
| R049      | Gemini   | Structured | Output structure corruption |

This demonstrates that the experimental pipeline, parser, storage architecture, and analysis workflow are operational and suitable for larger-scale execution.

Related Research Questions:

* RQ4
* RQ5

---

## Observation 2: OpenAI Demonstrated the Highest Overall Accuracy

Across exact vector matching, severity matching, and score error metrics, OpenAI demonstrated the strongest overall pilot performance.

Key observations:

| Metric                            | OpenAI Conventional | OpenAI Structured |
| --------------------------------- | ------------------- | ----------------- |
| Exact vector match                | 30%                 | 30%               |
| Severity match                    | 60%                 | 58%               |
| Mean Absolute Error (MAE)         | 1.134               | 1.312             |
| Internal vector-score consistency | 98%                 | 98%               |

OpenAI also showed the lowest prompt sensitivity, with very low condition-flip rates across CVSS metrics.

This suggests that OpenAI produced the most stable and accurate outputs in the pilot, although exact vector reproduction remained limited.

Related Research Questions:

* RQ1
* RQ2
* RQ4

---

## Observation 3: Gemini Produced Moderate Accuracy with One Structural Failure

Gemini generally performed between OpenAI and Ollama in terms of accuracy.

Key observations:

| Metric                            | Gemini Conventional | Gemini Structured |
| --------------------------------- | ------------------- | ----------------- |
| Exact vector match                | 22%                 | 20.41%            |
| Severity match                    | 48%                 | 46.94%            |
| Mean Absolute Error (MAE)         | 1.280               | 1.3061            |
| Internal vector-score consistency | 84%                 | 87.76%            |

One Gemini structured-prompt output failed parsing:

| Record ID | Provider | Condition  | Failure Type                |
| --------- | -------- | ---------- | --------------------------- |
| R049      | Gemini   | Structured | Output structure corruption |

The raw response for R049 contained an incomplete JSON structure, an unexpected token (`SALT-ACTION`), and a second complete JSON object. The output therefore contained a recoverable human-readable assessment but was not compliant with the automated extraction requirements.

This represents an output-structure reliability failure rather than a CVSS reasoning failure.

Related Research Questions:

* RQ2
* RQ4
* RQ5

---

## Observation 4: Ollama Exhibited Significant Prompt Sensitivity

Ollama showed substantially higher condition-flip rates than the cloud models.

Examples from the prompt condition flip analysis:

| Metric                     | Flip Rate |
| -------------------------- | --------- |
| Attack Vector (AV)         | 41.67%    |
| Confidentiality Impact (C) | 37.5%     |
| Availability Impact (A)    | 59.57%    |

This indicates that small changes in prompt structure can materially affect Ollama's interpretation of the same vulnerability description.

Related Research Questions:

* RQ1
* RQ4
* RQ5

---

## Observation 5: Ollama Produced Two Structured-Condition Parse Failures

Two Ollama structured-prompt responses failed parsing:

| Record ID | Provider | Condition  | Failure Type               |
| --------- | -------- | ---------- | -------------------------- |
| R006      | Ollama   | Structured | Instruction non-compliance |
| R022      | Ollama   | Structured | Instruction non-compliance |

In both cases, the model generated explanatory prose and CVSS reasoning rather than the required structured output format.

The responses contained information that a human could interpret, but they were not suitable for automated extraction. This indicates a failure of output discipline under the structured condition.

Related Research Questions:

* RQ4
* RQ5

---

## Observation 6: Structured Prompting Did Not Consistently Improve Performance

The pilot results do not provide evidence that structured prompting universally improves reliability or accuracy.

Observed effects varied by provider:

| Provider | Effect of Structured Prompting                                                                          |
| -------- | ------------------------------------------------------------------------------------------------------- |
| OpenAI   | Little change in exact vector match and severity match                                                  |
| Gemini   | Slightly lower exact vector and severity match, but slightly improved internal vector-score consistency |
| Ollama   | Slight improvement in score error but worse parseability and exact vector match                         |

The impact of structured prompting appears provider-dependent rather than universally beneficial.

Related Research Questions:

* RQ4

---

## Observation 7: Exact Vector Matching Was Substantially Lower Than Per-Metric Agreement

All models achieved higher per-metric agreement rates than exact vector match rates.

This suggests that models frequently identify several CVSS metrics correctly while still failing to reproduce the complete official vector.

A single incorrect metric is sufficient to prevent an exact vector match.

For example, OpenAI conventional achieved strong agreement on several individual metrics:

| Metric                 | Agreement |
| ---------------------- | --------- |
| Attack Vector (AV)     | 90%       |
| Attack Complexity (AC) | 92%       |
| Scope (S)              | 90%       |

However, its exact vector match rate was 30%.

Related Research Questions:

* RQ2

---

## Observation 8: Severity Classification Was More Accurate Than Exact Vector Reproduction

Severity match rates were consistently higher than exact vector match rates.

Examples:

| Provider | Condition    | Exact Vector Match | Severity Match |
| -------- | ------------ | ------------------ | -------------- |
| OpenAI   | Conventional | 30%                | 60%            |
| Gemini   | Conventional | 22%                | 48%            |
| Ollama   | Conventional | 6%                 | 30%            |

This suggests that models often place vulnerabilities into approximately correct risk categories even when the exact CVSS vector differs from the official assessment.

This occurs because a predicted vector can differ from the official vector while still producing a score within the same official severity band.

Related Research Questions:

* RQ2

---

## Observation 9: Distinct Failure Modes Were Observed

The pilot identified several failure modes:

1. Output structure corruption.
2. Instruction non-compliance.
3. Internal vector-score inconsistency.
4. Prompt-condition instability.

Examples:

| Failure Mode                        | Example                                       |
| ----------------------------------- | --------------------------------------------- |
| Output structure corruption         | Gemini R049 structured                        |
| Instruction non-compliance          | Ollama R006 and R022 structured               |
| Internal vector-score inconsistency | Especially frequent in Ollama outputs         |
| Prompt-condition instability        | High Ollama flip rates across several metrics |

These findings support the inclusion of failure-mode analysis as a core component of reliability evaluation.

Related Research Questions:

* RQ5

---

## Observation 10: Preliminary CVSS–EPSS Relationships Differed Across Models

The official CVSS baseline exhibited a weak positive Spearman correlation with EPSS:

```text
Official CVSS baseline rho = 0.2695
```

Observed model correlations varied across providers and prompting conditions:

| Provider | Condition    | Spearman rho |
| -------- | ------------ | ------------ |
| Ollama   | Conventional | -0.1078      |
| Ollama   | Structured   | 0.1546       |
| OpenAI   | Conventional | 0.2850       |
| OpenAI   | Structured   | 0.2172       |
| Gemini   | Conventional | 0.3550       |
| Gemini   | Structured   | 0.4415       |

OpenAI conventional closely matched the official CVSS baseline, while Gemini structured produced the strongest positive relationship with EPSS in the pilot.

These observations require validation on a larger dataset before interpretation as final findings.

Related Research Questions:

* RQ3

---

## Pilot Assessment

The pilot successfully demonstrated that:

* The experimental design is operational.
* The result pipeline can generate, preserve, parse, and analyse LLM CVSS outputs.
* All five research questions can be evaluated using the collected data.
* Meaningful differences exist between providers and prompting conditions.
* Reliability, stability, accuracy, and failure modes can be measured quantitatively.

The pilot therefore provides sufficient evidence to justify progression to the main experiment.

---

## Methodological Note

The pilot findings remain preliminary.

No failed outputs were re-run, manually corrected, or repaired.

The pilot results were retained as authentic experimental outcomes.


## Research Question Evidence Mapping

## RQ1

Research Question

To analyse how LLMs interpret CVE descriptions and generate structured CVSS vectors under different prompting strategies.

## Pilot Evidence

OpenAI exhibited very low prompt-condition flip rates.
Gemini showed moderate prompt-condition flip rates.
Ollama exhibited high prompt-condition flip rates across multiple CVSS metrics.
Structured prompting changed how different models interpreted the same CVE descriptions.

## Relevant Tables

Table 2
Table 6

## Preliminary Pilot Finding

Different LLMs interpret the same CVE descriptions differently, and the impact of prompting strategy varies significantly between providers.

## RQ2

Research Question

To evaluate the accuracy and consistency of LLM-generated CVSS metrics against ground-truth CVSS scores.

## Pilot Evidence

OpenAI achieved the highest metric agreement rates.
OpenAI achieved the highest severity match rates.
OpenAI achieved the lowest score error.
Exact vector reproduction remained difficult for all providers.

## Relevant Tables

Table 2
Table 3
Table 4
Table 5

## Preliminary Pilot Finding

OpenAI demonstrated the strongest overall accuracy, while exact reproduction of complete CVSS vectors remained challenging for all models.

## RQ3

Research Question

To analyse the correlation between LLM-generated CVSS severity scores and exploit probability indicators obtained from EPSS.

## Pilot Evidence

Official CVSS baseline produced a weak positive correlation with EPSS.
OpenAI conventional most closely matched the official baseline relationship.
Gemini structured produced the strongest positive CVSS–EPSS correlation.
Ollama exhibited weak or negative relationships with EPSS.

## Relevant Tables

Table 7

## Preliminary Pilot Finding

Different models produce different CVSS–EPSS relationships, suggesting variation in how generated severity scores align with exploit-probability rankings.


## Interpretation Guide for Spearman's Rho (RQ3)

The following interpretation bands were used to assist interpretation of Spearman correlation coefficients:

Absolute rho value	Interpretation
0.00–0.19	        Very weak
0.20–0.39	        Weak
0.40–0.59	        Moderate
0.60–0.79	        Strong
0.80–1.00	        Very strong

These bands are provided as general statistical interpretation guidelines and are used only to support discussion of CVSS–EPSS relationships observed during the pilot analysis.


## Source	Rho	Interpretation

Official CVSS	      0.2695       Weak positive
OpenAI Conventional	  0.2850	   Weak positive
OpenAI Structured	  0.2172	   Weak positive
Gemini Conventional	  0.3550	   Weak positive
Gemini Structured	  0.4415	   Moderate positive
Ollama Conventional	 -0.1078	   Very weak negative
Ollama Structured	  0.1546	   Very weak positive

## RQ4

Research Question

To examine whether structured prompting improves the reliability and stability of LLM-generated CVSS vectors when compared to conventional baseline prompting.

## Pilot Evidence

Structured prompting did not consistently improve performance.
OpenAI showed minimal difference between prompting conditions.
Gemini experienced a structured-condition parse failure.
Ollama experienced two structured-condition parse failures.
Structured prompting improved some metrics while degrading others.

## Relevant Tables

Table 2
Table 3
Table 4
Table 5
Table 6

## Preliminary Pilot Finding

The impact of structured prompting appears provider-dependent and does not universally improve reliability.

## RQ5

Research Question

To pinpoint LLM limits, patterns of instability or specific failure modes that make vulnerability scores unreliable.

## Pilot Evidence

Failure modes identified include:

Output structure corruption.
Instruction non-compliance.
Internal vector-score inconsistency.
Prompt-condition instability.

## Examples include:

Gemini R049.
Ollama R006.
Ollama R022.

## Relevant Tables

Completeness Analysis
Table 6
Failure Inventory

## Preliminary Pilot Finding

Distinct reliability failure modes exist and differ across providers.