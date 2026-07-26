import pandas as pd

pilot_records = [
    {
        "record_id": "PILOT-001",
        "original_cve_id": "",
        "original_description": "",
        "sanitised_description": "",
        "official_cvss_vector": "",
        "official_base_score": "",
        "official_severity": "",
        "epss_score": "",
        "vulnerability_category": "",
        "published_date": ""
    }
]

df = pd.DataFrame(pilot_records)

output_path = "data/processed/pilot_dataset_template.xlsx"
df.to_excel(output_path, index=False)

print(f"Pilot dataset template created: {output_path}")