# Condition 1 Sanity Test Findings

## Test Purpose

The purpose of this test was to validate whether the conventional natural-language prompt could produce structured, machine-readable JSON output across ChatGPT, Gemini, and llama3:8b.

This was a parseability and output-discipline test, not an accuracy test.

## Findings

1. All three models returned a single valid JSON object.
2. All three models used the expected JSON keys.
3. All three models used valid CVSS metric codes.
4. No model included markdown code fences, preamble, or explanatory text.
5. The conventional prompt achieved strict schema compliance across all three tested models.
6. The three models produced different CVSS vectors and base scores for the same vulnerability description.
7. llama3:8b produced an internally inconsistent output: the returned vector string was not consistent with the reported base score of 0.0.

## Key Methodological Implication

The main experiment must separate:
- per-metric agreement,
- vector-to-score consistency,
- base-score agreement against ground truth.

This is necessary because a model may assign CVSS metrics and still fail to calculate the corresponding CVSS base score correctly.

## Action

No changes will be made to the conventional prompt based on this test because the prompt passed the parseability check. Accuracy and scoring performance will be evaluated later during the full pilot experiment.


## Prompt changes are allowed only for:

1. Parseability fixes:
   malformed JSON, missing keys, wrong key names, invalid value format.

2. Methodological fairness fixes:
   differences between Condition 1 and Condition 2 that introduce unfair comparison, such as different metric order, different JSON keys, different valid values, or different anti-memorisation instructions.

## Prompt changes are not allowed for:

3. Accuracy fixes:
   wrong CVSS metric choices, wrong base score, disagreement with NVD ground truth, or disagreement between models.