# Parser Validation v1

## Purpose

Validate parser behaviour using frozen sanity-test outputs from both prompt conditions.

## Results

Condition 1:
- ChatGPT: strict
- Gemini: strict
- llama3:8b: strict

Condition 2:
- ChatGPT: strict
- Gemini: strict
- llama3:8b: embedded

## Validation Checks

- Parse success: passed for all six responses
- All required keys present: passed for all six responses
- Valid CVSS metric values: passed for all six responses
- Numeric base score: passed for all six responses
- Vector string present: passed for all six responses

## Conclusion

Parser v1 correctly classified and extracted model responses across strict and fenced formats.

Status: VALIDATED