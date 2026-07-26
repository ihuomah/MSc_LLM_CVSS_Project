# Run Single Inference Validation v1

## Objective

To validate the integrated inference pipeline before scaling to multi-record execution.

Unlike the provider-specific validation scripts, which tested OpenAI, Gemini, and Ollama independently, this validation tested a unified execution pipeline capable of running all selected providers and prompt conditions within a single script.

The purpose of this stage was to confirm that the production inference architecture functions correctly before scaling to larger datasets.

---

## Validation Scope

The validation was performed using:

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

## Validation Workflow

The integrated pipeline executes the following sequence:

```text
Dataset Record
        ↓
Prompt Rendering
        ↓
Provider Inference
        ↓
Raw Response Capture
        ↓
Parser Execution
        ↓
CVSS Validation
        ↓
Results Storage
```

This workflow mirrors the process that will later be used during pilot and main experimental execution.

---

## Output Artefacts

The integrated pipeline preserves evidence at multiple stages of execution.

### Raw Response File

Example:

```text
R001_conventional_raw.txt
```

Purpose:

* Stores the exact text returned by the model
* Preserves the original model output without modification
* Serves as an audit trail for parser verification

Represents:

```text
What the model said
```

---

### API Response File

Example:

```text
R001_conventional_api_response.json
```

Purpose:

* Stores the complete provider response
* Preserves provider metadata
* Supports future auditing, token analysis, and troubleshooting

Represents:

```text
What the provider returned
```

---

### Parsed Output File

Example:

```text
R001_conventional_parsed.json
```

Purpose:

* Stores parser output
* Stores extracted CVSS metrics
* Stores validation results
* Stores vector-score consistency calculations

Represents:

```text
What the experiment understood
```

---

### Consolidated Results Table

File:

```text
run_single_inference_record1_results.xlsx
```

Purpose:

* Stores one row per inference run
* Aggregates all providers and prompt conditions
* Provides an analysis-ready dataset

Represents:

```text
What will be analysed statistically
```

---

## Results Storage Structure

Outputs were saved under:

```text
results/test_runs/run_single_inference_record1/
```

Structure:

```text
run_single_inference_record1/
│
├── raw_responses/
│   ├── ollama/
│   ├── openai/
│   └── gemini/
│
└── run_single_inference_record1_results.xlsx
```

---

## Validation Results

### OpenAI

| Condition    | Parse Success | Compliance | Predicted Score | Calculated Score | Consistent |
| ------------ | ------------- | ---------- | --------------- | ---------------- | ---------- |
| conventional | True          | strict     | 7.2             | 7.2              | True       |
| structured   | True          | strict     | 7.2             | 7.2              | True       |

---

### Gemini

| Condition    | Parse Success | Compliance | Predicted Score | Calculated Score | Consistent |
| ------------ | ------------- | ---------- | --------------- | ---------------- | ---------- |
| conventional | True          | fenced     | 9.1             | 9.1              | True       |
| structured   | True          | fenced     | 9.1             | 9.1              | True       |

---

### Ollama

| Condition    | Parse Success | Compliance | Predicted Score | Calculated Score | Consistent |
| ------------ | ------------- | ---------- | --------------- | ---------------- | ---------- |
| conventional | True          | strict     | 9.8             | 8.8              | False      |
| structured   | True          | fenced     | 9.0             | 8.1              | False      |

---

## Key Observations

### Integrated Pipeline Success

All six inference runs completed successfully.

The integrated pipeline successfully:

* Loaded the dataset
* Rendered prompts
* Executed all three providers
* Parsed all responses
* Calculated CVSS scores
* Saved all artefacts
* Generated a consolidated results table

---

### Reproducibility

The integrated pipeline reproduced the same outputs previously obtained from the provider-specific validation scripts.

This confirms that the transition from individual provider scripts to a unified execution pipeline did not alter model behaviour.

---

### Cross-Provider Differences

The validation also reproduced previously observed differences between providers.

OpenAI and Gemini produced internally consistent vectors and scores.

Ollama produced parseable outputs but reported base scores that did not match the scores recalculated from the predicted vectors.

The models also disagreed on several CVSS metrics, demonstrating that the pipeline can successfully capture cross-provider variation.

---

## Conclusion

The run_single_inference validation confirms that the unified execution architecture is operational and capable of executing all selected providers and prompt conditions within a single workflow.

This stage provides evidence that the experimental infrastructure is functioning correctly before scaling beyond a single record.

The next phase is resilience validation through retry handling, followed by execution on a 5-record test set prior to the 50-record pilot run.
