# Model Execution Plan v1

## Purpose

This document defines how model inference will be executed for the LLM-CVSS experiment.

The aim is to run all experimental inference through automated APIs or local endpoints, store raw responses, parse outputs, and generate raw results tables for later analysis.

---

## Model Execution Routes

| Model        | Execution Route  |
| ------------ | ---------------- |
| OpenAI model | OpenAI API       |
| Gemini model | Gemini API       |
| llama3:8b    | Ollama local API |

Manual web-interface testing was used only for early prompt sanity checks. Experimental inference will be automated.

---

## Prompt Conditions

The accepted prompt condition labels are:

```text
conventional
structured
```

The label `pdl` should not be used as a prompt condition value.

---

## Pilot Scope

The pilot experiment will use:

```text
50 CVEs × 3 models × 2 prompt conditions × 1 run = 300 inferences
```

The pilot validates the full pipeline.

---

## Model Snapshot Locking

To support reproducibility, model identifiers must be locked before experimental execution begins.

Once a pilot or main run starts, the model identifier must not change.

### Planned Models

| Provider | Model Snapshot |
| -------- | -------------- |
| OpenAI   | TO_BE_LOCKED   |
| Gemini   | TO_BE_LOCKED   |
| Ollama   | llama3:8b      |

The OpenAI and Gemini model identifiers will be recorded immediately before the first API-based inference test.

The exact model identifier used for each inference must also be stored in the `model_snapshot` column of the raw results table.

Model changes during an active run are not permitted.


## Execution Ladder

Stage 1:

```text
1 record × 3 models × 2 conditions = 6 inferences
```

Stage 2:

```text
5 records × 3 models × 2 conditions = 30 inferences
```

Stage 3:

```text
50 records × 3 models × 2 conditions = 300 inferences
```

Each stage must pass before moving to the next.

---

## Results Directory Structure

```text
results/
├──pilot
|   ├── raw_responses/
│   ├── openai/
│   │   ├── standard/
│   │   │   └── run_001/
│   │   └── structured/
│   │       └── run_001/
│   ├── gemini/
│   │   ├── standard/
│   │   │   └── run_001/
│   │   └── structured/
│   │       └── run_001/
│   └── ollama/
│       ├── standard/
│       │   └── run_001/
│       └── structured/
│           └── run_001/
    ├── raw_results/
    ├── analysis/
    └── logs/
├──full  
├─test_runs
    connectivity/
        ollama/
        openai/
        gemini/
    cvss_record_1/
        ollama/
            conventional/
            structured/
        openai/
            conventional/
            structured/
        gemini/
            conventional/
            structured/  
```

---

## Raw Response File Naming

Raw response files should use:

```text
R001_run001.txt
R002_run001.txt
...
```

Provider and prompt condition are represented by the folder path.

---

## Logs

The logs folder should contain:

```text
inference_log.csv
api_errors.log
cost_tracking.csv
```

---

## API Key Management

API keys are stored locally in:

```text
.env
```

The `.env` file must not be committed to Git or shared.

Scripts should load keys using environment variables.

---

## API Parameters

Default deterministic settings:

```text
temperature = 0
seed = 42 where supported
```

Model identifiers must be recorded in the raw results table.

---

## Failure Handling

If one inference fails, the full run should not crash.

The failed call should be logged, and the results row should record:

```text
parse_success = False
compliance_category = invalid
```

Errors should be written to:

```text
results/logs/api_errors.log
```

---

## Raw Response Rule

Raw responses are immutable evidence.

Each response must be saved exactly as returned before parsing.

If parser logic changes later, saved raw responses should be re-parsed rather than re-running the models.

---

## Status

Execution plan status: v1 ready for API connectivity testing.
