# Main Sampling Observations v1

## Date

2026-06-20

---

# Context

Sampling was performed using:

`sample_main_dataset.py`

Input dataset:

`main_candidate_pool_with_epss.parquet`

The purpose of this stage was to create the frozen Main Study dataset used for all subsequent sanitisation, inference, and analysis activities.

The sampling procedure followed the frozen Main Dataset Specification and applied:

* NVD-grounded filtering
* EPSS-covered filtering
* Pilot-study exclusion
* Stratified random sampling
* Fixed random seed (42)

---

# Sampling Pool Construction

## Enriched Candidate Pool

| Metric                 |   Count |
| ---------------------- | ------: |
| Candidate Pool Records | 134,789 |

## NVD-Grounded and EPSS-Covered Pool

| Metric                      |  Count |
| --------------------------- | -----: |
| NVD-Grounded + EPSS-Covered | 74,856 |

### Observation

The NVD-grounded subset retained 74,856 records after application of the ground-truth eligibility rule.

This confirms that the Main Study can operate using NVD-reviewed CVSS v3.1 assessments while maintaining complete EPSS coverage.

---

# Pilot Study Exclusion

## Pilot Records Loaded

| Metric            | Count |
| ----------------- | ----: |
| Pilot CVEs Loaded |    50 |

## Pilot Exclusion Results

| Metric                                  | Count |
| --------------------------------------- | ----: |
| Pilot CVEs Found and Excluded           |    29 |
| Pilot CVEs Not Present in Sampling Pool |    21 |

### Observation

Only 29 of the 50 pilot-study CVEs were present in the NVD-grounded sampling pool.

The remaining 21 pilot CVEs were absent because they were associated with fallback CVSS assessments and therefore did not satisfy the NVD-grounded eligibility rule.

This finding confirms that the pilot dataset contained a mixture of NVD Primary and Secondary CVSS v3.1 assessments.

---

# Pilot Ground-Truth Refinement Finding

A follow-up inspection of pilot-study CVEs produced the following result:

| CVSS Selection Method    | Count |
| ------------------------ | ----: |
| primary_type             |    29 |
| fallback_first_available |    21 |

### Observation

The pilot dataset used mixed ground truth:

* 29 NVD Primary assessments
* 21 Secondary (fallback) assessments

The Main Study uses a refined ground-truth definition:

`NVD-grounded CVSS v3.1 only`

This refinement was introduced after analysis of the candidate pool and fallback-assessment behaviour.

The pilot therefore served its intended methodological purpose by identifying a source of ground-truth heterogeneity prior to full-scale experimentation.

---

# Sampling Pool After Pilot Exclusion

| Severity | Available Records |
| -------- | ----------------: |
| Critical |            12,261 |
| High     |            26,235 |
| Medium   |            35,247 |
| Low      |             1,084 |

### Observation

All severity strata substantially exceeded the required sample size of 250 records.

The Low-severity stratum remained the smallest category but still contained more than four times the required sample size.

---

# Frozen Main Sample

## Target Sampling Design

| Severity | Target |
| -------- | -----: |
| Critical |    250 |
| High     |    250 |
| Medium   |    250 |
| Low      |    250 |

## Actual Sample Obtained

| Severity | Sampled |
| -------- | ------: |
| Critical |     250 |
| High     |     250 |
| Medium   |     250 |
| Low      |     250 |
| Total    |   1,000 |

### Observation

The sampling process successfully produced the intended balanced dataset of 1,000 CVEs.

No fallback or rebalancing procedures were required.

---

# Publication Year Distribution

| Year | Count |
| ---- | ----: |
| 2023 |   375 |
| 2024 |   305 |
| 2025 |   207 |
| 2026 |   113 |

### Observation

The sampled dataset is weighted toward 2023–2024 publications.

This pattern was anticipated during candidate-pool analysis and reflects the declining availability of NVD Primary CVSS assessments in more recent years.

No year-based stratification was applied.

Publication year will therefore be reported as a descriptive characteristic of the final sample rather than as a controlled sampling factor.

---

# CVSS Source Distribution

| CVSS Selection Method    | Count |
| ------------------------ | ----: |
| primary_type             |   993 |
| nvd_source               |     7 |
| fallback_first_available |     0 |

### Observation

No fallback CVSS assessments were included in the final sample.

All sampled records satisfy the NVD-grounded eligibility rule established during candidate-pool review.

---

# Frozen Dataset Outputs

## Authoritative Datasets

* `main_dataset_frozen_v1.parquet`
* `main_dataset_frozen_v1.csv`

## Convenience Dataset

* `main_dataset_frozen_v1.xlsx`

### Observation

Excel export generated expected truncation warnings for extremely large `cpe_uris` fields.

Verification confirmed that:

* Parquet retains complete CPE information
* CSV retains complete CPE information
* Excel truncates values exceeding 32,767 characters

The Parquet and CSV files remain the authoritative frozen dataset artefacts.

---

# Reproducibility Information

Random seed:

`42`

Sampling method:

`Stratified random sampling by official severity`

Ground-truth eligibility rule:

`NVD-grounded CVSS v3.1 only`

Pilot exclusion:

`Applied`

EPSS requirement:

`Applied`

---

# Phase Outcome

The Main Study frozen dataset was successfully generated and frozen.

The dataset satisfies:

* Balanced severity representation
* NVD-grounded CVSS v3.1 assessments
* Complete EPSS coverage
* Pilot-study independence
* Reproducible sampling

The dataset is approved for Phase 5 sanitisation.

---

# Status

Version: v1

Status: Frozen Dataset Created
