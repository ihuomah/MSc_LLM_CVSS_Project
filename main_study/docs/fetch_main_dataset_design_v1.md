# Fetch Main Dataset Design v1

## Purpose

This document defines the design for:

`main_study/scripts/fetch_main_dataset.py`

This script constructs the raw Main Study candidate pool from NVD.

It performs a census-style fetch only.

It must not sample records, enrich EPSS, exclude pilot CVEs, or sanitise descriptions.

---

# Script Name

`fetch_main_dataset.py`

---

# Script Location

`main_study/scripts/fetch_main_dataset.py`

---

# Input Sources

## NVD API

Source:

`https://services.nvd.nist.gov/rest/json/cves/2.0`

Date window:

`2023-01-01` to `2026-05-25`

API key:

Loaded from `.env` using:

`NVD_API_KEY`

---

# Eligibility Rules

A CVE is eligible for the raw candidate pool if it meets all of the following:

1. It is returned by the NVD CVE API within the defined publication date window.
2. It has a usable English vulnerability description.
3. It has CVSS v3.1 data.
4. The CVSS v3.1 vector starts with `CVSS:3.1/`.
5. It has a CVSS v3.1 base score.
6. Its derived severity falls into one of:

   * CRITICAL
   * HIGH
   * MEDIUM
   * LOW

---

# CVSS Ground Truth Rule

The script shall prioritise NVD Primary CVSS v3.1 metrics as the ground-truth source.

If multiple CVSS v3.1 records exist for a CVE, the script shall prefer:

1. CVSS v3.1 where `type = Primary`
2. CVSS v3.1 where `source = nvd@nist.gov`
3. Otherwise, the first available CVSS v3.1 record shall be retained with a flag for review

The selected CVSS source information shall be stored for auditability.

---

# CVE Status Rule

The script shall exclude rejected CVEs.

The script shall record the CVE vulnerability status where available.

CVEs without usable CVSS v3.1 data shall not enter the raw candidate pool.

---

# CPE Extraction Rule

The script shall extract CPE metadata from each CVE configuration.

For each CPE 2.3 URI:

`cpe:2.3:<part>:<vendor>:<product>:<version>:...`

the script shall extract:

* vendor token
* product token
* full CPE URI

CPE values shall be stored as:

* `cpe_vendors`
* `cpe_products`
* `cpe_uris`
* `has_cpe`

---

# Output Dataset

Primary output:

`main_study/datasets/raw/main_candidate_pool_raw.xlsx`

Required columns:

* `cve_id`
* `vuln_status`
* `published_date`
* `last_modified_date`
* `original_description`
* `official_cvss_vector`
* `official_base_score`
* `official_severity`
* `cvss_source`
* `cvss_type`
* `cvss_version`
* `cpe_vendors`
* `cpe_products`
* `cpe_uris`
* `has_cpe`

---

# Raw JSON Cache

The script shall also cache raw NVD API pages.

Output folder:

`main_study/datasets/raw/nvd_json_pages/`

Each page shall be saved as JSON for audit and reproducibility.

This prevents loss of progress during long NVD pulls and supports later inspection without re-querying NVD.

---

# Checkpoint / Resume Rule

The script shall support resume behaviour.

If a raw JSON page has already been downloaded, the script should reuse it rather than downloading it again.

This protects the process from interruption during long API retrieval.

---

# Pagination Rule

The script shall use NVD pagination.

Recommended page size:

`2000`

The script shall continue fetching until all pages in each date window are retrieved.

---

# Rate Limit Rule

The script shall use API-key based requests where available.

If API errors occur, the script shall retry after a backoff delay.

Failed windows or pages must be logged.

---

# Audit Outputs

The script shall generate an audit log:

`main_study/audit/fetch_main_dataset_log.txt`

The log shall include:

* start timestamp
* end timestamp
* date window
* NVD API key loaded status
* total records fetched from NVD
* total eligible CVSS v3.1 records retained
* severity distribution
* by-year distribution
* number with CPE metadata
* number without CPE metadata
* number of rejected records skipped
* any failed pages or retry events

---

# Candidate Pool Measurements

The script shall print and log:

## Severity Distribution

* CRITICAL
* HIGH
* MEDIUM
* LOW

## Year Distribution

Counts grouped by publication year.

## CPE Coverage

* records with CPE
* records without CPE

---

# Non-Responsibilities

This script must not:

* sample the dataset
* exclude pilot CVEs
* download or merge EPSS
* sanitise descriptions
* create inference input
* create record mappings
* run any model
* perform accuracy analysis

---

# Status

Version: v1

Status: Design Frozen Pending Implementation


# Additional Frozen Fetch Decisions

## Eligibility Rule

A CVE is eligible for the raw Main Study candidate pool only if it satisfies all of the following:

1. It is returned by the NVD CVE API using publication-date filtering.
2. It is not rejected.
3. It has a usable English description.
4. It has CVSS v3.1 data.
5. The selected CVSS v3.1 vector starts with `CVSS:3.1/`.
6. The selected CVSS v3.1 record has a base score.
7. The derived severity is one of:

   * CRITICAL
   * HIGH
   * MEDIUM
   * LOW

## CVSS Primary/Secondary Rule

The script shall prioritise NVD Primary CVSS v3.1 metrics.

Selection order:

1. Use CVSS v3.1 where `type = Primary`.
2. If no Primary v3.1 record exists, use a v3.1 record where `source = nvd@nist.gov`.
3. If neither exists, use the first available CVSS v3.1 record and flag it as a fallback.

The script shall store:

* `cvss_source`
* `cvss_type`
* `cvss_selection_method`

This ensures that any non-primary or fallback CVSS selection remains auditable.

## Status Exclusion Rule

The script shall explicitly exclude CVEs with vulnerability status indicating that they are not suitable for scoring analysis, including:

* Rejected
* Awaiting Analysis
* Undergoing Analysis

The script shall record excluded-status counts in the audit log.

## Fetch Scope Rule

The script shall fetch each publication-date window without severity filtering.

The script shall not use `cvssV3Severity` as an API query filter.

Filtering shall be performed client-side after the raw NVD JSON pages have been cached.

This allows the audit log to record both:

* total CVEs returned by NVD
* total CVEs retained after eligibility filtering

## Date Filter Rule

The script shall use:

* `pubStartDate`
* `pubEndDate`

The script shall not use `lastModStartDate` or `lastModEndDate` for candidate pool construction.

Publication date is used because it is more stable for defining the study population.

## Resume and Completion Marker Rule

Raw JSON page caching alone is not sufficient for resume safety.

Each date window shall have a manifest file recording:

* window start date
* window end date
* total results reported by NVD
* page start indexes downloaded
* number of records downloaded
* completion status
* timestamp completed

A window shall only be skipped during resume if its manifest states that the window is complete.

Partial windows shall be resumed or refetched rather than silently skipped.

## Measurement Scope Rule

The fetch script shall record light candidate-pool measurements only:

* total fetched
* total eligible
* severity distribution
* publication-year distribution
* CPE coverage

Detailed feasibility analysis, EPSS coverage, and sampling decisions shall be handled by later scripts.
