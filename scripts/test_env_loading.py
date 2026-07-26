from dotenv import load_dotenv
import os

load_dotenv()

nvd_key = os.getenv("NVD_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

print("=" * 80)
print("Environment Variable Check")
print("=" * 80)

print(f"NVD key loaded: {bool(nvd_key)}")
print(f"OpenAI key loaded: {bool(openai_key)}")
print(f"Gemini key loaded: {bool(gemini_key)}")

if nvd_key:
    print(f"NVD key length: {len(nvd_key)}")
    print(f"OpenAI key length: {len(openai_key)}")
    print(f"Gemini key length: {len(gemini_key)}")