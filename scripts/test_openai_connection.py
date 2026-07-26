from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from datetime import datetime, timezone
import time

load_dotenv()

MODEL = "gpt-5.5"

OUTPUT_DIR = Path("results/test_runs/connectivity/openai")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "openai_connection_test.txt"


def main():
    client = OpenAI()

    prompt = "Return exactly this word: OK"

    print("Testing OpenAI connection...")
    print(f"Model: {MODEL}")

    start = time.time()

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    end = time.time()

    raw_response = response.output_text.strip()

    latency_ms = int((end - start) * 1000)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    OUTPUT_FILE.write_text(raw_response, encoding="utf-8")

    print("=" * 80)
    print("OpenAI connection test completed")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Latency ms: {latency_ms}")
    print(f"Raw response: {raw_response}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()