import json
import sys
import time
import os
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv
from google import genai
from cvss import CVSS3

sys.path.insert(0, str(Path(__file__).parent))

from parse_model_response import parse_model_response
from config import GEMINI_MODEL, TEMPERATURE, SEED


load_dotenv()

DATASET = Path("data/frozen_pilot_v2/datasets/pilot_inference_input_v2.xlsx")

CONVENTIONAL_PROMPT = Path(
    "prompts/frozen_prompt_v1/condition1_conventional_prompt_v1.txt"
)
STRUCTURED_PROMPT = Path(
    "prompts/frozen_prompt_v1/condition2_structured_prompt_v1.txt"
)

OUTPUT_BASE = Path("results/test_runs/cvss_record_1/gemini")


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


def call_gemini(prompt: str) -> tuple[str, int, dict]:
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

    return raw_response, latency_ms, full_api_response


def calculate_vector_score(vector: str):
    try:
        return CVSS3(vector).scores()[0]
    except Exception:
        return None


def run_test(record_id: int, condition: str, prompt_path: Path):
    print("=" * 80)
    print(f"Testing provider=gemini, record_id={record_id}, condition={condition}")
    print(f"Model: {GEMINI_MODEL}")

    description = load_description(record_id)
    prompt = render_prompt(prompt_path, description)

    raw_response, latency_ms, full_api_response = call_gemini(prompt)

    output_dir = OUTPUT_BASE / condition
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_file = output_dir / f"R{record_id:03d}_{condition}_raw.txt"
    api_file = output_dir / f"R{record_id:03d}_{condition}_api_response.json"
    parsed_file = output_dir / f"R{record_id:03d}_{condition}_parsed.json"

    raw_file.write_text(raw_response, encoding="utf-8")
    api_file.write_text(json.dumps(full_api_response, indent=2), encoding="utf-8")

    parsed = parse_model_response(raw_response)

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

    output = {
        "record_id": record_id,
        "model_name": "gemini",
        "model_snapshot": GEMINI_MODEL,
        "prompt_condition": condition,
        "run_index": 1,
        "timestamp": timestamp,
        "inference_latency_ms": latency_ms,
        "provider_fingerprint": None,
        "raw_response_file": str(raw_file),
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
        "parser_error": None,
    }

    parsed_file.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"Raw response saved to: {raw_file}")
    print(f"API response saved to: {api_file}")
    print(f"Parsed output saved to: {parsed_file}")
    print(f"Latency ms: {latency_ms}")
    print(f"Parse success: {output['parse_success']}")
    print(f"Compliance: {output['compliance_category']}")
    print(f"All keys present: {output['all_keys_present']}")
    print(f"Valid metric values: {output['valid_metric_values']}")
    print(f"Predicted vector: {predicted_vector}")
    print(f"Predicted base score: {predicted_base_score}")
    print(f"Calculated base score: {calculated_base_score}")
    print(f"Vector-score delta: {vector_score_delta}")
    print(f"Vector-score consistent: {vector_score_consistent}")


def main():
    record_id = 1

    run_test(record_id, "conventional", CONVENTIONAL_PROMPT)
    run_test(record_id, "structured", STRUCTURED_PROMPT)


if __name__ == "__main__":
    main()