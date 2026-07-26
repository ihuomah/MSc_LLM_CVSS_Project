Pilot Dataset Version: v1.0

Date Frozen: [today's date]

Dataset Size:
50 CVEs

Severity Distribution:
10 Critical
15 High
15 Medium
10 Low

CVSS Version:
CVSS v3.1 only

Pipeline:

fetch_nvd_cves.py
→ nvd_pilot_raw.xlsx

sanitise_pilot_dataset.py
→ nvd_pilot_sanitised.xlsx

inspect_sanitisation_review.py
→ no_cpe_review.xlsx
→ cpe_leak_review.xlsx

pilot_manual_review.xlsx
→ apply_manual_redactions.py

→ nvd_pilot_final.xlsx

create_pilot_inference_and_mapping.py

→ pilot_inference_input_v1.xlsx
→ pilot_record_id_mapping_v1.xlsx
→ pilot_record_id_verification_v1.xlsx

Notes:
- CPE-based sanitisation used where available.
- Manual review applied to No-CPE records.
- Dataset frozen before LLM inference.