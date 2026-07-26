# EPSS Enrichment Design v1

Pilot v1 remains frozen and unchanged.

EPSS enrichment will derive Pilot v2 from the frozen Pilot v1 dataset using the existing frozen CVE IDs.

No CVEs will be added or removed. No descriptions, CVSS vectors, base scores, severities, sanitisation outputs, or record mappings will be modified.

EPSS source: FIRST/Cyentia daily EPSS CSV.

## Coverage check result:
- Pilot records: 50
- Has EPSS: 50
- Missing EPSS: 0
- Coverage: 100%

## Fields to add:
- epss_score
- epss_percentile
- epss_date
- epss_source
- has_epss

## Output:
data/enriched_pilot_v2/

Purpose:
Enable RQ3 analysis without modifying the frozen pilot v1 dataset.