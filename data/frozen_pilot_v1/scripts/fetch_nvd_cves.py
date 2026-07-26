"""
NVD fetch script — upgraded to capture CPE vendor/product metadata for
per-record (CPE-driven) sanitisation, with pagination for the full run.

New columns vs. previous version:
    cpe_vendors   : unique vendor tokens from this CVE's CPE configs (|-joined)
    cpe_products  : unique product tokens from this CVE's CPE configs (|-joined)
    cpe_uris      : raw CPE 2.3 URIs (||-joined) — kept for audit/reproducibility

CPE 2.3 URI format (13 colon-separated fields):
    cpe:2.3:<part>:<vendor>:<product>:<version>:<update>:<edition>:...
    index:  0   1     2        3         4          5
So vendor = field 3, product = field 4, version = field 5.
Tokens are NVD-normalised: lowercase, '_' for spaces, '\\' escaping.
"""

import time
from datetime import datetime, timedelta
import requests
import pandas as pd

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# Optional: put your NVD API key here (or load from env) to lift rate limits.
NVD_API_KEY = ""   # e.g. "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2026, 5, 25)
WINDOW_DAYS = 119

SEVERITY_TARGETS = {
    "CRITICAL": 10,
    "HIGH": 15,
    "MEDIUM": 15,
    "LOW": 10,
}

RANDOM_SEED = 42
PAGE_SIZE = 2000
REQUEST_DELAY = 6   # seconds; 6 is safe for keyless. ~0.6 ok with a key.


def iso_format(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def expected_severity(score):
    score = float(score)
    if score >= 9.0:
        return "CRITICAL"
    elif score >= 7.0:
        return "HIGH"
    elif score >= 4.0:
        return "MEDIUM"
    elif score >= 0.1:
        return "LOW"
    return "NONE"


def extract_cvss_v31(cve):
    metrics = cve.get("metrics", {})
    if "cvssMetricV31" not in metrics:
        return None
    metric = metrics["cvssMetricV31"][0]
    cvss_data = metric.get("cvssData", {})
    vector_string = cvss_data.get("vectorString", "")
    if not vector_string.startswith("CVSS:3.1/"):
        return None
    return cvss_data


def extract_cpe_metadata(cve):
    """Walk the CVE's configurations and collect vendor/product tokens + URIs.

    Returns (vendors_list, products_list, uris_list), each de-duplicated and
    order-preserved. Tokens stay in NVD-normalised form here; the sanitiser
    de-normalises them when matching against the description.
    """
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
                # parts[3] = vendor, parts[4] = product
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


def fetch_window(start, end):
    """Fetch all matching vulnerabilities in a date window, paginated."""
    headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}
    collected = []
    start_index = 0
    total = None

    while True:
        params = {
            "pubStartDate": iso_format(start),
            "pubEndDate": iso_format(end),
            "resultsPerPage": PAGE_SIZE,
            "startIndex": start_index,
        }
        resp = requests.get(NVD_API, params=params, headers=headers, timeout=60)
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code} at startIndex={start_index}; "
                  f"retrying once after backoff.")
            time.sleep(REQUEST_DELAY * 2)
            resp = requests.get(NVD_API, params=params, headers=headers, timeout=60)
            if resp.status_code != 200:
                print(f"  Still failing; skipping rest of this window.")
                break

        data = resp.json()
        if total is None:
            total = data.get("totalResults", 0)
            print(f"  totalResults in window: {total}")

        page = data.get("vulnerabilities", [])
        collected.extend(page)
        start_index += len(page)

        time.sleep(REQUEST_DELAY)
        if start_index >= (total or 0) or not page:
            break

    return collected


def main():
    all_candidates = []
    seen_cves = set()
    current_start = START_DATE

    while current_start <= END_DATE:
        current_end = min(current_start + timedelta(days=WINDOW_DAYS), END_DATE)
        print(f"\nSearching window: {current_start.date()} to {current_end.date()}")

        for item in fetch_window(current_start, current_end):
            cve = item.get("cve", {})
            cve_id = cve.get("id", "N/A")
            if cve_id in seen_cves:
                continue

            cvss_data = extract_cvss_v31(cve)
            if not cvss_data:
                continue
            base_score = cvss_data.get("baseScore", None)
            vector_string = cvss_data.get("vectorString", "")
            if base_score is None:
                continue
            severity = expected_severity(base_score)
            if severity not in SEVERITY_TARGETS:
                continue

            descriptions = cve.get("descriptions", [])
            # prefer the English description explicitly
            description = "N/A"
            for d in descriptions:
                if d.get("lang") == "en":
                    description = d.get("value", "N/A")
                    break
            else:
                if descriptions:
                    description = descriptions[0].get("value", "N/A")

            vendors, products, uris = extract_cpe_metadata(cve)

            all_candidates.append({
                "cve_id": cve_id,
                "original_description": description,
                "cpe_vendors": "|".join(vendors),
                "cpe_products": "|".join(products),
                "cpe_uris": "||".join(uris),
                "has_cpe": bool(vendors or products),
                "official_cvss_vector": vector_string,
                "official_base_score": base_score,
                "official_severity": severity,
                "published_date": cve.get("published", "N/A"),
            })
            seen_cves.add(cve_id)

        print(f"Candidates collected so far: {len(all_candidates)}")
        current_start = current_end + timedelta(days=1)

    candidate_df = pd.DataFrame(all_candidates)
    if candidate_df.empty:
        print("\nNo CVEs collected.")
        return

    print("\nCandidate severity distribution:")
    print(candidate_df["official_severity"].value_counts())
    print("\nCVEs with CPE metadata:",
          int(candidate_df["has_cpe"].sum()), "of", len(candidate_df))

    sampled_frames = []
    for severity, target_count in SEVERITY_TARGETS.items():
        severity_df = candidate_df[candidate_df["official_severity"] == severity]
        if len(severity_df) < target_count:
            print(f"\nWarning: only {len(severity_df)} {severity} CVEs available.")
            sampled = severity_df
        else:
            sampled = severity_df.sample(n=target_count, random_state=RANDOM_SEED)
        sampled_frames.append(sampled)

    final_df = (
        pd.concat(sampled_frames)
        .sample(frac=1, random_state=RANDOM_SEED)
        .reset_index(drop=True)
    )

    output_path = "data/raw/nvd_pilot_raw.xlsx"
    final_df.to_excel(output_path, index=False)
    print(f"\nSaved {len(final_df)} CVEs to: {output_path}")
    print("\nFinal severity distribution:")
    print(final_df["official_severity"].value_counts())
    print("\nCVEs missing CPE (will need backstop/review):",
          int((~final_df["has_cpe"]).sum()))


if __name__ == "__main__":
    main()