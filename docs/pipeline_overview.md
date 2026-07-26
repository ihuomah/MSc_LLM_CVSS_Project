# Experimental Pipeline Overview

## Purpose

This document explains the end-to-end experimental pipeline for evaluating the reliability of LLM-generated CVSS v3.1 scoring under two prompt conditions:

1. Conventional natural-language prompting
2. PDL-style declarative structured prompting

The aim is to evaluate accuracy, consistency, output discipline, vector-score consistency, EPSS relationship, and failure modes.

---

## High-Level Pipeline

```text
Dataset
   ↓
Prompt Template
   ↓
Model Inference
   ↓
Raw Response Storage
   ↓
Parser
   ↓
CVSS Library Recalculation
   ↓
Results Table
   ↓
Analysis

For repeatability analysis, the inference stage is repeated:

Dataset
   ↓
Prompt Template
   ↓
Model Inference
      ↳ repeated N times where required
   ↓
Raw Response Storage
   ↓
Parser
   ↓
CVSS Library Recalculation
   ↓
Results Table
   ↓
Analysis

Each output row must include:

record_id
model
prompt_condition
run_index
Stage 1: Dataset

The dataset provides the vulnerability descriptions used as model input and the official CVSS values used as ground truth.

The models only receive the sanitised vulnerability description.

They do not receive:

CVE ID
vendor/product identity
official CVSS vector
official CVSS base score
official severity
EPSS score

The official CVSS and EPSS values are used later for evaluation.

Stage 2: Prompt Templates

Two frozen prompt templates are used.

Condition 1: Conventional Prompt

A natural-language instruction prompt asking the model to analyse the vulnerability description and return CVSS v3.1 metrics in JSON format.

Condition 2: PDL-Style Declarative Prompt

A structured declarative prompt based on IBM Prompt Declaration Language concepts. The model receives a task specification organised into sections such as:

TASK
ROLE
INPUT
METRICS
CONSTRAINTS
OUTPUT
REQUIREMENTS

Both conditions use:

same CVSS metrics
same valid values
same JSON keys
same anti-memorisation constraints
same output requirements

The only intended difference is prompt structure.

Stage 3: Model Inference

Each model receives one rendered prompt containing one vulnerability description.

Models:

ChatGPT
Gemini
llama3:8b via Ollama

For each inference, the system records:

record_id
model
prompt_condition
run_index
timestamp
model_identifier
raw_response_path

The pilot dataset is run once to validate the pipeline.

The main dataset may use repeated runs to measure stability and consistency.

Stage 4: Raw Response Storage

Raw model responses are immutable evidence.

Every model response must be saved exactly as returned before parsing.

This includes:

clean JSON
markdown-fenced JSON
explanatory text
malformed output
any other unexpected behaviour

Raw responses should not be edited manually.

Suggested storage pattern:

results/raw/
  record001_chatgpt_condition1_run1.txt
  record001_chatgpt_condition2_run1.txt
  record001_gemini_condition1_run1.txt
  record001_gemini_condition2_run1.txt
  record001_ollama_condition1_run1.txt
  record001_ollama_condition2_run1.txt

If parser logic changes later, results should be regenerated from saved raw responses, not by rerunning the models.

Stage 5: Parser

The parser converts raw model responses into structured fields.

It extracts:

attack_vector
attack_complexity
privileges_required
user_interaction
scope
confidentiality_impact
integrity_impact
availability_impact
vector_string
base_score

It also records parse and compliance information.

Compliance Categories
Category	Meaning
strict	The response is exactly one JSON object with no extra text
fenced	The response is only markdown-fenced JSON
embedded	Valid JSON appears inside surrounding text or explanation
invalid	No valid JSON object can be extracted

The parser is strict for compliance logging but tolerant for data extraction.

Stage 6: CVSS Library Recalculation

The model returns both:

vector_string
base_score

The CVSS library independently recalculates the canonical base score from the model-generated vector string.

This allows the experiment to detect vector-score inconsistency.

Example:

Model vector:
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N

Model reported score:
0.0

Canonical score from vector:
7.5

This is classified as an internal vector-score inconsistency.

This separates:

metric reasoning failure
arithmetic/scoring failure
output-format failure

The project uses the cvss Python library version 3.6.

Stage 7: Results Table

Each parsed model response becomes one row in the results table.

Recommended columns:

record_id
model
prompt_condition
run_index
raw_response_path
compliance_category
parse_success
all_keys_present
valid_metric_values
attack_vector
attack_complexity
privileges_required
user_interaction
scope
confidentiality_impact
integrity_impact
availability_impact
vector_string
model_reported_base_score
canonical_score_from_model_vector
vector_score_consistency
official_cvss_vector
official_base_score
official_severity
epss_score
published_date

Additional columns may be added later for:

per_metric_match
exact_vector_match
base_score_error
severity_band_match
Stage 8: Analysis

The results table supports the dissertation research questions.

RQ1: How LLMs interpret CVE descriptions

Analyse model-generated CVSS metrics across:

models
prompt conditions
vulnerability records

This shows how different models interpret the same vulnerability description.

RQ2: Accuracy and consistency against ground truth

Compare model outputs against official CVSS values:

model metrics vs official metrics
model vector vs official vector
model base score vs official base score
model severity vs official severity

This measures CVSS accuracy and consistency.

RQ3: Relationship with EPSS

EPSS is not a severity score.

EPSS estimates probability of exploitation in the wild, while CVSS estimates intrinsic vulnerability severity.

The analysis should therefore examine whether model-generated CVSS scores preserve the relationship with EPSS compared with official CVSS scores.

This may include:

official CVSS score ↔ EPSS probability
model-generated CVSS score ↔ EPSS probability

The goal is to determine whether model-generated CVSS scores retain, weaken, or distort the prioritisation signal when compared with EPSS.

RQ4: Effect of structured prompting

Compare Condition 1 and Condition 2 across:

schema compliance
invalid output rate
per-metric agreement
exact vector match
base score error
vector-score consistency
repeated-run consistency

This evaluates whether structured prompt improves reliability and stability compared with the conventional prompt.

RQ5: Failure modes

Identify patterns that make LLM-generated vulnerability scores unreliable.

Examples:

Metric Reasoning Failure
Official AV:N
Model AV:L
Arithmetic / Vector-Score Failure
Model vector implies 7.5
Model reports 0.0
Output Discipline Failure
Model returns explanation and fenced JSON instead of bare JSON
Instability Failure
Same model + same prompt + same CVE produces different outputs across repeated runs
Repeatability Design

For the pilot dataset:

run_index = 1

The pilot validates the pipeline end-to-end.

For the main experiment, repeated runs may be performed to measure stability.

Example:

record_id: R001
model: ChatGPT
condition: Condition 1
run_index: 1, 2, 3

Repeated-run consistency can then be measured by comparing outputs within the same:

record_id + model + prompt_condition

group.

Project Principles
1. Raw responses are immutable evidence

Never manually edit raw model responses.

2. Prompt changes are restricted

Allowed:

parseability fixes
methodological fairness fixes

Not allowed:

accuracy fixes
model-specific behaviour fixes
changes made because a model disagreed with NVD
3. Parser tolerance must be logged

The parser may extract JSON from imperfect responses, but it must record whether extraction was strict, fenced, embedded, or invalid.

4. Accuracy and reliability are separate

A model may be accurate but unstable.

A model may produce valid metrics but an incorrect score.

A model may produce useful JSON but fail strict schema compliance.

These must be analysed separately.

Current Status

Completed:

Dataset frozen
Prompt templates frozen
Prompt sanity tests completed
Parser v1 built and validated
CVSS library installed and validated

Next artefact:

Inference script

The inference script will connect the frozen dataset, frozen prompts, models, parser, and CVSS library into one reproducible results-generation pipeline.


This document now becomes your reference point before we write the inference script.