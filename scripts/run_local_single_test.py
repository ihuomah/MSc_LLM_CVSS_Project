import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

VALID_METRICS = {
    "AV": ["N", "A", "L", "P"],
    "AC": ["L", "H"],
    "PR": ["N", "L", "H"],
    "UI": ["N", "R"],
    "S": ["U", "C"],
    "C": ["H", "L", "N"],
    "I": ["H", "L", "N"],
    "A": ["H", "L", "N"],
}

description = """
A vulnerability in Software Y allows a remote unauthenticated attacker
to execute arbitrary code by sending specially crafted network requests.
"""

with open("prompts/cvss_pdl_prompt.pdl", "r", encoding="utf-8") as file:
    prompt_template = file.read()

prompt = prompt_template.replace("{{ vulnerability_description }}", description)

payload = {
    "model": "llama3:8b",
    "prompt": prompt,
    "stream": False
}

response = requests.post(OLLAMA_URL, json=payload)
raw_output = response.json()["response"]

cleaned_output = re.sub(r"```", "", raw_output)

vector_match = re.search(r"CVSS:3\.1/[A-Z:/]+", cleaned_output)
score_match = re.search(r"base_score:\s*([0-9.]+)", cleaned_output, re.IGNORECASE)

vector = vector_match.group(0) if vector_match else None
base_score = score_match.group(1) if score_match else None

errors = []

if vector:
    metrics = vector.replace("CVSS:3.1/", "").split("/")
    detected_keys = set()

    for metric in metrics:
        if ":" not in metric:
            errors.append(f"Malformed metric: {metric}")
            continue

        key, value = metric.split(":")
        detected_keys.add(key)

        if key not in VALID_METRICS:
            errors.append(f"Invalid metric key: {key}")
        elif value not in VALID_METRICS[key]:
            errors.append(f"Invalid value '{value}' for metric '{key}'")

    missing = set(VALID_METRICS.keys()) - detected_keys
    for key in missing:
        errors.append(f"Missing metric: {key}")
else:
    errors.append("No CVSS v3.1 vector found.")

print("\n===== RAW MODEL OUTPUT =====\n")
print(raw_output)

print("\n===== EXTRACTED OUTPUT =====\n")
print("Vector:", vector)
print("Base Score:", base_score)

print("\n===== VALIDATION RESULT =====\n")
if errors:
    print("Invalid CVSS output:")
    for error in errors:
        print("-", error)
else:
    print("Valid CVSS v3.1 output.")