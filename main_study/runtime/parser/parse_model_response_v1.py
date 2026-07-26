import json
import re
from typing import Dict, Any, Tuple, Optional


EXPECTED_KEYS = [
    "attack_vector",
    "attack_complexity",
    "privileges_required",
    "user_interaction",
    "scope",
    "confidentiality_impact",
    "integrity_impact",
    "availability_impact",
    "vector_string",
    "base_score",
]

VALID_VALUES = {
    "attack_vector": {"N", "A", "L", "P"},
    "attack_complexity": {"L", "H"},
    "privileges_required": {"N", "L", "H"},
    "user_interaction": {"N", "R"},
    "scope": {"U", "C"},
    "confidentiality_impact": {"N", "L", "H"},
    "integrity_impact": {"N", "L", "H"},
    "availability_impact": {"N", "L", "H"},
}


def classify_and_extract_json(raw_response: str) -> Tuple[str, Optional[str]]:
    """
    Classifies model output and extracts JSON if possible.

    Returns:
        compliance_category: strict, fenced, embedded, or invalid
        json_text: extracted JSON string or None
    """

    raw_response = raw_response.strip()

    # 1. Strict: entire response is valid JSON
    try:
        json.loads(raw_response)
        return "strict", raw_response
    except json.JSONDecodeError:
        pass

    # 2. Fenced: JSON inside markdown code fence
    fence_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        raw_response,
        re.DOTALL | re.IGNORECASE,
    )

    if fence_match:
        json_text = fence_match.group(1).strip()
        try:
            json.loads(json_text)
            return "fenced", json_text
        except json.JSONDecodeError:
            pass

    # 3. Embedded: find first JSON-like object
    start = raw_response.find("{")
    end = raw_response.rfind("}")

    if start != -1 and end != -1 and end > start:
        json_text = raw_response[start : end + 1].strip()
        try:
            json.loads(json_text)
            return "embedded", json_text
        except json.JSONDecodeError:
            pass

    # 4. Invalid
    return "invalid", None


def validate_response(parsed_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates expected keys, metric values, vector string, and base score.
    """

    result = {
        "all_keys_present": True,
        "valid_metric_values": True,
        "base_score_numeric": True,
        "vector_string_present": True,
        "missing_keys": [],
        "invalid_values": {},
    }

    for key in EXPECTED_KEYS:
        if key not in parsed_json:
            result["all_keys_present"] = False
            result["missing_keys"].append(key)

    for key, allowed in VALID_VALUES.items():
        if key in parsed_json:
            value = parsed_json[key]
            if value not in allowed:
                result["valid_metric_values"] = False
                result["invalid_values"][key] = value

    if "base_score" in parsed_json:
        if not isinstance(parsed_json["base_score"], (int, float)):
            result["base_score_numeric"] = False

    if "vector_string" in parsed_json:
        vector = parsed_json["vector_string"]
        if not isinstance(vector, str) or not vector.startswith("CVSS:3.1/"):
            result["vector_string_present"] = False

    return result


def parse_model_response(raw_response: str) -> Dict[str, Any]:
    """
    Main parser function.
    """

    compliance_category, json_text = classify_and_extract_json(raw_response)

    output = {
        "compliance_category": compliance_category,
        "parse_success": False,
        "parsed_json": None,
        "validation": None,
    }

    if json_text is None:
        return output

    try:
        parsed_json = json.loads(json_text)
        output["parse_success"] = True
        output["parsed_json"] = parsed_json
        output["validation"] = validate_response(parsed_json)
    except json.JSONDecodeError:
        pass

    return output