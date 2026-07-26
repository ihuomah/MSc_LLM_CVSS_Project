from pathlib import Path
from parse_model_response import parse_model_response


BASE_DIR = Path("prompts/frozen_prompt_v1")

TEST_FILES = [
    BASE_DIR / "condition1_test_outputs" / "chatgpt_condition1_test_output_v1.txt",
    BASE_DIR / "condition1_test_outputs" / "gemini_condition1_test_output_v1.txt",
    BASE_DIR / "condition1_test_outputs" / "ollama_condition1_test_output_v1.txt",
    BASE_DIR / "condition2_test_outputs" / "chatgpt_condition2_test_output_v1.txt",
    BASE_DIR / "condition2_test_outputs" / "gemini_condition2_test_output_v1.txt",
    BASE_DIR / "condition2_test_outputs" / "ollama_condition2_test_output_v1.txt",
]


def main():
    for file_path in TEST_FILES:
        print("=" * 80)
        print(f"File: {file_path}")

        if not file_path.exists():
            print("ERROR: File not found")
            continue

        raw_response = file_path.read_text(encoding="utf-8")
        result = parse_model_response(raw_response)

        print(f"Compliance category: {result['compliance_category']}")
        print(f"Parse success: {result['parse_success']}")

        if result["validation"]:
            print(f"All keys present: {result['validation']['all_keys_present']}")
            print(f"Valid metric values: {result['validation']['valid_metric_values']}")
            print(f"Base score numeric: {result['validation']['base_score_numeric']}")
            print(f"Vector string present: {result['validation']['vector_string_present']}")

            if result["validation"]["missing_keys"]:
                print(f"Missing keys: {result['validation']['missing_keys']}")

            if result["validation"]["invalid_values"]:
                print(f"Invalid values: {result['validation']['invalid_values']}")


if __name__ == "__main__":
    main()