# Condition 2 Sanity Test Findings

## Purpose

The purpose of this test was to evaluate whether the structured declarative prompt produced structured, machine-readable outputs across ChatGPT, Gemini, and llama3:8b.

This was a parseability and output-discipline test, not an accuracy test.

## Findings

1. ChatGPT returned a single valid JSON object.
2. Gemini returned a single valid JSON object.
3. llama3:8b returned valid JSON embedded within explanatory text and markdown code fences.
4. llama3:8b output was parseable but not strictly schema compliant.
5. No prompt changes were made in response to scoring differences or output-discipline behaviour, in accordance with the locked refinement rule.
6. The original Ollama response is retained as evidence of an output-discipline failure under the structured prompt condition.

## Compliance Classification

- ChatGPT: strict
- Gemini: strict
- llama3:8b: fenced/embedded

## Preliminary Observation

Under the structured prompt condition, Gemini and llama3:8b produced base scores that appeared internally consistent with their generated vectors. No conclusion is drawn from this single CVE test. This observation supports the inclusion of vector-to-score consistency analysis during the pilot and main experiments.

## Action

Condition 2 is accepted for the experiment. The parser will be designed to extract valid JSON from strict, fenced, and embedded responses while logging compliance category.