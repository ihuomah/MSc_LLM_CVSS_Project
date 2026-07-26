from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INFERENCE = PROJECT_ROOT / "main_study" / "experiment_inputs" / "main_inference_dataset_v1.parquet"
MAPPING = PROJECT_ROOT / "main_study" / "experiment_inputs" / "main_record_mapping_v1.parquet"
VERIFICATION = PROJECT_ROOT / "main_study" / "experiment_inputs" / "main_record_verification_v1.parquet"

OUTPUT = PROJECT_ROOT / "main_study" / "audit" / "failed_inference_validation_records.xlsx"

FAILED_RECORD_IDS = [68, 191, 305, 580, 671, 822, 872, 155, 748]


def main():
    inf = pd.read_parquet(INFERENCE)
    mp = pd.read_parquet(MAPPING)
    ver = pd.read_parquet(VERIFICATION)

    joined = (
        inf.merge(mp, on="record_id", how="left")
           .merge(ver, on=["record_id", "cve_id"], how="left")
    )

    failed = joined[joined["record_id"].isin(FAILED_RECORD_IDS)].copy()

    assert len(failed) == len(FAILED_RECORD_IDS), (
        f"Expected {len(FAILED_RECORD_IDS)} records, found {len(failed)} — check record_id dtype"
    )

    cols = [
        "record_id",
        "cve_id",
        "description_for_model",
        "official_cvss_vector",
        "official_base_score",
        "official_severity",
        "epss_score",
        "epss_percentile",
    ]

    failed[cols].to_excel(OUTPUT, index=False)

    print("=" * 80)
    print("Failed validation records exported")
    print("=" * 80)
    print(
        failed[
            [
                "record_id",
                "cve_id",
                "official_base_score",
                "official_cvss_vector",
            ]
        ].to_string(index=False)
    )
    print(f"\nSaved to: {OUTPUT}")


if __name__ == "__main__":
    main()