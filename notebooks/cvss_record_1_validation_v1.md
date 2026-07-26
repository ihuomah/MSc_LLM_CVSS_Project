# CVSS Record 1 Validation v1

## Objective

To validate the full CVSS inference pipeline on a single frozen pilot record before scaling to multi-record testing.

This test used:

```text
record_id = 1
```

across:

```text
3 providers × 2 prompt conditions = 6 inference runs
```

---

## Providers Tested

| Provider | Model          |
| -------- | -------------- |
| OpenAI   | gpt-5.5        |
| Gemini   | gemini-2.5-pro |
| Ollama   | llama3:8b      |

---

## Prompt Conditions

```text
conventional
structured
```

---

## Result Storage

Outputs were saved under:

```text
results/test_runs/cvss_record_1/
```

with provider and condition subfolders.

---

## Validation Components

This test validated:

* Dataset loading from frozen pilot input
* Prompt rendering using `{DESCRIPTION}`
* Provider API/model call
* Raw response saving
* Full API response saving
* Parser execution
* CVSS vector extraction
* CVSS base score recalculation
* Vector-score consistency check
* Parsed result JSON saving

---

## Summary of Results

| Provider | Condition    | Parse Success | Compliance | Predicted      Vector                             | Predicted Score | Calculated Score | Consistent |
| -------- | ------------ | ------------- | ---------- | -------------------------------------------- | --------------: | ---------------: | ---------- |
| OpenAI   | conventional | True          | strict     | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H |             7.2 |              7.2 | True       |
| OpenAI   | structured   | True          | strict     | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H |             7.2 |              7.2 | True       |
| Gemini   | conventional | True          | fenced     | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H |             9.1 |              9.1 | True       |
| Gemini   | structured   | True          | fenced     | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H |             9.1 |              9.1 | True       |
| Ollama   | conventional | True          | strict     | CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |             9.8 |              8.8 | False      |
| Ollama   | structured   | True          | fenced     | CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N |             9.0 |              8.1 | False      |

---

## Observations

All six inference runs were successfully parsed, confirming that the parser can process outputs from all three selected providers.

OpenAI produced strict JSON-style compliance under both prompt conditions.

Gemini produced fenced outputs under both prompt conditions, but the responses remained parseable and internally vector-score consistent.

Ollama produced parseable outputs under both conditions, but both outputs showed vector-score inconsistency between the reported base score and the score recalculated from the predicted CVSS vector.

The record also shows early evidence of inter-model disagreement. OpenAI and Gemini both selected network attack vector and high privileges required, but disagreed on scope. Ollama differed further by selecting adjacent attack vector.

---

## Conclusion

The `record_id=1` validation confirms that the full CVSS inference and parsing pipeline is operational across all selected providers and prompt conditions.

The results also confirm that the pipeline can capture important reliability dimensions, including:

* Output compliance
* Prompt-condition sensitivity
* Vector-score consistency
* Cross-provider disagreement

The next step is to build `run_single_inference.py` and test it on `record_id=1` using the same providers and prompt conditions before scaling to a 5-record test and then the 50-record pilot.
