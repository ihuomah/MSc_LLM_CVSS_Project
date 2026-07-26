import requests
import time
from pathlib import Path
from datetime import datetime, timezone


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:8b"

OUTPUT_DIR = Path("results/test_runs/connectivity/ollama")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "ollama_connection_test.txt"


def main():
    prompt = "Return exactly this word: OK"

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "seed": 42,
        },
    }

    print("Testing Ollama connection...")
    print(f"Model: {MODEL}")

    start = time.time()
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    end = time.time()

    response.raise_for_status()

    data = response.json()
    raw_response = data.get("response", "")

    latency_ms = int((end - start) * 1000)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    OUTPUT_FILE.write_text(raw_response, encoding="utf-8")

    print("=" * 80)
    print("Ollama connection test completed")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Latency ms: {latency_ms}")
    print(f"Raw response: {raw_response}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()