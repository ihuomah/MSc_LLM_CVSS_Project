# Pilot Failure Modes Observation v1

## Purpose

This note documents the failure modes observed during the 50-record pilot experiment.

The objective is to identify patterns of instability and output unreliability relevant to Research Question 5.

---

## Pilot Overview

Total inferences:

```text
300
```

Successful parses:

```text
297
```

Failed parses:

```text
3
```

Overall parse rate:

```text
99.0%
```

Affected outputs:

| Record ID | Provider | Condition  |
| --------- | -------- | ---------- |
| 6         | Ollama   | Structured |
| 22        | Ollama   | Structured |
| 49        | Gemini   | Structured |

---

## Failure Mode 1: Output Structure Corruption

### Example

Record:

```text
R049
```

Provider:

```text
Gemini
```

Condition:

```text
Structured
```

### Observed Behaviour

The response contained:

* An incomplete JSON structure.
* An unexpected token ("SALT-ACTION").
* A second complete JSON object.

The overall response was not parseable as a valid structured output.

### Classification

```text
Output Structure Corruption
```

### Notes

The response appeared to contain a recoverable CVSS assessment, but the output format violated the required schema and could not be processed automatically.

The response was retained unchanged and not re-run.

---

## Failure Mode 2: Instruction Non-Compliance

### Examples

Records:

```text
R006
R022
```

Provider:

```text
Ollama
```

Condition:

```text
Structured
```

### Observed Behaviour

The model generated:

* Narrative reasoning.
* Metric explanations.
* CVSS assessment text.

However, it did not produce the required structured output format specified by the prompt.

### Classification

```text
Instruction Non-Compliance
```

### Notes

The responses contained usable information for a human reader but did not satisfy the output-format requirements of the automated extraction pipeline.

The responses were retained unchanged and not re-run.

---

## Observed Pattern

All pilot parse failures occurred under the Structured prompting condition.

Failure distribution:

| Provider | Conventional | Structured |
| -------- | ------------ | ---------- |
| OpenAI   | 0            | 0          |
| Gemini   | 0            | 1          |
| Ollama   | 0            | 2          |

No parse failures were observed under the Conventional condition.

---

## Research Question Relevance

### RQ4

To examine whether introducing structured prompting improves the reliability and stability of LLM-generated CVSS vectors.

The pilot indicates that structured prompting can introduce output-format failures for some models.

### RQ5

To pinpoint LLM limits, patterns of instability or specific failure modes that make vulnerability scores unreliable.

Two distinct failure modes were identified:

1. Output Structure Corruption.
2. Instruction Non-Compliance.

These failure modes reduce the reliability of automated CVSS extraction despite the models producing technically meaningful responses.

---

## Methodological Decision

The failed outputs were retained as authentic experimental outcomes.

No parser modifications, prompt changes, response repairs, or re-runs were performed following these observations.

The pilot dataset remains unchanged.
