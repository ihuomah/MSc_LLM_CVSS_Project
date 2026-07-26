import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

test_description = """
A vulnerability in Software Y allows a remote unauthenticated attacker
to execute arbitrary code by sending specially crafted network requests.
"""

with open("prompts/cvss_pdl_prompt.pdl", "r", encoding="utf-8") as f:
    prompt_template = f.read()

final_prompt = prompt_template.replace(
    "{{ vulnerability_description }}",
    test_description
)

payload = {
    "model": "llama3:8b",
    "prompt": final_prompt,
    "stream": False
}

response = requests.post(OLLAMA_URL, json=payload)

result = response.json()

print("\n===== PDL MODEL RESPONSE =====\n")
print(result["response"])