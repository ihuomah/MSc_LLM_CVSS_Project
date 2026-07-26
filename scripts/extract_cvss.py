import re

response_text = """
Here is the estimated CVSS v3.1 vector and base score based on the provided vulnerability description:
AV: N
AC: H
PR: L
UI: R
S: U
C: H
I: H
A: N
cvss_vector: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N
base_score: 9.8

Note that the scoring is based only on the provided vulnerability description.
"""

# STEP 1 — Remove markdown formatting
cleaned = re.sub(r"```", "", response_text)

# STEP 2 — Extract CVSS vector
vector_match = re.search(r"CVSS:3\.1/[A-Z:/]+", cleaned)

# STEP 3 — Extract base score
score_match = re.search(r"base_score:\s*([0-9.]+)", cleaned)

print("\n===== EXTRACTED RESULTS =====\n")

if vector_match:
    print("Vector:")
    print(vector_match.group(0))
else:
    print("No vector found.")

print()

if score_match:
    print("Base Score:")
    print(score_match.group(1))
else:
    print("No base score found.")