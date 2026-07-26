import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


# ============================================================================
# Paths
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "main_study" / "datasets" / "raw"
JSON_CACHE_DIR = RAW_DIR / "nvd_json_pages"
OUTPUT_FILE = RAW_DIR / "main_candidate_pool_raw.xlsx"

AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"
LOG_FILE = AUDIT_DIR / "fetch_main_dataset_log.txt"

RAW_DIR.mkdir(parents=True, exist_ok=True)
JSON_CACHE_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Configuration
# ============================================================================

load_dotenv()

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_API_KEY = os.getenv("NVD_API_KEY")

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2026, 5, 25)

WINDOW_DAYS = 119
PAGE_SIZE = 2000

REQUEST_DELAY = 3 if NVD_API_KEY else 6
MAX_RETRIES = 5

EXCLUDED_STATUSES = {
    "Rejected",
    "Awaiting Analysis",
    "Undergoing Analysis",
}


# ============================================================================
# Utility functions
# ============================================================================

def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_log(message):
    timestamp = utc_now()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)


def iso_format(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def window_folder_name(start, end):
    return f"{start.date()}_to_{end.date()}"


def expected_severity(score):
    score = float(score)
    if score >= 9.0:
        return "CRITICAL"
    if score >= 7.0:
        return "HIGH"
    if score >= 4.0:
        return "MEDIUM"
    if score >= 0.1:
        return "LOW"
    return "NONE"


def load_manifest(manifest_path):
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return None


def save_manifest(manifest_path, manifest):
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


# ============================================================================
# CVSS and CPE extraction
# ============================================================================

def select_cvss_v31(cve):
    metrics = cve.get("metrics", {})
    cvss_items = metrics.get("cvssMetricV31", [])

    if not cvss_items:
        return None

    def usable(item):
        cvss_data = item.get("cvssData", {})
        vector = cvss_data.get("vectorString", "")
        return isinstance(vector, str) and vector.startswith("CVSS:3.1/") and cvss_data.get("baseScore") is not None

    usable_items = [item for item in cvss_items if usable(item)]
    if not usable_items:
        return None

    for item in usable_items:
        if str(item.get("type", "")).lower() == "primary":
            method = "primary_type"
            return item, method

    for item in usable_items:
        if str(item.get("source", "")).lower() == "nvd@nist.gov":
            method = "nvd_source"
            return item, method

    return usable_items[0], "fallback_first_available"


def extract_cpe_metadata(cve):
    vendors, products, uris = [], [], []
    seen_v, seen_p, seen_u = set(), set(), set()

    for config in cve.get("configurations", []):
        for node in config.get("nodes", []):
            for match in node.get("cpeMatch", []):
                uri = match.get("criteria", "")
                if not uri or not uri.startswith("cpe:2.3:"):
                    continue

                if uri not in seen_u:
                    uris.append(uri)
                    seen_u.add(uri)

                parts = uri.split(":")
                if len(parts) > 4:
                    vendor = parts[3]
                    product = parts[4]

                    if vendor and vendor not in ("*", "-") and vendor not in seen_v:
                        vendors.append(vendor)
                        seen_v.add(vendor)

                    if product and product not in ("*", "-") and product not in seen_p:
                        products.append(product)
                        seen_p.add(product)

    return vendors, products, uris


def extract_english_description(cve):
    descriptions = cve.get("descriptions", [])

    for d in descriptions:
        if d.get("lang") == "en":
            value = d.get("value", "")
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


# ============================================================================
# NVD fetch with cache and manifest
# ============================================================================

def fetch_page(params, headers):
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                NVD_API,
                params=params,
                headers=headers,
                timeout=90,
            )

            if response.status_code == 200:
                return response.json()

            last_error = f"HTTP {response.status_code}: {response.text[:300]}"

        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"

        wait = min(60, REQUEST_DELAY * (attempt + 2))
        write_log(f"Retry {attempt + 1}/{MAX_RETRIES} after error: {last_error}. Waiting {wait}s.")
        time.sleep(wait)

    raise RuntimeError(f"NVD request failed after retries: {last_error}")


def fetch_window(start, end):
    folder = JSON_CACHE_DIR / window_folder_name(start, end)
    folder.mkdir(parents=True, exist_ok=True)

    manifest_path = folder / "manifest.json"
    manifest = load_manifest(manifest_path)

    if manifest and manifest.get("complete") is True:
        write_log(f"Window already complete, using cache: {start.date()} to {end.date()}")
    else:
        write_log(f"Fetching window: {start.date()} to {end.date()}")

        headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}

        start_index = 0
        total_results = None
        downloaded_pages = manifest.get("downloaded_pages", []) if manifest else []

        while True:
            page_file = folder / f"page_{start_index:05d}.json"

            if page_file.exists():
                data = json.loads(page_file.read_text(encoding="utf-8"))
                write_log(f"Using cached page: {page_file}")
            else:
                params = {
                    "pubStartDate": iso_format(start),
                    "pubEndDate": iso_format(end),
                    "resultsPerPage": PAGE_SIZE,
                    "startIndex": start_index,
                }

                data = fetch_page(params, headers)
                page_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                write_log(f"Saved page: {page_file}")
                time.sleep(REQUEST_DELAY)

            if total_results is None:
                total_results = int(data.get("totalResults", 0))
                write_log(f"Window totalResults: {total_results}")

            page = data.get("vulnerabilities", [])
            if start_index not in downloaded_pages:
                downloaded_pages.append(start_index)

            start_index += len(page)

            manifest = {
                "window_start": str(start.date()),
                "window_end": str(end.date()),
                "total_results": total_results,
                "downloaded_pages": sorted(downloaded_pages),
                "records_downloaded_so_far": start_index,
                "complete": start_index >= total_results or not page,
                "last_updated_utc": utc_now(),
            }
            save_manifest(manifest_path, manifest)

            if start_index >= total_results or not page:
                break

    vulnerabilities = []
    for page_file in sorted(folder.glob("page_*.json")):
        data = json.loads(page_file.read_text(encoding="utf-8"))
        vulnerabilities.extend(data.get("vulnerabilities", []))

    return vulnerabilities


# ============================================================================
# Main candidate-pool construction
# ============================================================================

def build_candidate_rows(vulnerabilities):
    rows = []
    seen_cves = set()

    counters = {
        "total_seen": 0,
        "duplicates_skipped": 0,
        "excluded_status": 0,
        "missing_description": 0,
        "missing_cvss_v31": 0,
        "severity_none": 0,
        "eligible": 0,
        "fallback_cvss_used": 0,
    }

    excluded_status_counts = {}

    for item in vulnerabilities:
        counters["total_seen"] += 1

        cve = item.get("cve", {})
        cve_id = cve.get("id")

        if not cve_id:
            continue

        if cve_id in seen_cves:
            counters["duplicates_skipped"] += 1
            continue

        seen_cves.add(cve_id)

        vuln_status = cve.get("vulnStatus", "")

        if vuln_status in EXCLUDED_STATUSES:
            counters["excluded_status"] += 1
            excluded_status_counts[vuln_status] = excluded_status_counts.get(vuln_status, 0) + 1
            continue

        description = extract_english_description(cve)
        if not description:
            counters["missing_description"] += 1
            continue

        selected = select_cvss_v31(cve)
        if not selected:
            counters["missing_cvss_v31"] += 1
            continue

        cvss_item, selection_method = selected
        cvss_data = cvss_item.get("cvssData", {})

        vector = cvss_data.get("vectorString")
        base_score = cvss_data.get("baseScore")
        severity = expected_severity(base_score)

        if severity not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
            counters["severity_none"] += 1
            continue

        if selection_method == "fallback_first_available":
            counters["fallback_cvss_used"] += 1

        vendors, products, uris = extract_cpe_metadata(cve)

        rows.append({
            "cve_id": cve_id,
            "vuln_status": vuln_status,
            "published_date": cve.get("published"),
            "last_modified_date": cve.get("lastModified"),
            "original_description": description,
            "official_cvss_vector": vector,
            "official_base_score": base_score,
            "official_severity": severity,
            "cvss_source": cvss_item.get("source"),
            "cvss_type": cvss_item.get("type"),
            "cvss_version": cvss_data.get("version"),
            "cvss_selection_method": selection_method,
            "cpe_vendors": "|".join(vendors),
            "cpe_products": "|".join(products),
            "cpe_uris": "||".join(uris),
            "has_cpe": bool(vendors or products),
        })

        counters["eligible"] += 1

    return pd.DataFrame(rows), counters, excluded_status_counts


def main():
    LOG_FILE.write_text("", encoding="utf-8")

    write_log("=" * 80)
    write_log("Starting Main Study NVD candidate-pool fetch")
    write_log("=" * 80)
    write_log(f"NVD API key loaded: {bool(NVD_API_KEY)}")
    write_log(f"Date window: {START_DATE.date()} to {END_DATE.date()}")
    write_log(f"Window days: {WINDOW_DAYS}")
    write_log(f"Page size: {PAGE_SIZE}")

    all_vulnerabilities = []
    current_start = START_DATE

    while current_start <= END_DATE:
        current_end = min(current_start + timedelta(days=WINDOW_DAYS), END_DATE)
        window_items = fetch_window(current_start, current_end)
        all_vulnerabilities.extend(window_items)

        write_log(f"Fetched/cached window records: {len(window_items)}")
        current_start = current_end + timedelta(days=1)

    write_log(f"Total raw vulnerability items loaded from cached pages: {len(all_vulnerabilities)}")

    candidate_df, counters, excluded_status_counts = build_candidate_rows(all_vulnerabilities)

    # ============================================================================
    # Save outputs
    # ============================================================================

    PARQUET_FILE = RAW_DIR / "main_candidate_pool_raw.parquet"
    CSV_FILE = RAW_DIR / "main_candidate_pool_raw.csv"

    candidate_df.to_parquet(PARQUET_FILE, index=False)
    candidate_df.to_csv(CSV_FILE, index=False, encoding="utf-8")
    candidate_df.to_excel(OUTPUT_FILE, index=False)

    write_log(f"Saved Parquet: {PARQUET_FILE}")
    write_log(f"Saved CSV: {CSV_FILE}")
    write_log(f"Saved Excel: {OUTPUT_FILE}")

    write_log("=" * 80)
    write_log("Candidate Pool Summary")
    write_log("=" * 80)
    write_log(f"Output file: {OUTPUT_FILE}")
    write_log(f"Total raw items seen: {counters['total_seen']}")
    write_log(f"Eligible CVEs retained: {counters['eligible']}")
    write_log(f"Duplicates skipped: {counters['duplicates_skipped']}")
    write_log(f"Excluded by status: {counters['excluded_status']}")
    write_log(f"Missing English description: {counters['missing_description']}")
    write_log(f"Missing usable CVSS v3.1: {counters['missing_cvss_v31']}")
    write_log(f"Severity NONE skipped: {counters['severity_none']}")
    write_log(f"Fallback CVSS selections used: {counters['fallback_cvss_used']}")

    write_log(f"Excluded status counts: {excluded_status_counts}")

    if not candidate_df.empty:
        write_log("\nSeverity distribution:")
        write_log(str(candidate_df["official_severity"].value_counts()))

        candidate_df["published_year"] = pd.to_datetime(
            candidate_df["published_date"], errors="coerce"
        ).dt.year

        write_log("\nPublication year distribution:")
        write_log(str(candidate_df["published_year"].value_counts().sort_index()))

        write_log("\nCPE coverage:")
        write_log(str(candidate_df["has_cpe"].value_counts()))

        write_log("\nCVSS selection method distribution:")
        write_log(str(candidate_df["cvss_selection_method"].value_counts()))

    write_log("=" * 80)
    write_log("Main Study NVD candidate-pool fetch complete")
    write_log("=" * 80)


if __name__ == "__main__":
    main()