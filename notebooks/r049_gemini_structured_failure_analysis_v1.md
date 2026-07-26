# R049 Gemini Structured Failure Analysis v1

## Purpose

This note documents the only parse failure observed during the 50-record pilot experiment.

The objective is to preserve the observed behaviour exactly as it occurred during the pilot run without modifying the dataset, parser, prompts, or model outputs.

---

## Experimental Context

Provider: Gemini

Prompt Condition: Structured

Record ID: 49

Pilot Run: run_001

Observed Result:

```text
parse_success: False
compliance_category: invalid
```

All other pilot outputs were successfully parsed.

---

## Raw Response Inspection

The raw response contained the following structure:

1. Opening JSON code fence.
2. Beginning of a JSON object.
3. Unexpected text token:

```text
SALT-ACTION
```

4. A second JSON code fence.
5. A complete JSON object containing all required CVSS fields.

The response therefore contained multiple JSON-like structures rather than a single valid JSON object.

---

## Parser Behaviour

The parser classified the response as:

```text
parse_success: False
compliance_category: invalid
```

This behaviour is considered correct.

The parser is designed to validate compliance with the required output structure and does not attempt to recover or repair malformed responses.

No parser modifications were made following this observation.

---

## Observed Failure Mode

The model generated a response that contained:

* An incomplete JSON object.
* An unexpected non-CVSS token ("SALT-ACTION").
* A second complete JSON object.

Although the second JSON object appears human-readable and contains a valid CVSS assessment, the overall response is structurally invalid from the perspective of an automated extraction pipeline.

This event is therefore classified as:

```text
Output Structure Failure
```

rather than:

```text
CVSS Reasoning Failure
```

---

## Research Question Relevance

This observation is relevant to:

### RQ4

To examine whether introducing structured prompting improves the reliability and stability of LLM-generated CVSS vectors.

The failure occurred under the structured prompting condition.

### RQ5

To pinpoint LLM limits, patterns of instability or specific failure modes that make vulnerability scores unreliable.

The event represents a documented example of output-format instability causing automated extraction failure.

---

## Methodological Decision

The response will not be re-run, corrected, repaired, or manually recovered.

The pilot dataset remains unchanged.

The observation is retained as an authentic outcome of the experiment and will be included in subsequent reliability analysis.

---

## Status

Investigation completed.

No changes required to:

* Dataset
* Prompt templates
* Parser
* Experimental design
* Pilot results
