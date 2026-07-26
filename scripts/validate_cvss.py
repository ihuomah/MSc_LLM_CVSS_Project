import re

response_text = """
CVSS Vector: CVSS:3.1/AV:N/AC:L/Au:N/C:C/I:C/A:C
Base Score: 9.8
"""

valid_metrics = {
    "AV": ["N", "A", "L", "P"],
    "AC": ["L", "H"],
    "PR": ["N", "L", "H"],
    "UI": ["N", "R"],
    "S": ["U", "C"],
    "C": ["H", "L", "N"],
    "I": ["H", "L", "N"],
    "A": ["H", "L", "N"]
}

vector_match = re.search(r"CVSS:3\.1/.*", response_text)

if not vector_match:
    print("No valid CVSS vector found.")
    exit()

vector = vector_match.group(0)

print(f"\nDetected Vector:\n{vector}\n")

metrics = vector.replace("CVSS:3.1/", "").split("/")

errors = []

for metric in metrics:
    try:
        key, value = metric.split(":")
    except ValueError:
        errors.append(f"Malformed metric: {metric}")
        continue

    if key not in valid_metrics:
        errors.append(f"Invalid metric key: {key}")
        continue

    if value not in valid_metrics[key]:
        errors.append(f"Invalid value '{value}' for metric '{key}'")

required_keys = set(valid_metrics.keys())
detected_keys = set([m.split(":")[0] for m in metrics if ":" in m])

missing = required_keys - detected_keys

for item in missing:
    errors.append(f"Missing metric: {item}")

if errors:
    print("Validation Errors Found:\n")

    for err in errors:
        print(f"- {err}")

else:
    print("CVSS vector is valid.")