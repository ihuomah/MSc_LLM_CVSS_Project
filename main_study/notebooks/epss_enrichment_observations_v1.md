# EPSS Enrichment Observations v1

## Date

2026-06-20

---

# Context

EPSS enrichment was performed using:

`enrich_main_with_epss.py`

Input dataset:

`main_candidate_pool_raw.parquet`

Output dataset:

`main_candidate_pool_with_epss.parquet`

The purpose of this stage was to merge EPSS scores with the full Main Study candidate pool and confirm whether EPSS coverage supports the intended sampling strategy.

---

# EPSS Snapshot

EPSS source:

FIRST EPSS daily CSV

Local file:

`main_study/datasets/raw/epss/epss_scores-current.csv.gz`

Enrichment timestamp:

2026-06-20T00:03:07Z

---

# Overall EPSS Coverage

| Total Records | Has EPSS | Missing EPSS | Coverage |
| ------------: | -------: | -----------: | -------: |
|       134,789 |  134,789 |            0 |   100.0% |

## Observation

EPSS coverage is complete for the full Main Study candidate pool.

No candidate records were missing EPSS scores.

---

# EPSS Coverage by Severity

| Severity | Total Records | Has EPSS | Missing EPSS | Coverage |
| -------- | ------------: | -------: | -----------: | -------: |
| Critical |        18,415 |   18,415 |            0 |   100.0% |
| High     |        49,563 |   49,563 |            0 |   100.0% |
| Medium   |        63,865 |   63,865 |            0 |   100.0% |
| Low      |         2,946 |    2,946 |            0 |   100.0% |

## Observation

EPSS coverage is complete across all severity strata.

This confirms that EPSS availability does not constrain severity-balanced sampling.

---

# EPSS Coverage by Publication Year

| Year | Total Records | Has EPSS | Missing EPSS | Coverage |
| ---- | ------------: | -------: | -----------: | -------: |
| 2023 |        28,669 |   28,669 |            0 |   100.0% |
| 2024 |        38,769 |   38,769 |            0 |   100.0% |
| 2025 |        43,925 |   43,925 |            0 |   100.0% |
| 2026 |        23,426 |   23,426 |            0 |   100.0% |

## Observation

EPSS coverage is complete across all publication years in the candidate pool.

---

# EPSS Coverage by CVSS Selection Method

| CVSS Selection Method    | Total Records | Has EPSS | Missing EPSS | Coverage |
| ------------------------ | ------------: | -------: | -----------: | -------: |
| fallback_first_available |        59,933 |   59,933 |            0 |   100.0% |
| nvd_source               |           599 |      599 |            0 |   100.0% |
| primary_type             |        74,257 |   74,257 |            0 |   100.0% |

## Observation

EPSS coverage is complete for both NVD-grounded and Secondary CVSS records.

The decision to restrict the experimental sampling pool to NVD-grounded records is therefore not constrained by EPSS availability.

---

# NVD-Grounded EPSS Coverage

NVD-grounded records are defined as records where:

* `cvss_selection_method = primary_type`
* `cvss_selection_method = nvd_source`

| Total Records | Has EPSS | Missing EPSS | Coverage |
| ------------: | -------: | -----------: | -------: |
|        74,856 |   74,856 |            0 |   100.0% |

## Observation

The NVD-grounded sampling pool has full EPSS coverage.

This confirms that the Main Study can use NVD-grounded CVSS v3.1 records while still supporting RQ3, which requires EPSS.

---

# NVD-Grounded EPSS Coverage by Severity

| Severity | Total Records | Has EPSS | Missing EPSS | Coverage |
| -------- | ------------: | -------: | -----------: | -------: |
| Critical |        12,270 |   12,270 |            0 |   100.0% |
| High     |        26,242 |   26,242 |            0 |   100.0% |
| Medium   |        35,257 |   35,257 |            0 |   100.0% |
| Low      |         1,087 |    1,087 |            0 |   100.0% |

## Key Feasibility Finding

The smallest NVD-grounded severity stratum is Low severity:

`Low ∩ NVD-grounded ∩ EPSS = 1,087`

This exceeds the target requirement of 250 Low-severity records.

Therefore, the intended balanced sample of 1,000 CVEs is feasible using only NVD-grounded, EPSS-covered records.

---

# Sampling Implication

The Main Study can proceed with the following sampling rule:

Use only records where:

* `is_nvd_grounded = True`
* `has_epss = True`

Then apply stratified random sampling by official severity.

Proposed final sample:

| Severity | Target |
| -------- | -----: |
| Critical |    250 |
| High     |    250 |
| Medium   |    250 |
| Low      |    250 |
| Total    |  1,000 |

---

# Methodological Implication

The EPSS enrichment stage confirms that there is no need to include Secondary CVSS records in the main experimental sample.

The study can preserve the cleaner ground-truth rule:

`NVD-grounded CVSS v3.1 only`

while also retaining complete EPSS coverage for correlation analysis.

This keeps the Main Study aligned with the frozen methodology and avoids mixing NVD Primary assessments with CNA/vendor Secondary assessments.

---

# Outputs Created

## Enriched Dataset

`main_study/datasets/processed/main_candidate_pool_with_epss.parquet`

`main_study/datasets/processed/main_candidate_pool_with_epss.csv`

## Audit Outputs

`main_study/audit/main_epss_enrichment_log.txt`

`main_study/audit/main_epss_coverage_summary.xlsx`

---

# Status

Version: v1

Status: EPSS Enrichment Complete
