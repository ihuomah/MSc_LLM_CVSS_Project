# API Execution Plan v1

## Purpose

This document defines how API-based execution will be handled for the LLM-CVSS experiment.

The project will use API automation for experimental inference and dataset fetching to improve reproducibility, reduce manual copy-paste errors, and preserve a clean audit trail.

---

## API-Based Components

The project may use the following API-based components:

1. OpenAI API
   Used for ChatGPT model inference.

2. Gemini API
   Used for Gemini model inference.

3. Ollama local API
   Used for local llama3:8b inference.

4. NVD API
   Used for fetching CVE records for the main 1000-CVE dataset.

---

## API Key Management Rule

API keys must not be written directly into Python scripts, notebooks, markdown files, screenshots, prompts, or chat messages.

API keys will be stored locally in a `.env` file at the project root.

The `.env` file must not be committed to Git or shared.

---

## Local `.env` File

The project root should contain:

```text
.env
```

Example structure:

```text
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
NVD_API_KEY=your_nvd_api_key_here
```

The real keys must remain local and must not be pasted into project notes or shared documents.

---

## `.gitignore` Rule

The project root must include a `.gitignore` file containing:

```text
.env
```

This prevents accidental exposure of local API credentials if the project is pushed to GitHub or another repository.

---

## Loading API Keys in Scripts

Python scripts should load API keys from environment variables.

Example:

```python
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
nvd_api_key = os.getenv("NVD_API_KEY")
```

Scripts should fail safely if a required key is missing.

Example:

```python
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Check your .env file.")
```

---

## NVD API Key Handling

The existing NVD fetch script should be updated, if necessary, so that it reads the NVD API key from:

```text
NVD_API_KEY
```

rather than storing the key directly inside the script.

The frozen pilot dataset and frozen pilot scripts remain unchanged for audit purposes.

For the main 1000-CVE dataset, a new or updated fetch script should use the local `.env` key-loading pattern.

---

## Model Execution Plan

Experimental inference will use API or local endpoint automation:

| Model family     | Execution route  |
| ---------------- | ---------------- |
| OpenAI / ChatGPT | OpenAI API       |
| Gemini           | Gemini API       |
| llama3:8b        | Ollama local API |

Manual web-interface use was limited to early prompt sanity checks only.

For the actual pilot and main experiments, inference will be automated.

---

## Execution Stages

The experiment will proceed in stages:

1. One-record API connectivity test
2. One-record full inference test
3. Five-record batch test
4. Full 50-CVE pilot run
5. Main dataset run

This staged approach reduces risk and allows errors in API access, prompt rendering, parsing, raw response storage, or results writing to be detected early.

---

## Raw Response Rule

Every model response must be saved exactly as returned before parsing.

Raw responses are immutable evidence.

If parser logic changes later, saved raw responses should be re-parsed rather than re-running the models.

---

## Cost and Limits

Before running large batches, the project should estimate approximate token usage and cost.

The pilot run is expected to involve:

```text
50 CVEs × 3 models × 2 prompt conditions × 1 run = 300 inferences
```

The main experiment may involve:

```text
1000 CVEs × 3 models × 2 prompt conditions × run_count
```

The run count should be selected based on research value, cost, API limits, and timeline.

---

## Prompt Condition Labels

The accepted prompt condition labels are:

```text
conventional
structured
```

The label `pdl` should not be used for experimental prompt condition naming, because Condition 2 is a structured prompt submitted as plain text rather than a PDL-runtime execution.

---

## Status

API execution strategy: proposed and ready for implementation.
