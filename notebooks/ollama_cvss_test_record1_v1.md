# Ollama CVSS Test – Record 1

## Date

2026-06-09

## Purpose

This was a non-official test run to validate prompt rendering, Ollama inference, raw response storage, parser compatibility, and CVSS vector-score consistency checking using one frozen pilot record.

This test is not part of the official pilot results.

## Test Setup

- Model: llama3:8b via Ollama local API
- Record ID: 1
- Prompt conditions:
  - conventional
  - structured
- Temperature: 0
- Seed: 42
- Output location: results/test_runs/ollama/

## Results Summary

### Conventional Prompt

- Parse success: True
- Compliance category: strict
- All keys present: True
- Valid metric values: True
- Predicted vector: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
- Predicted base score: 9.8
- Calculated base score from vector: 8.8
- Vector-score delta: +1.0
- Vector-score consistent: False
- Latency: 29620 ms

### Structured Prompt

- Parse success: True
- Compliance category: fenced
- All keys present: True
- Valid metric values: True
- Predicted vector: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N
- Predicted base score: 9.0
- Calculated base score from vector: 8.1
- Vector-score delta: +0.9
- Vector-score consistent: False
- Latency: 56166 ms

## Interpretation

The test passed from an infrastructure perspective.

The following components worked correctly:

- Frozen pilot input file loaded successfully
- Prompt templates rendered correctly using `{DESCRIPTION}`
- Ollama API call completed successfully
- Raw responses were saved
- Full API responses were saved
- Parser extracted JSON successfully
- Schema validation passed
- CVSS library recalculated scores from model-generated vectors
- Vector-score consistency check worked

Both model outputs were well-formed, but both showed vector-score inconsistency. The model-reported base score was higher than the score calculated from its own generated vector.

This is treated as model-output evidence and not as a prompt bug.

No prompt changes were made.

## Status

Prompt rendering and parser compatibility validated for Ollama on one frozen pilot record.

Official pilot execution has not yet started.