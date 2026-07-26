from dotenv import load_dotenv
from google import genai
from pathlib import Path
from datetime import datetime, timezone
import time
import os

load_dotenv()

MODEL = "gemini-2.5-pro"

OUTPUT_DIR = Path("results/test_runs/connectivity/gemini")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "gemini_connection_test.txt"


def main():
    api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    prompt = "Return exactly this word: OK"

    print("Testing Gemini connection...")
    print(f"Model: {MODEL}")

    start = time.time()

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    end = time.time()

    raw_response = response.text.strip()

    latency_ms = int((end - start) * 1000)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    OUTPUT_FILE.write_text(raw_response, encoding="utf-8")

    print("=" * 80)
    print("Gemini connection test completed")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Latency ms: {latency_ms}")
    print(f"Raw response: {raw_response}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()