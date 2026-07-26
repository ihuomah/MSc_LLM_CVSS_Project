# Candidate Pool Observations v1

## Date

2026-06-19

---

# Context

The raw Main Study candidate pool was generated using:

`fetch_main_dataset.py`

Date window:

2023-01-01 to 2026-05-25

The purpose of this notebook entry is to record observations from the candidate-pool construction stage prior to EPSS enrichment and sampling.

---

# Candidate Pool Summary

## Raw NVD Records Examined

147,602

## Eligible CVEs Retained

134,789

## Rejected or Excluded

12,813

Breakdown:

* Rejected: 5,856
* Awaiting Analysis: 977
* Undergoing Analysis: 15
* Missing usable CVSS v3.1: 5,962
* Severity NONE: 3

---

# Severity Distribution

| Severity |  Count |
| -------- | -----: |
| Critical | 18,415 |
| High     | 49,563 |
| Medium   | 63,865 |
| Low      |  2,946 |

## Observation

The candidate pool contains sufficient CVEs across all severity levels to support a balanced sampling strategy.

Low-severity CVEs represent the smallest stratum but still contain substantially more records than any currently anticipated sample requirement.

---

# Publication Year Distribution

| Year |  Count |
| ---- | -----: |
| 2023 | 28,669 |
| 2024 | 38,769 |
| 2025 | 43,925 |
| 2026 | 23,426 |

## Observation

Eligible CVEs are present across all years within the study period.

The candidate pool has broad year coverage. However, subsequent inspection revealed that CVSS source composition varies substantially by publication year, requiring consideration during sampling and interpretation.

---

# CPE Coverage

| Has CPE |   Count |
| ------- | ------: |
| True    | 105,823 |
| False   |  28,966 |

## Observation

Approximately 78.5% of eligible CVEs contain CPE metadata.

This level of coverage is expected to support automated sanitisation for the majority of records.

A significant minority of CVEs lack CPE metadata and may require additional review during the sanitisation phase.

---

# CVSS Selection Method Distribution

| Selection Method         |  Count |
| ------------------------ | -----: |
| primary_type             | 74,257 |
| fallback_first_available | 59,933 |
| nvd_source               |    599 |

---

## CVSS Source Distribution Finding

Inspection of the candidate pool revealed a strong relationship between publication year and CVSS selection method.

Older CVEs (2023) were predominantly associated with NVD Primary CVSS v3.1 assessments, whereas more recent CVEs (2025–2026) increasingly relied on fallback CVSS assessments.

Follow-up inspection confirmed that fallback records consist of Secondary CVSS v3.1 assessments supplied by CNAs, vendors, and security advisory organisations rather than NVD Primary assessments.

This indicates that NVD analysis backlog significantly influences the composition of the candidate pool, particularly for more recent publication years.

Status: Resolved

---

### Supporting Evidence and Scope

NVD Primary CVSS v3.1 coverage declines by publication year:

* 2023 ≈ 93%
* 2024 ≈ 60%
* 2025 ≈ 38%
* 2026 ≈ 36%

This pattern is consistent with the known NVD analysis backlog.

Restricting ground truth to NVD-grounded records therefore skews the sampleable pool toward 2023–2024.

Decision:

Sampling will stratify on severity only.

Publication year will be reported as a descriptive characteristic rather than a controlled sampling dimension.

No year-based stratification is applied because recent NVD-grounded strata become increasingly sparse (for example, Low severity 2026 contains only 123 NVD-grounded records), making balanced year stratification impractical.

Study scope:

The Main Study population is defined as:

"CVEs with NVD-analyst-reviewed CVSS v3.1 assessments."

CVEs scored only by CNAs and CVEs awaiting NVD analysis are considered outside the preferred experimental sampling population.

NVD's analysis queue may not be random and therefore represents a potential external-validity limitation.

---

## Fallback CVSS Detail Finding

Inspection of fallback-selected records confirmed that fallback selection does not introduce CVSS v2 or CVSS v3.0 metrics.

All fallback-selected records were found to contain:

* CVSS Version = 3.1
* CVSS Type = Secondary

The largest fallback sources included:

* Patchstack
* Wordfence
* GitHub Security Advisories
* VulDB
* Microsoft
* Adobe
* Oracle
* Cisco
* IBM
* Intel
* Various CNA and vendor security advisories

This confirms that fallback-selected records remain valid CVSS v3.1 assessments but are not NVD Primary assessments.

### Implication

The candidate pool contains two distinct CVSS populations:

#### NVD-grounded assessments

* primary_type
* nvd_source

#### Secondary assessments

* fallback_first_available

Because the dissertation protocol defines ground truth as NVD-assigned CVSS v3.1 assessments, Secondary CVSS records are not currently considered part of the preferred experimental sampling pool.

Status: Resolved

---

## Tentative Ground Truth Decision

Main Study sampling is expected to be restricted to:

* primary_type
* nvd_source

unless EPSS coverage analysis reveals an unexpected constraint.

The full candidate pool remains frozen and will be retained for auditability and descriptive analysis.

Fallback Secondary CVSS v3.1 records remain part of the frozen candidate pool but are not currently planned for inclusion in the main experimental sample.

Status: Pending confirmation during EPSS integration.

---

## Observation

Diagnostic review confirmed that the CVSS selection logic is functioning correctly.

The high fallback rate is not caused by script error.

Instead, it reflects the growing proportion of CVEs that currently contain Secondary CVSS v3.1 assessments without corresponding NVD Primary assessments.

This effect becomes increasingly pronounced in more recent publication years and is consistent with the observed NVD analysis backlog.

### Implication

Ground-truth selection must be treated as a methodological decision rather than a data-processing decision.

Status: Resolved

---

# Excel Export Observation

During export of the raw candidate pool, multiple warnings were generated indicating that some cell contents exceeded Excel's maximum cell size of 32,767 characters.

These warnings originated primarily from:

* cpe_products
* cpe_uris

which may contain extremely large lists of CPE entries.

### Additional Observation

The raw NVD JSON cache was successfully preserved.

The JSON cache occupies approximately 1.19 GB and contains all raw NVD responses used to construct the candidate pool.

Due to Excel cell-length limitations, some `cpe_products` and `cpe_uris` values were truncated during XLSX export.

The JSON cache therefore remains the authoritative source for complete CPE information.

The exported XLSX remains suitable for manual inspection only.

Authoritative dataset preservation is provided by:

* main_candidate_pool_raw.parquet
* main_candidate_pool_raw.csv

---

## Implication

The Excel export should not be considered a complete preservation of raw CPE information.

The Parquet file, CSV file, and raw JSON cache remain the authoritative preservation artefacts.

The impact on sanitisation is expected to be minimal because sanitisation primarily relies on:

* cpe_vendors
* cpe_products
* has_cpe

rather than the full URI list.

---

# Actions

## Completed

* Candidate pool construction completed.
* Raw NVD pages cached.
* Candidate pool audit log generated.
* CVSS source distribution analysed.
* Fallback source analysis completed.
* Candidate pool preserved in Parquet and CSV formats.

## Pending

* Perform EPSS enrichment on the full candidate pool.
* Measure EPSS coverage overall.
* Measure EPSS coverage by severity.
* Measure EPSS coverage by publication year.
* Measure EPSS coverage for NVD-grounded records only.
* Confirm feasibility of the Primary-only sampling pool.

---

# Status

Version: v1

Status: Open Observation Record
