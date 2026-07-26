# Main Dataset Specification v1

## Dissertation

**Title:**

Evaluating the Reliability of LLM-Based Vulnerability Scoring using the Common Vulnerability Scoring System (CVSS) and the Exploit Prediction Scoring System (EPSS)

---

# Purpose

This document defines the dataset specification for the Main Study.

Unlike the protocol document, which defines the workflow, this specification records the actual dataset characteristics selected for the experiment.

This document shall be updated as candidate-pool measurements are performed and decisions are finalised.

---

# Status

Version: v1

Status: Draft – Pending Candidate Pool Measurement

---

# Candidate Pool Definition

Source:

NVD CVE API v2.0

Date Window:

2023-01-01 to 2026-05-25

CVSS Requirement:

* Must contain CVSS v3.1 metrics
* Must contain CVSS v3.1 vector string
* Must contain CVSS v3.1 base score

Ground Truth:

Primary NVD CVSS v3.1 assessment

CPE Metadata:

The following fields shall be collected:

* cpe_vendors
* cpe_products
* cpe_uris
* has_cpe

---

# EPSS Integration

Source:

FIRST EPSS Daily CSV

Required Fields:

* epss_score
* epss_percentile
* has_epss
* epss_date
* epss_source

EPSS Snapshot Date:

TBD

EPSS Coverage:

TBD

EPSS Coverage by Severity:

TBD

EPSS Inclusion Rule:

TBD

Decision will be made after candidate-pool measurement and EPSS coverage analysis.

---

# Pilot Independence Rule

The 50 CVEs used in the pilot study shall be excluded from the Main Study candidate pool prior to final sampling.

Pilot Mapping Source:

pilot_record_id_verification_v2.xlsx

Pilot Exclusion Status:

Pending

---

# Sampling Strategy

Sampling Method:

Stratified random sampling

Random Seed:

42

Target Sample Size:

TBD

Severity Distribution:

TBD

Rationale:

Final sample size and severity distribution shall be selected after candidate-pool measurement and feasibility assessment.

---

# Reproducibility Artefacts

The following artefacts shall be frozen:

1. Candidate pool dataset
2. EPSS-enriched candidate pool
3. Sampled dataset
4. Sanitised dataset
5. Final dataset
6. Inference dataset
7. Record mapping dataset
8. Verification dataset

---

# Candidate Pool Measurement Results

## Total Candidate Pool

TBD

## Severity Distribution

TBD

### Critical

TBD

### High

TBD

### Medium

TBD

### Low

TBD

---

# Final Sampling Decision

Target Sample Size:

TBD

Severity Distribution:

TBD

Justification:

TBD

---

# Approval Status

Protocol Frozen: Yes

Dataset Specification Frozen: No

Dataset Generation Started: No
