# Model Registry v1

## Purpose

This document records the models selected for the LLM-CVSS experiment.

It is used to keep model names, execution routes, and deterministic settings consistent across the pilot and main experiment.

---

## Model Registry

| Provider | Model Name     | Model Snapshot / Identifier | Execution Route  | Temperature | Seed | Status |
| -------- | -------------- | --------------------------- | ---------------- | ----------- | ---- | ------ |
| OpenAI   | gpt-5.5        | gpt-5.5                     | OpenAI API       | 0           | 42   | Locked |
| Gemini   | gemini-2.5-pro | gemini-2.5-pro              | Gemini API       | 0           | 42   | Locked |
| Ollama   | llama3:8b      | llama3:8b                   | Ollama local API | 0           | 42   | Locked |

---

## Provider Selection Rationale

Three LLM deployment configurations were selected for evaluation:

* OpenAI gpt-5.5 (commercial cloud flagship)
* Google Gemini 2.5 Pro (commercial cloud flagship)
* Meta Llama 3 8B executed locally through Ollama (local open-source deployment)

The commercial providers were represented using their flagship models to minimise capability-tier bias during comparison. The local model was selected to represent an on-premises deployment option that can operate without external API access.

These three configurations provide a comparison across commercial cloud-hosted and locally deployed LLM environments while remaining representative of deployment options available to practitioners.

---

## Prompt Conditions

The accepted prompt condition labels are:

```text
conventional
structured
```

---

## Model Locking Rule

Once pilot or main experiment execution begins, the model identifiers must not change during that run.

If a provider deprecates or changes a model during execution, the run must be paused and documented before continuing.

---

## Connectivity Validation Status

The following providers have successfully passed connectivity validation:

* OpenAI API
* Google Gemini API
* Ollama Local API

Connectivity validation confirms:

* Environment variable loading
* Authentication
* Network connectivity
* Response retrieval
* File output handling

Connectivity validation does not constitute final model selection for experimental execution.

---

## Notes

The local model used in this study is `llama3:8b`, executed through Ollama.

OpenAI and Gemini connectivity testing was successfully completed on 2026-06-10.

Final OpenAI and Gemini model identifiers will be locked after record_id=1 CVSS pipeline validation and before pilot execution begins.

Once locked, model identifiers will remain unchanged throughout a given experimental run.

## Notes update

OpenAI, Gemini, and Ollama connectivity validation was successfully completed on 2026-06-10.

The models listed in this registry are locked for pilot and main experimental execution.

Any model change after this point must be documented and justified before further experimental results are collected.
