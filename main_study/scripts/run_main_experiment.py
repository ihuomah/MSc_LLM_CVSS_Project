# Save as: main_study/scripts/run_main_experiment.py
# Phase 7 Main Experiment Runner
#
# Usage examples:
#   Pre-flight all providers:
#       python main_study\scripts\run_main_experiment.py --run-id run_001 --records 1,2
#
#   Main run in three terminals:
#       python main_study\scripts\run_main_experiment.py --run-id run_001 --provider openai
#       python main_study\scripts\run_main_experiment.py --run-id run_001 --provider gemini
#       python main_study\scripts\run_main_experiment.py --run-id run_001 --provider ollama
#
#   Final combined export after provider runs:
#       python main_study\scripts\run_main_experiment.py --run-id run_001 --combine-only

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types
from cvss import CVSS3


# =============================================================================
# Paths
# =============================================================================

SCRIPT_PATH = Path(__file__).resolve()
MAIN_STUDY_DIR = SCRIPT_PATH.parents[1]
PROJECT_ROOT = SCRIPT_PATH.parents[2]

INPUT_DATASET = MAIN_STUDY_DIR / "experiment_inputs" / "main_inference_dataset_v1.parquet"

RUNTIME_DIR = MAIN_STUDY_DIR / "runtime"
RUNTIME_CONFIG = RUNTIME_DIR / "config.py"
RUNTIME_PARSER = RUNTIME_DIR / "parser" / "parse_model_response_v1.py"
RUNTIME_CONVENTIONAL_PROMPT = RUNTIME_DIR / "prompts" / "condition1_conventional_prompt_v1.txt"
RUNTIME_STRUCTURED_PROMPT = RUNTIME_DIR / "prompts" / "condition2_structured_prompt_v1.txt"

FROZEN_CONVENTIONAL_PROMPT = PROJECT_ROOT / "prompts" / "frozen_prompt_v1" / "condition1_conventional_prompt_v1.txt"
FROZEN_STRUCTURED_PROMPT = PROJECT_ROOT / "prompts" / "frozen_prompt_v1" / "condition2_structured_prompt_v1.txt"
FROZEN_PARSER = PROJECT_ROOT / "scripts" / "frozen_parser_v1" / "parse_model_response_v1.py"

RESULTS_DIR = MAIN_STUDY_DIR / "results"
LOGS_DIR = RESULTS_DIR / "logs"
FAILURES_DIR = RESULTS_DIR / "failures"
RAW_RESULTS_DIR = RESULTS_DIR / "raw_results"
RAW_RESPONSES_DIR = RESULTS_DIR / "raw_responses"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_SHOW_URL = "http://localhost:11434/api/show"

MAX_RETRIES = 5
RETRY_WAIT_SECONDS = [5, 10, 20, 30, 60]


# =============================================================================
# Runtime imports
# =============================================================================

def import_module_from_path(module_name: str, path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import module from: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


config = import_module_from_path("main_runtime_config", RUNTIME_CONFIG)
parser_module = import_module_from_path("main_runtime_parser", RUNTIME_PARSER)

OPENAI_MODEL = config.OPENAI_MODEL
GEMINI_MODEL = config.GEMINI_MODEL
OLLAMA_MODEL = config.OLLAMA_MODEL
TEMPERATURE = config.TEMPERATURE
SEED = config.SEED

parse_model_response = parser_module.parse_model_response

load_dotenv(PROJECT_ROOT / ".env")


# =============================================================================
# Utility functions
# =============================================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_log(log_file: Path, message: str):
    log_file.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{utc_now()}] {message}"
    print(line)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def append_jsonl(path: Path, row: dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def calculate_vector_score(vector: str | None):
    if not vector:
        return None
    try:
        return CVSS3(vector).scores()[0]
    except Exception:
        return None


def render_prompt(prompt_path: Path, description: str) -> str:
    template = prompt_path.read_text(encoding="utf-8")
    if "{DESCRIPTION}" not in template:
        raise ValueError(f"{prompt_path} does not contain {{DESCRIPTION}}")
    return template.replace("{DESCRIPTION}", description)


def record_label(record_id: int) -> str:
    return f"R{record_id:04d}"


def output_paths(record_id: int, provider: str, condition: str, run_id: str) -> dict[str, Path]:
    base = RAW_RESPONSES_DIR / provider / condition / run_id
    label = record_label(record_id)

    return {
        "dir": base,
        "raw": base / f"{label}_{condition}_raw.txt",
        "api": base / f"{label}_{condition}_api_response.json",
        "parsed": base / f"{label}_{condition}_parsed.json",
    }


def is_completed(record_id: int, provider: str, condition: str, run_id: str) -> bool:
    """
    Canonical resume rule:
    Complete if canonical parsed file exists and api_success=True.
    parse_success may be True or False.
    """
    parsed_path = output_paths(record_id, provider, condition, run_id)["parsed"]
    parsed = read_json(parsed_path)
    return bool(parsed and parsed.get("api_success") is True)


def illegal_excel_clean(value):
    """
    Excel/openpyxl can crash on illegal control characters.
    Parquet remains master, so this sanitisation is only for XLSX review output.
    """
    if isinstance(value, str):
        return re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", value)
    return value


def sanitise_dataframe_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    cleaned = df.copy()
    for col in cleaned.columns:
        if cleaned[col].dtype == "object":
            cleaned[col] = cleaned[col].map(illegal_excel_clean)
    return cleaned


# =============================================================================
# Provenance and integrity
# =============================================================================

def build_asset_manifest() -> list[dict[str, Any]]:
    assets = [
        {"name": "runtime_config", "path": RUNTIME_CONFIG},
        {"name": "runtime_parser", "path": RUNTIME_PARSER},
        {"name": "runtime_conventional_prompt", "path": RUNTIME_CONVENTIONAL_PROMPT},
        {"name": "runtime_structured_prompt", "path": RUNTIME_STRUCTURED_PROMPT},
        {"name": "input_dataset", "path": INPUT_DATASET},
        {"name": "frozen_parser", "path": FROZEN_PARSER},
        {"name": "frozen_conventional_prompt", "path": FROZEN_CONVENTIONAL_PROMPT},
        {"name": "frozen_structured_prompt", "path": FROZEN_STRUCTURED_PROMPT},
    ]

    manifest = []
    for asset in assets:
        path = asset["path"]
        if not path.exists():
            raise FileNotFoundError(f"Required asset missing: {path}")
        manifest.append({
            "name": asset["name"],
            "path": str(path),
            "sha256": sha256_file(path),
        })

    return manifest


def assert_runtime_matches_frozen(asset_manifest: list[dict[str, Any]]):
    by_name = {row["name"]: row for row in asset_manifest}

    checks = [
        ("runtime_parser", "frozen_parser"),
        ("runtime_conventional_prompt", "frozen_conventional_prompt"),
        ("runtime_structured_prompt", "frozen_structured_prompt"),
    ]

    mismatches = []

    for runtime_name, frozen_name in checks:
        runtime_hash = by_name[runtime_name]["sha256"]
        frozen_hash = by_name[frozen_name]["sha256"]

        if runtime_hash != frozen_hash:
            mismatches.append({
                "runtime_asset": runtime_name,
                "frozen_asset": frozen_name,
                "runtime_hash": runtime_hash,
                "frozen_hash": frozen_hash,
            })

    if mismatches:
        raise RuntimeError(
            "Runtime assets do not match frozen originals:\n"
            + json.dumps(mismatches, indent=2)
        )


def environment_manifest() -> dict[str, Any]:
    return {
        "timestamp": utc_now(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "package_versions": {
            "openai": package_version("openai"),
            "google-genai": package_version("google-genai"),
            "requests": package_version("requests"),
            "pandas": package_version("pandas"),
            "pyarrow": package_version("pyarrow"),
            "cvss": package_version("cvss"),
            "python-dotenv": package_version("python-dotenv"),
        },
        "models": {
            "openai": OPENAI_MODEL,
            "gemini": GEMINI_MODEL,
            "ollama": OLLAMA_MODEL,
        },
        "requested_temperature": TEMPERATURE,
        "requested_seed": SEED,
    }


# =============================================================================
# Error classification
# =============================================================================

def get_status_code(exc: Exception) -> int | None:
    """
    Extract HTTP status code from common exception shapes:
    requests, OpenAI SDK, Google SDK wrappers.
    """
    status_code = getattr(exc, "status_code", None)
    if status_code is not None:
        try:
            return int(status_code)
        except Exception:
            pass

    response = getattr(exc, "response", None)
    if response is not None:
        status_code = getattr(response, "status_code", None)
        if status_code is not None:
            try:
                return int(status_code)
            except Exception:
                pass

    return None


def is_retryable_exception(exc: Exception) -> bool:
    status_code = get_status_code(exc)

    if status_code in {400, 401, 403}:
        return False

    if status_code == 429:
        return True

    if status_code is not None and 500 <= status_code <= 599:
        return True

    if isinstance(exc, (requests.Timeout, requests.ConnectionError)):
        return True

    # For unknown SDK/network errors, retry conservatively.
    return True


class ProbeInconclusiveError(RuntimeError):
    pass


def classify_probe_exception(exc: Exception) -> str:
    """
    Capability probes must not silently disable temperature/seed after a transient error.
    A real 400-style rejection means unsupported.
    Retryable/transient errors mean inconclusive and should abort the run.
    """
    status_code = get_status_code(exc)
    msg = str(exc).lower()

    if (
    status_code == 400
    or "unsupported parameter" in msg
    or "unknown parameter" in msg
    or "unexpected keyword argument" in msg
):
        return "unsupported"

    if is_retryable_exception(exc):
        return "inconclusive"

    # 401/403 etc are not parameter capability issues; abort rather than run wrongly.
    return "inconclusive"


def probe_with_retry(label: str, call_fn, log_file: Path):
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            return call_fn()
        except Exception as e:
            last_error = e
            classification = classify_probe_exception(e)

            if classification == "unsupported":
                raise

            if attempt >= MAX_RETRIES:
                break

            wait_seconds = RETRY_WAIT_SECONDS[min(attempt, len(RETRY_WAIT_SECONDS) - 1)]
            write_log(
                log_file,
                f"Capability probe transient error for {label}. "
                f"attempt={attempt + 1}/{MAX_RETRIES}, wait={wait_seconds}s, "
                f"status_code={get_status_code(e)}, error={type(e).__name__}: {e}"
            )
            time.sleep(wait_seconds)

    raise ProbeInconclusiveError(
        f"Capability probe inconclusive for {label}. "
        f"Last error: {type(last_error).__name__}: {last_error}"
    )


# =============================================================================
# Provider capability probe
# =============================================================================

def probe_openai(log_file: Path) -> dict[str, Any]:
    result = {
        "provider": "openai",
        "model": OPENAI_MODEL,
        "temperature_supported": False,
        "seed_supported": False,
        "temperature_status": "unsupported_or_rejected",
        "seed_status": "unsupported_or_rejected",
        "probe_errors": [],
    }

    client = OpenAI()
    base_kwargs = {"model": OPENAI_MODEL, "input": "Return the word OK only."}

    try:
        def call_temperature_probe():
            kwargs = dict(base_kwargs)
            kwargs["temperature"] = TEMPERATURE
            return client.responses.create(**kwargs)

        response = probe_with_retry("openai.temperature", call_temperature_probe, log_file)
        result["temperature_supported"] = True
        result["temperature_status"] = "accepted_unconfirmed"
        result["temperature_probe_response_id"] = getattr(response, "id", None)
    except ProbeInconclusiveError:
        raise
    except Exception as e:
        result["probe_errors"].append({
            "parameter": "temperature",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "status_code": get_status_code(e),
        })

    try:
        def call_seed_probe():
            kwargs = dict(base_kwargs)
            kwargs["seed"] = SEED
            return client.responses.create(**kwargs)

        response = probe_with_retry("openai.seed", call_seed_probe, log_file)
        result["seed_supported"] = True
        result["seed_status"] = "accepted_unconfirmed"
        result["seed_probe_response_id"] = getattr(response, "id", None)
    except ProbeInconclusiveError:
        raise
    except Exception as e:
        result["probe_errors"].append({
            "parameter": "seed",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "status_code": get_status_code(e),
        })

    write_log(log_file, f"OpenAI capability probe: temp={result['temperature_status']}, seed={result['seed_status']}")
    return result

def probe_gemini(log_file: Path) -> dict[str, Any]:
    result = {
        "provider": "gemini",
        "model": GEMINI_MODEL,
        "temperature_supported": False,
        "seed_supported": False,
        "temperature_status": "unsupported_or_rejected",
        "seed_status": "unsupported_or_rejected",
        "probe_errors": [],
    }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found; aborting provider probe.")

    client = genai.Client(api_key=api_key)

    try:
        def call_temperature_probe():
            cfg = types.GenerateContentConfig(temperature=TEMPERATURE)
            return client.models.generate_content(
                model=GEMINI_MODEL,
                contents="Return the word OK only.",
                config=cfg,
            )

        response = probe_with_retry("gemini.temperature", call_temperature_probe, log_file)
        result["temperature_supported"] = True
        result["temperature_status"] = "accepted_unconfirmed"
        result["temperature_probe_finish_reason"] = extract_gemini_finish_reason(response.model_dump(mode="json"))
    except ProbeInconclusiveError:
        raise
    except Exception as e:
        result["probe_errors"].append({
            "parameter": "temperature",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "status_code": get_status_code(e),
        })

    try:
        def call_seed_probe():
            cfg = types.GenerateContentConfig(seed=SEED)
            return client.models.generate_content(
                model=GEMINI_MODEL,
                contents="Return the word OK only.",
                config=cfg,
            )

        response = probe_with_retry("gemini.seed", call_seed_probe, log_file)
        result["seed_supported"] = True
        result["seed_status"] = "accepted_unconfirmed"
        result["seed_probe_finish_reason"] = extract_gemini_finish_reason(response.model_dump(mode="json"))
    except ProbeInconclusiveError:
        raise
    except Exception as e:
        result["probe_errors"].append({
            "parameter": "seed",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "status_code": get_status_code(e),
        })

    write_log(log_file, f"Gemini capability probe: temp={result['temperature_status']}, seed={result['seed_status']}")
    return result

def probe_ollama(log_file: Path) -> dict[str, Any]:
    result = {
        "provider": "ollama",
        "model": OLLAMA_MODEL,
        "temperature_supported": False,
        "seed_supported": False,
        "temperature_status": "unsupported_or_rejected",
        "seed_status": "unsupported_or_rejected",
        "probe_errors": [],
        "model_digest": None,
    }

    try:
        show_response = requests.post(
            OLLAMA_SHOW_URL,
            json={"model": OLLAMA_MODEL},
            timeout=60,
        )
        if show_response.ok:
            data = show_response.json()
            result["model_digest"] = data.get("digest")
    except Exception as e:
        result["probe_errors"].append({
            "parameter": "model_show",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "status_code": get_status_code(e),
        })

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": "Return the word OK only.",
            "stream": False,
            "options": {
                "temperature": TEMPERATURE,
                "seed": SEED,
            },
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        result["temperature_supported"] = True
        result["seed_supported"] = True
        result["temperature_status"] = "accepted_unconfirmed"
        result["seed_status"] = "accepted_unconfirmed"
    except Exception as e:
        result["probe_errors"].append({
            "parameter": "temperature_seed",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "status_code": get_status_code(e),
        })

    write_log(log_file, f"Ollama capability probe: temp={result['temperature_status']}, seed={result['seed_status']}")
    return result


def run_capability_probe(providers: list[str], log_file: Path) -> dict[str, Any]:
    write_log(log_file, f"Running provider capability probe for: {providers}")

    probe = {"timestamp": utc_now()}

    if "openai" in providers:
        probe["openai"] = probe_openai(log_file)

    if "gemini" in providers:
        probe["gemini"] = probe_gemini(log_file)

    if "ollama" in providers:
        probe["ollama"] = probe_ollama(log_file)

    write_log(log_file, "Provider capability probe completed")
    return probe


# =============================================================================
# Provider response extraction
# =============================================================================

def extract_openai_text(api_response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """
    Avoid relying only on response.output_text.
    Empty output/refusal is still API success and should become State 2.
    """
    metadata = {
        "finish_reason": None,
        "refusal": None,
        "blocked_or_empty": False,
    }

    text_parts = []

    for item in api_response.get("output", []) or []:
        for content in item.get("content", []) or []:
            ctype = content.get("type")
            if ctype in {"output_text", "text"}:
                text = content.get("text")
                if isinstance(text, str):
                    text_parts.append(text)
            if "refusal" in content:
                metadata["refusal"] = content.get("refusal")

    raw = "\n".join(text_parts).strip()

    if not raw:
        metadata["blocked_or_empty"] = True

    return raw, metadata


def extract_gemini_text(api_response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """
    If Gemini returns a response object but no text/parts, this is State 2
    not State 3. It is an API success with unusable content.
    """
    metadata = {
        "finish_reason": extract_gemini_finish_reason(api_response),
        "block_reason": None,
        "blocked_or_empty": False,
    }

    prompt_feedback = api_response.get("prompt_feedback") or api_response.get("promptFeedback") or {}
    metadata["block_reason"] = prompt_feedback.get("block_reason") or prompt_feedback.get("blockReason")

    text_parts = []

    for cand in api_response.get("candidates", []) or []:
        content = cand.get("content") or {}
        for part in content.get("parts", []) or []:
            text = part.get("text")
            if isinstance(text, str):
                text_parts.append(text)

    raw = "\n".join(text_parts).strip()

    if not raw:
        metadata["blocked_or_empty"] = True

    return raw, metadata


def extract_gemini_finish_reason(api_response: dict[str, Any]) -> str | None:
    candidates = api_response.get("candidates", []) or []
    if not candidates:
        return None
    return candidates[0].get("finish_reason") or candidates[0].get("finishReason")


def extract_openai_usage(api_response: dict[str, Any]) -> dict[str, Any]:
    usage = api_response.get("usage") or {}
    return {
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }


def extract_gemini_usage(api_response: dict[str, Any]) -> dict[str, Any]:
    usage = api_response.get("usage_metadata") or api_response.get("usageMetadata") or {}
    return {
        "input_tokens": usage.get("prompt_token_count") or usage.get("promptTokenCount"),
        "output_tokens": usage.get("candidates_token_count") or usage.get("candidatesTokenCount"),
        "total_tokens": usage.get("total_token_count") or usage.get("totalTokenCount"),
    }


def extract_ollama_usage(api_response: dict[str, Any]) -> dict[str, Any]:
    prompt_tokens = api_response.get("prompt_eval_count")
    output_tokens = api_response.get("eval_count")
    total = None

    if prompt_tokens is not None and output_tokens is not None:
        total = prompt_tokens + output_tokens

    return {
        "input_tokens": prompt_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total,
    }


# =============================================================================
# Provider calls
# =============================================================================

def call_openai_once(prompt: str, capability: dict[str, Any]):
    client = OpenAI()

    kwargs = {
        "model": OPENAI_MODEL,
        "input": prompt,
    }

    if capability.get("temperature_supported"):
        kwargs["temperature"] = TEMPERATURE

    if capability.get("seed_supported"):
        kwargs["seed"] = SEED

    start = time.time()
    response = client.responses.create(**kwargs)
    end = time.time()

    try:
        api_response = response.model_dump(mode="json")
    except Exception as e:
        api_response = {
            "model_dump_error": f"{type(e).__name__}: {e}",
            "response_repr": repr(response),
        }

    try:
        raw_response, response_meta = extract_openai_text(api_response)
    except Exception as e:
        raw_response = ""
        response_meta = {
            "finish_reason": None,
            "refusal": None,
            "blocked_or_empty": True,
            "extraction_error": f"{type(e).__name__}: {e}",
        }

    usage = extract_openai_usage(api_response)

    metadata = {
        "model_snapshot": api_response.get("model") or OPENAI_MODEL,
        "provider_fingerprint": api_response.get("system_fingerprint"),
        "response_id": api_response.get("id"),
        "finish_reason": response_meta.get("finish_reason"),
        "block_reason": None,
        "refusal": response_meta.get("refusal"),
        "blocked_or_empty": response_meta.get("blocked_or_empty"),
        "extraction_error": response_meta.get("extraction_error"),
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_tokens": usage["total_tokens"],
    }

    return raw_response, int((end - start) * 1000), api_response, metadata

def call_gemini_once(prompt: str, capability: dict[str, Any]):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    config_kwargs = {}

    if capability.get("temperature_supported"):
        config_kwargs["temperature"] = TEMPERATURE

    if capability.get("seed_supported"):
        config_kwargs["seed"] = SEED

    cfg = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    start = time.time()

    if cfg is not None:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=cfg,
        )
    else:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

    end = time.time()

    try:
        api_response = response.model_dump(mode="json")
    except Exception as e:
        api_response = {
            "model_dump_error": f"{type(e).__name__}: {e}",
            "response_repr": repr(response),
        }

    try:
        raw_response, response_meta = extract_gemini_text(api_response)
    except Exception as e:
        raw_response = ""
        response_meta = {
            "finish_reason": None,
            "block_reason": None,
            "blocked_or_empty": True,
            "extraction_error": f"{type(e).__name__}: {e}",
        }

    usage = extract_gemini_usage(api_response)

    metadata = {
        "model_snapshot": (
            api_response.get("model_version")
            or api_response.get("modelVersion")
            or GEMINI_MODEL
        ),
        "provider_fingerprint": (
            api_response.get("model_version")
            or api_response.get("modelVersion")
        ),
        "response_id": None,
        "finish_reason": response_meta.get("finish_reason"),
        "block_reason": response_meta.get("block_reason"),
        "refusal": None,
        "blocked_or_empty": response_meta.get("blocked_or_empty"),
        "extraction_error": response_meta.get("extraction_error"),
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_tokens": usage["total_tokens"],
    }

    return raw_response, int((end - start) * 1000), api_response, metadata

def call_ollama_once(prompt: str, capability: dict[str, Any]):
    options = {}

    if capability.get("temperature_supported"):
        options["temperature"] = TEMPERATURE

    if capability.get("seed_supported"):
        options["seed"] = SEED

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    if options:
        payload["options"] = options

    start = time.time()
    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    end = time.time()

    response.raise_for_status()

    api_response = response.json()
    raw_response = (api_response.get("response") or "").strip()
    usage = extract_ollama_usage(api_response)

    metadata = {
        "model_snapshot": OLLAMA_MODEL,
        "provider_fingerprint": capability.get("model_digest"),
        "response_id": None,
        "finish_reason": api_response.get("done_reason"),
        "block_reason": None,
        "refusal": None,
        "blocked_or_empty": not bool(raw_response),
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_tokens": usage["total_tokens"],
    }

    return raw_response, int((end - start) * 1000), api_response, metadata


def call_provider_with_retry(provider: str, prompt: str, capability: dict[str, Any], log_file: Path):
    total_retry_wait_ms = 0
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            if provider == "openai":
                result = call_openai_once(prompt, capability)
            elif provider == "gemini":
                result = call_gemini_once(prompt, capability)
            elif provider == "ollama":
                result = call_ollama_once(prompt, capability)
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            return {
                "api_success": True,
                "raw_response": result[0],
                "latency_ms": result[1],
                "api_response": result[2],
                "metadata": result[3],
                "retry_count": attempt,
                "total_retry_wait_ms": total_retry_wait_ms,
                "error_type": None,
                "error_message": None,
                "status_code": None,
            }

        except Exception as e:
            last_error = e
            status_code = get_status_code(e)
            retryable = is_retryable_exception(e)

            if not retryable:
                write_log(
                    log_file,
                    f"NON-RETRYABLE API ERROR provider={provider}, "
                    f"status_code={status_code}, error={type(e).__name__}: {e}"
                )
                break

            if attempt >= MAX_RETRIES:
                break

            wait_seconds = RETRY_WAIT_SECONDS[min(attempt, len(RETRY_WAIT_SECONDS) - 1)]
            total_retry_wait_ms += wait_seconds * 1000

            write_log(
                log_file,
                f"Retryable API error provider={provider}, "
                f"attempt={attempt + 1}/{MAX_RETRIES}, "
                f"wait={wait_seconds}s, "
                f"status_code={status_code}, "
                f"error={type(e).__name__}: {e}"
            )

            time.sleep(wait_seconds)

    return {
        "api_success": False,
        "raw_response": None,
        "latency_ms": None,
        "api_response": None,
        "metadata": {},
        "retry_count": MAX_RETRIES if last_error and is_retryable_exception(last_error) else 0,
        "total_retry_wait_ms": total_retry_wait_ms,
        "error_type": type(last_error).__name__ if last_error else "UnknownError",
        "error_message": str(last_error) if last_error else "Unknown error",
        "status_code": get_status_code(last_error) if last_error else None,
    }


# =============================================================================
# Parsing and result row
# =============================================================================

def safe_parse(raw_response: str):
    try:
        parsed = parse_model_response(raw_response)
        return parsed, None
    except Exception as e:
        return {
            "parse_success": False,
            "compliance_category": "parser_exception",
            "parsed_json": {},
            "validation": {},
        }, f"{type(e).__name__}: {e}"


def build_result_row(
    record_id: int,
    provider: str,
    condition: str,
    run_id: str,
    capability: dict[str, Any],
    provider_result: dict[str, Any],
    parsed: dict[str, Any],
    parser_exception: str | None,
    paths: dict[str, Path],
) -> dict[str, Any]:

    parsed_json = parsed.get("parsed_json") or {}
    validation = parsed.get("validation") or {}

    predicted_vector = parsed_json.get("vector_string")
    predicted_base_score = parsed_json.get("base_score")

    calculated_base_score = None
    vector_score_delta = None
    vector_score_consistent = None

    if predicted_vector and predicted_base_score is not None:
        calculated_base_score = calculate_vector_score(predicted_vector)

        if calculated_base_score is not None:
            try:
                vector_score_delta = float(predicted_base_score) - float(calculated_base_score)
                vector_score_consistent = abs(vector_score_delta) < 0.15
            except Exception:
                vector_score_delta = None
                vector_score_consistent = None

    metadata = provider_result.get("metadata") or {}

    return {
        "record_id": record_id,
        "record_label": record_label(record_id),
        "provider": provider,
        "model_name": provider,
        "model_snapshot": metadata.get("model_snapshot"),
        "prompt_condition": condition,
        "run_id": run_id,
        "timestamp": utc_now(),

        "requested_temperature": TEMPERATURE,
        "requested_seed": SEED,
        "temperature_status": capability.get("temperature_status"),
        "seed_status": capability.get("seed_status"),

        "api_success": provider_result["api_success"],
        "parse_success": parsed.get("parse_success"),
        "compliance_category": parsed.get("compliance_category"),

        "inference_latency_ms": provider_result["latency_ms"],
        "retry_count": provider_result["retry_count"],
        "total_retry_wait_ms": provider_result["total_retry_wait_ms"],
        "error_type": provider_result["error_type"],
        "error_message": provider_result["error_message"],
        "status_code": provider_result.get("status_code"),
        "parser_exception": parser_exception,

        "provider_fingerprint": metadata.get("provider_fingerprint"),
        "response_id": metadata.get("response_id"),
        "finish_reason": metadata.get("finish_reason"),
        "block_reason": metadata.get("block_reason"),
        "refusal": metadata.get("refusal"),
        "blocked_or_empty": metadata.get("blocked_or_empty"),
        "extraction_error": metadata.get("extraction_error"),
        "input_tokens": metadata.get("input_tokens"),
        "output_tokens": metadata.get("output_tokens"),
        "total_tokens": metadata.get("total_tokens"),

        "raw_response_file": str(paths["raw"]),
        "api_response_file": str(paths["api"]),
        "parsed_output_file": str(paths["parsed"]),

        "all_keys_present": validation.get("all_keys_present"),
        "valid_metric_values": validation.get("valid_metric_values"),
        "base_score_numeric": validation.get("base_score_numeric"),
        "vector_string_present": validation.get("vector_string_present"),

        "attack_vector": parsed_json.get("attack_vector"),
        "attack_complexity": parsed_json.get("attack_complexity"),
        "privileges_required": parsed_json.get("privileges_required"),
        "user_interaction": parsed_json.get("user_interaction"),
        "scope": parsed_json.get("scope"),
        "confidentiality_impact": parsed_json.get("confidentiality_impact"),
        "integrity_impact": parsed_json.get("integrity_impact"),
        "availability_impact": parsed_json.get("availability_impact"),

        "predicted_vector": predicted_vector,
        "predicted_base_score": predicted_base_score,
        "calculated_base_score": calculated_base_score,
        "vector_score_delta": vector_score_delta,
        "vector_score_consistent": vector_score_consistent,
    }


# =============================================================================
# Dataset and task selection
# =============================================================================

def load_dataset() -> dict[int, str]:
    if not INPUT_DATASET.exists():
        raise FileNotFoundError(f"Input dataset not found: {INPUT_DATASET}")

    df = pd.read_parquet(INPUT_DATASET)

    required = {"record_id", "description_for_model"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Input dataset missing columns: {missing}")

    dataset = {}

    for _, row in df.iterrows():
        record_id = int(row["record_id"])
        description = row["description_for_model"]

        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"Empty description_for_model for record_id={record_id}")

        dataset[record_id] = description

    return dataset


def parse_records_arg(records_arg: str | None, available_records: list[int]) -> list[int]:
    if not records_arg:
        return available_records

    requested = []
    for part in records_arg.split(","):
        part = part.strip()
        if part:
            requested.append(int(part))

    missing = sorted(set(requested) - set(available_records))
    if missing:
        raise ValueError(f"Requested record IDs not found in dataset: {missing}")

    return requested


def selected_providers(provider_arg: str) -> list[str]:
    if provider_arg == "all":
        return ["openai", "gemini", "ollama"]
    return [provider_arg]


# =============================================================================
# Export rebuild
# =============================================================================

def scan_canonical_results(run_id: str, provider: str | None = None) -> list[dict[str, Any]]:
    rows = []

    if provider:
        pattern = RAW_RESPONSES_DIR / provider
        parsed_files = pattern.glob(f"*/{run_id}/*_parsed.json")
    else:
        parsed_files = RAW_RESPONSES_DIR.glob(f"*/*/{run_id}/*_parsed.json")

    for parsed_file in parsed_files:
        data = read_json(parsed_file)
        if data and data.get("api_success") is True:
            rows.append(data)

    rows.sort(key=lambda r: (
        int(r.get("record_id", 0)),
        str(r.get("provider", "")),
        str(r.get("prompt_condition", "")),
    ))

    return rows


def normalise_export_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep derived exports from crashing on mixed model-generated types.
    Canonical per-record JSON files remain the source of truth.
    """
    if df.empty:
        return df

    out = df.copy()

    numeric_cols = [
        "record_id",
        "requested_temperature",
        "requested_seed",
        "inference_latency_ms",
        "retry_count",
        "total_retry_wait_ms",
        "status_code",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "predicted_base_score",
        "calculated_base_score",
        "vector_score_delta",
    ]

    bool_cols = [
        "api_success",
        "parse_success",
        "all_keys_present",
        "valid_metric_values",
        "base_score_numeric",
        "vector_string_present",
        "vector_score_consistent",
        "blocked_or_empty",
    ]

    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    for col in bool_cols:
        if col in out.columns:
            out[col] = out[col].astype("boolean")

    for col in out.columns:
        if out[col].dtype == "object":
            out[col] = out[col].map(
                lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else x
            )

    return out


def write_export_files(
    rows: list[dict[str, Any]],
    parquet_file: Path,
    csv_file: Path,
    xlsx_file: Path | None,
    log_file: Path,
):
    RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows)

    if df.empty:
        write_log(log_file, f"No rows available for export: {parquet_file.name}")
        return

    try:
        export_df = normalise_export_dataframe(df)
        export_df.to_parquet(parquet_file, index=False)
        export_df.to_csv(csv_file, index=False, encoding="utf-8")
    except Exception as e:
        write_log(
            log_file,
            f"Parquet/CSV export failed but run will continue: "
            f"{type(e).__name__}: {e}"
        )
        return

    if xlsx_file is not None:
        try:
            excel_df = sanitise_dataframe_for_excel(export_df)
            excel_df.to_excel(xlsx_file, index=False)
        except Exception as e:
            write_log(
                log_file,
                f"XLSX export failed but run will continue: "
                f"{type(e).__name__}: {e}"
            )

def rebuild_provider_exports(run_id: str, provider: str, log_file: Path):
    rows = scan_canonical_results(run_id, provider=provider)

    parquet_file = RAW_RESULTS_DIR / f"{run_id}_{provider}_results.parquet"
    csv_file = RAW_RESULTS_DIR / f"{run_id}_{provider}_results.csv"

    # No XLSX in-loop. XLSX is built only in combined export mode.
    write_export_files(
        rows=rows,
        parquet_file=parquet_file,
        csv_file=csv_file,
        xlsx_file=None,
        log_file=log_file,
    )

    write_log(log_file, f"Provider exports rebuilt for {provider}. Rows exported: {len(rows)}")


def rebuild_combined_exports(run_id: str, log_file: Path):
    rows = scan_canonical_results(run_id, provider=None)

    parquet_file = RAW_RESULTS_DIR / f"{run_id}_results.parquet"
    csv_file = RAW_RESULTS_DIR / f"{run_id}_results.csv"
    xlsx_file = RAW_RESULTS_DIR / f"{run_id}_results.xlsx"

    write_export_files(
        rows=rows,
        parquet_file=parquet_file,
        csv_file=csv_file,
        xlsx_file=xlsx_file,
        log_file=log_file,
    )

    write_log(log_file, f"Combined exports rebuilt. Rows exported: {len(rows)}")


# =============================================================================
# Task execution
# =============================================================================

def execute_task(
    record_id: int,
    description: str,
    provider: str,
    condition: str,
    prompt_path: Path,
    run_id: str,
    capability: dict[str, Any],
    failure_file: Path,
    log_file: Path,
) -> str:

    paths = output_paths(record_id, provider, condition, run_id)

    if is_completed(record_id, provider, condition, run_id):
        return "skipped"

    write_log(
        log_file,
        f"RUN record_id={record_id}, provider={provider}, condition={condition}, run_id={run_id}"
    )

    prompt = render_prompt(prompt_path, description)
    provider_result = call_provider_with_retry(provider, prompt, capability, log_file)

    if not provider_result["api_success"]:
        failure_row = {
            "timestamp": utc_now(),
            "record_id": record_id,
            "record_label": record_label(record_id),
            "provider": provider,
            "prompt_condition": condition,
            "run_id": run_id,
            "retry_count": provider_result["retry_count"],
            "total_retry_wait_ms": provider_result["total_retry_wait_ms"],
            "error_type": provider_result["error_type"],
            "error_message": provider_result["error_message"],
            "status_code": provider_result.get("status_code"),
        }
        append_jsonl(failure_file, failure_row)
        write_log(log_file, f"API FAILURE record_id={record_id}, provider={provider}, condition={condition}")
        return "api_failure"

    # API success: write canonical artefacts even if raw content is empty/unparseable.
    paths["dir"].mkdir(parents=True, exist_ok=True)

    raw_response = provider_result["raw_response"] or ""
    api_response = provider_result["api_response"] or {}

    paths["raw"].write_text(raw_response, encoding="utf-8")
    paths["api"].write_text(json.dumps(api_response, indent=2, ensure_ascii=False), encoding="utf-8")

    parsed, parser_exception = safe_parse(raw_response)

    row = build_result_row(
        record_id=record_id,
        provider=provider,
        condition=condition,
        run_id=run_id,
        capability=capability,
        provider_result=provider_result,
        parsed=parsed,
        parser_exception=parser_exception,
        paths=paths,
    )

    paths["parsed"].write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")

    if row["parse_success"]:
        write_log(log_file, f"SUCCESS record_id={record_id}, provider={provider}, condition={condition}")
        return "success"

    write_log(log_file, f"PARSE FAILURE SAVED record_id={record_id}, provider={provider}, condition={condition}")
    return "parse_failure"


def count_completed_for_task_list(
    selected_records: list[int],
    providers: list[str],
    conditions: list[tuple[str, Path]],
    run_id: str,
) -> int:
    completed = 0
    for record_id in selected_records:
        for provider in providers:
            for condition, _ in conditions:
                if is_completed(record_id, provider, condition, run_id):
                    completed += 1
    return completed


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True, help="Example: run_001")
    parser.add_argument(
        "--provider",
        default="all",
        choices=["all", "openai", "gemini", "ollama"],
        help="Provider to run. Use all for pre-flight; use one provider per terminal for main run.",
    )
    parser.add_argument("--records", default=None, help="Optional comma-separated record IDs, e.g. 1,2")
    parser.add_argument("--export-every", type=int, default=25, help="Rebuild provider parquet/csv every N API-success rows")
    parser.add_argument("--heartbeat-every", type=int, default=50, help="Heartbeat every N processed tasks")
    parser.add_argument(
        "--combine-only",
        action="store_true",
        help="Do not run inference. Rebuild combined parquet/csv/xlsx from canonical files.",
    )
    args = parser.parse_args()

    run_id = args.run_id
    providers = selected_providers(args.provider)

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    FAILURES_DIR.mkdir(parents=True, exist_ok=True)
    RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

    log_suffix = "combine" if args.combine_only else args.provider
    log_file = LOGS_DIR / f"{run_id}_{log_suffix}_log.txt"
    failure_file = FAILURES_DIR / f"{run_id}_{args.provider}_failures.jsonl"
    provenance_file = LOGS_DIR / f"{run_id}_{log_suffix}_provenance_manifest.json"

    write_log(log_file, "=" * 80)
    write_log(log_file, f"Starting runner: run_id={run_id}, provider={args.provider}, combine_only={args.combine_only}")

    asset_manifest = build_asset_manifest()
    assert_runtime_matches_frozen(asset_manifest)

    if args.combine_only:
        provenance = {
            "run_id": run_id,
            "created_at": utc_now(),
            "mode": "combine_only",
            "environment": environment_manifest(),
            "assets": asset_manifest,
        }
        provenance_file.write_text(json.dumps(provenance, indent=2, ensure_ascii=False), encoding="utf-8")
        rebuild_combined_exports(run_id, log_file)
        write_log(log_file, "Combine-only export completed")
        return

    capability_probe = run_capability_probe(providers, log_file)

    provenance = {
        "run_id": run_id,
        "created_at": utc_now(),
        "mode": "inference",
        "provider_arg": args.provider,
        "providers": providers,
        "environment": environment_manifest(),
        "assets": asset_manifest,
        "capability_probe": capability_probe,
    }

    provenance_file.write_text(json.dumps(provenance, indent=2, ensure_ascii=False), encoding="utf-8")
    write_log(log_file, f"Provenance manifest saved: {provenance_file}")

    dataset = load_dataset()
    available_records = sorted(dataset.keys())
    selected_records = parse_records_arg(args.records, available_records)

    conditions = [
        ("conventional", RUNTIME_CONVENTIONAL_PROMPT),
        ("structured", RUNTIME_STRUCTURED_PROMPT),
    ]

    capabilities = {provider: capability_probe[provider] for provider in providers}

    total_expected = len(selected_records) * len(providers) * len(conditions)

    write_log(log_file, f"Records selected: {len(selected_records)}")
    write_log(log_file, f"Providers selected: {providers}")
    write_log(log_file, f"Total expected tasks: {total_expected}")

    counters = {
        "processed": 0,
        "success": 0,
        "parse_failure": 0,
        "api_failure": 0,
        "skipped": 0,
        "api_success_since_export": {provider: 0 for provider in providers},
    }

    start_time = time.time()

    for record_id in selected_records:
        description = dataset[record_id]

        for provider in providers:
            for condition, prompt_path in conditions:
                status = execute_task(
                    record_id=record_id,
                    description=description,
                    provider=provider,
                    condition=condition,
                    prompt_path=prompt_path,
                    run_id=run_id,
                    capability=capabilities[provider],
                    failure_file=failure_file,
                    log_file=log_file,
                )

                counters["processed"] += 1

                if status in {"success", "parse_failure", "api_failure", "skipped"}:
                    counters[status] += 1

                if status in {"success", "parse_failure"}:
                    counters["api_success_since_export"][provider] += 1

                if (
                    args.export_every > 0
                    and counters["api_success_since_export"][provider] >= args.export_every
                ):
                    rebuild_provider_exports(run_id, provider, log_file)
                    counters["api_success_since_export"][provider] = 0

                if counters["processed"] % args.heartbeat_every == 0:
                    elapsed_minutes = (time.time() - start_time) / 60
                    write_log(
                        log_file,
                        "HEARTBEAT "
                        f"processed={counters['processed']}/{total_expected}, "
                        f"success_this_session={counters['success']}, "
                        f"parse_failures_this_session={counters['parse_failure']}, "
                        f"api_failures_this_session={counters['api_failure']}, "
                        f"skipped_this_session={counters['skipped']}, "
                        f"elapsed_minutes={elapsed_minutes:.2f}"
                    )

    # Final provider-specific parquet/csv exports.
    for provider in providers:
        rebuild_provider_exports(run_id, provider, log_file)

    completed_for_selection = count_completed_for_task_list(
        selected_records=selected_records,
        providers=providers,
        conditions=conditions,
        run_id=run_id,
    )
    outstanding = total_expected - completed_for_selection

    write_log(log_file, "=" * 80)
    write_log(log_file, "Run completed")
    write_log(log_file, f"Total expected tasks for selected records/providers: {total_expected}")
    write_log(log_file, f"Canonical completed rows for selected records/providers: {completed_for_selection}")
    write_log(log_file, f"Outstanding incomplete tasks: {outstanding}")
    write_log(log_file, f"Success this session: {counters['success']}")
    write_log(log_file, f"Parse failures this session: {counters['parse_failure']}")
    write_log(log_file, f"API failures this session: {counters['api_failure']}")
    write_log(log_file, f"Skipped this session: {counters['skipped']}")
    write_log(log_file, f"Provider-specific results exported to: {RAW_RESULTS_DIR}")
    write_log(log_file, "=" * 80)

    if args.provider == "all":
        write_log(
            log_file,
            "Provider=all was used. You may now run --combine-only to build the combined results table."
        )


if __name__ == "__main__":
    main()
