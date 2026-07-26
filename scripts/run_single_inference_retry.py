import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from cvss import CVSS3

sys.path.insert(0, str(Path(__file__).parent))

from parse_model_response import parse_model_response
from config import OPENAI_MODEL, GEMINI_MODEL, OLLAMA_MODEL, TEMPERATURE, SEED


load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"

DATASET = Path("data/frozen_pilot_v2/datasets/pilot_inference_input_v2.xlsx")

CONVENTIONAL_PROMPT = Path(
    "prompts/frozen_prompt_v1/condition1_conventional_prompt_v1.txt"
)
STRUCTURED_PROMPT = Path(
    "prompts/frozen_prompt_v1/condition2_structured_prompt_v1.txt"
)

OUTPUT_BASE = Path("results/test_runs/run_single_inference_retry_record1")
RAW_BASE = OUTPUT_BASE / "raw_responses"
RESULTS_FILE = OUTPUT_BASE / "run_single_inference_retry_record1_results.xlsx"

MAX_RETRIES = 5
RETRY_WAIT_SECONDS = [5, 10, 20, 30, 60]


def load_description(record_id: int) -> str:
    df = pd.read_excel(DATASET)
    row = df.loc[df["record_id"] == record_id]

    if row.empty:
        raise ValueError(f"record_id {record_id} not found in dataset")

    description = row.iloc[0]["description_for_model"]

    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"description_for_model is empty for record_id {record_id}")

    return description


def render_prompt(prompt_path: Path, description: str) -> str:
    template = prompt_path.read_text(encoding="utf-8")

    if "{DESCRIPTION}" not in template:
        raise ValueError(
            f"{prompt_path} does not contain the {{DESCRIPTION}} placeholder"
        )

    return template.replace("{DESCRIPTION}", description)


def call_ollama_once(prompt: str):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "seed": SEED,
        },
    }

    start = time.time()
    response = requests.post(OLLAMA_URL, json=payload, timeout=180)
    end = time.time()

    response.raise_for_status()

    data = response.json()
    raw_response = data.get("response", "")
    latency_ms = int((end - start) * 1000)

    return raw_response, latency_ms, data, OLLAMA_MODEL


def call_openai_once(prompt: str):
    client = OpenAI()

    start = time.time()

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt,
    )

    end = time.time()

    raw_response = response.output_text.strip()
    latency_ms = int((end - start) * 1000)
    full_api_response = response.model_dump(mode="json")

    return raw_response, latency_ms, full_api_response, OPENAI_MODEL


def call_gemini_once(prompt: str):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    start = time.time()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    end = time.time()

    raw_response = response.text.strip()
    latency_ms = int((end - start) * 1000)
    full_api_response = response.model_dump(mode="json")

    return raw_response, latency_ms, full_api_response, GEMINI_MODEL


def call_provider_with_retry(provider: str, prompt: str):
    total_retry_wait_ms = 0
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            if provider == "ollama":
                result = call_ollama_once(prompt)
            elif provider == "openai":
                result = call_openai_once(prompt)
            elif provider == "gemini":
                result = call_gemini_once(prompt)
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            retry_count = attempt

            return {
                "success": True,
                "raw_response": result[0],
                "latency_ms": result[1],
                "full_api_response": result[2],
                "model_snapshot": result[3],
                "retry_count": retry_count,
                "total_retry_wait_ms": total_retry_wait_ms,
                "error_type": None,
                "error_message": None,
            }

        except Exception as e:
            last_error = e

            if attempt >= MAX_RETRIES:
                break

            wait_seconds = RETRY_WAIT_SECONDS[min(attempt, len(RETRY_WAIT_SECONDS) - 1)]
            total_retry_wait_ms += wait_seconds * 1000

            print(
                f"Retryable error for provider={provider}. "
                f"Attempt {attempt + 1}/{MAX_RETRIES}. "
                f"Waiting {wait_seconds}s. Error: {type(e).__name__}: {e}"
            )

            time.sleep(wait_seconds)

    return {
        "success": False,
        "raw_response": "",
        "latency_ms": None,
        "full_api_response": {
            "error": str(last_error),
            "error_type": type(last_error).__name__,
        },
        "model_snapshot": (
            OLLAMA_MODEL
            if provider == "ollama"
            else OPENAI_MODEL
            if provider == "openai"
            else GEMINI_MODEL
        ),
        "retry_count": MAX_RETRIES,
        "total_retry_wait_ms": total_retry_wait_ms,
        "error_type": type(last_error).__name__,
        "error_message": str(last_error),
    }


def calculate_vector_score(vector: str):
    try:
        return CVSS3(vector).scores()[0]
    except Exception:
        return None


def run_one(record_id: int, provider: str, condition: str, prompt_path: Path):
    print("=" * 80)
    print(f"Running record_id={record_id}, provider={provider}, condition={condition}")

    description = load_description(record_id)
    prompt = render_prompt(prompt_path, description)

    provider_result = call_provider_with_retry(provider, prompt)

    raw_response = provider_result["raw_response"]
    latency_ms = provider_result["latency_ms"]
    full_api_response = provider_result["full_api_response"]
    model_snapshot = provider_result["model_snapshot"]

    output_dir = RAW_BASE / provider / condition
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_file = output_dir / f"R{record_id:03d}_{condition}_raw.txt"
    api_file = output_dir / f"R{record_id:03d}_{condition}_api_response.json"
    parsed_file = output_dir / f"R{record_id:03d}_{condition}_parsed.json"

    raw_file.write_text(raw_response, encoding="utf-8")
    api_file.write_text(json.dumps(full_api_response, indent=2), encoding="utf-8")

    parsed = parse_model_response(raw_response) if provider_result["success"] else {
        "parse_success": False,
        "compliance_category": "api_error",
        "parsed_json": {},
        "validation": {},
    }

    parsed_json = parsed.get("parsed_json") or {}
    validation = parsed.get("validation") or {}

    predicted_vector = parsed_json.get("vector_string")
    predicted_base_score = parsed_json.get("base_score")

    calculated_base_score = None
    vector_score_delta = None
    vector_score_consistent = None

    if predicted_vector and predicted_base_score is not None:
        calculated_base_score = calculate_vector_score(predicted_vector)

        if calculated_base_score is not None:
            vector_score_delta = float(predicted_base_score) - float(calculated_base_score)
            vector_score_consistent = abs(vector_score_delta) < 0.15

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    result_row = {
        "record_id": record_id,
        "model_name": provider,
        "model_snapshot": model_snapshot,
        "prompt_condition": condition,
        "run_index": 1,
        "timestamp": timestamp,
        "inference_latency_ms": latency_ms,
        "retry_count": provider_result["retry_count"],
        "total_retry_wait_ms": provider_result["total_retry_wait_ms"],
        "error_type": provider_result["error_type"],
        "error_message": provider_result["error_message"],
        "provider_fingerprint": None,
        "raw_response_file": str(raw_file),
        "api_response_file": str(api_file),
        "parsed_output_file": str(parsed_file),
        "parse_success": parsed.get("parse_success"),
        "compliance_category": parsed.get("compliance_category"),
        "all_keys_present": validation.get("all_keys_present"),
        "valid_metric_values": validation.get("valid_metric_values"),
        "base_score_numeric": validation.get("base_score_numeric"),
        "vector_string_present": validation.get("vector_string_present"),
        "attack_vector": parsed_json.get("attack_vector"),
        "attack_complexity": parsed_json.get("attack_complexity"),
        "privileges_required": parsed_json.get("privileges_required"),
        "user_interaction": parsed_json.get("user_interaction"),
        "scope": parsed_json.get("scope"),
        "confidentiality_impact": parsed_json.get("confidentiality_impact"),
        "integrity_impact": parsed_json.get("integrity_impact"),
        "availability_impact": parsed_json.get("availability_impact"),
        "predicted_vector": predicted_vector,
        "predicted_base_score": predicted_base_score,
        "calculated_base_score": calculated_base_score,
        "vector_score_delta": vector_score_delta,
        "vector_score_consistent": vector_score_consistent,
        "parser_error": provider_result["error_message"] if not provider_result["success"] else None,
    }

    parsed_file.write_text(json.dumps(result_row, indent=2), encoding="utf-8")

    print(f"Raw response saved to: {raw_file}")
    print(f"API response saved to: {api_file}")
    print(f"Parsed output saved to: {parsed_file}")
    print(f"Latency ms: {latency_ms}")
    print(f"Retry count: {provider_result['retry_count']}")
    print(f"Total retry wait ms: {provider_result['total_retry_wait_ms']}")
    print(f"Error type: {provider_result['error_type']}")
    print(f"Parse success: {result_row['parse_success']}")
    print(f"Compliance: {result_row['compliance_category']}")
    print(f"Predicted vector: {predicted_vector}")
    print(f"Predicted base score: {predicted_base_score}")
    print(f"Calculated base score: {calculated_base_score}")
    print(f"Vector-score consistent: {vector_score_consistent}")

    return result_row


def main():
    record_id = 1

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

    providers = ["ollama", "openai", "gemini"]

    conditions = [
        ("conventional", CONVENTIONAL_PROMPT),
        ("structured", STRUCTURED_PROMPT),
    ]

    results = []

    for provider in providers:
        for condition, prompt_path in conditions:
            row = run_one(record_id, provider, condition, prompt_path)
            results.append(row)

    df = pd.DataFrame(results)
    df.to_excel(RESULTS_FILE, index=False)

    print("=" * 80)
    print("Single inference retry validation completed")
    print("=" * 80)
    print(f"Rows written: {len(results)}")
    print(f"Results file: {RESULTS_FILE}")


if __name__ == "__main__":
    main()