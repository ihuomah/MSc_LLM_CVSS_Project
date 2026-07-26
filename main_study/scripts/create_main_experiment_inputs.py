from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "frozen"
    / "main_dataset_sanitised_final_v2.parquet"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "main_study"
    / "experiment_inputs"
)

AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

INFERENCE_PARQUET = OUTPUT_DIR / "main_inference_dataset_v1.parquet"
INFERENCE_CSV = OUTPUT_DIR / "main_inference_dataset_v1.csv"
INFERENCE_XLSX = OUTPUT_DIR / "main_inference_dataset_v1.xlsx"

MAPPING_PARQUET = OUTPUT_DIR / "main_record_mapping_v1.parquet"
MAPPING_CSV = OUTPUT_DIR / "main_record_mapping_v1.csv"
MAPPING_XLSX = OUTPUT_DIR / "main_record_mapping_v1.xlsx"

VERIFICATION_PARQUET = OUTPUT_DIR / "main_record_verification_v1.parquet"
VERIFICATION_CSV = OUTPUT_DIR / "main_record_verification_v1.csv"
VERIFICATION_XLSX = OUTPUT_DIR / "main_record_verification_v1.xlsx"

LOG_FILE = AUDIT_DIR / "main_experiment_input_creation_log_v1.txt"


def write_log(message):
    print(message)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def main():
    LOG_FILE.write_text("", encoding="utf-8")

    write_log("=" * 80)
    write_log("Creating Main Experiment Input Files")
    write_log("=" * 80)

    df = pd.read_parquet(INPUT_FILE).copy()

    if len(df) != 1000:
        raise ValueError(f"Expected 1000 rows, found {len(df)}")

    required_columns = [
        "record_id",
        "cve_id",
        "final_description",
        "official_cvss_vector",
        "official_base_score",
        "official_severity",
        "epss_score",
        "epss_percentile",
        "published_year",
        "cvss_selection_method",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df["record_id"].duplicated().any():
        raise ValueError("Duplicate record_id values found.")

    if df["record_id"].isna().any():
        raise ValueError("Missing record_id values found.")

    df = df.sort_values("record_id").reset_index(drop=True)

    # ============================================================================
    # Inference file
    # The model must only see record_id and description_for_model.
    # description_for_model MUST come from final_description.
    # ============================================================================

    inference_df = df[["record_id", "final_description"]].rename(
        columns={"final_description": "description_for_model"}
    )

    # ============================================================================
    # Mapping file
    # Used to reconnect record_id to CVE after inference.
    # ============================================================================

    mapping_df = df[["record_id", "cve_id"]].copy()

    # ============================================================================
    # Verification file
    # Answer-side data used only during analysis.
    # Never sent to the model.
    # ============================================================================

    verification_df = df[
        [
            "record_id",
            "cve_id",
            "official_cvss_vector",
            "official_base_score",
            "official_severity",
            "epss_score",
            "epss_percentile",
            "published_year",
            "cvss_selection_method",
        ]
    ].copy()

    # Save inference
    inference_df.to_parquet(INFERENCE_PARQUET, index=False)
    inference_df.to_csv(INFERENCE_CSV, index=False, encoding="utf-8")
    inference_df.to_excel(INFERENCE_XLSX, index=False)

    # Save mapping
    mapping_df.to_parquet(MAPPING_PARQUET, index=False)
    mapping_df.to_csv(MAPPING_CSV, index=False, encoding="utf-8")
    mapping_df.to_excel(MAPPING_XLSX, index=False)

    # Save verification
    verification_df.to_parquet(VERIFICATION_PARQUET, index=False)
    verification_df.to_csv(VERIFICATION_CSV, index=False, encoding="utf-8")
    verification_df.to_excel(VERIFICATION_XLSX, index=False)

    write_log(f"Input file: {INPUT_FILE}")
    write_log(f"Rows processed: {len(df)}")

    write_log("\nInference dataset:")
    write_log(f"Rows: {len(inference_df)}")
    write_log(f"Columns: {list(inference_df.columns)}")
    write_log(f"Parquet: {INFERENCE_PARQUET}")
    write_log(f"CSV: {INFERENCE_CSV}")
    write_log(f"XLSX: {INFERENCE_XLSX}")

    write_log("\nMapping dataset:")
    write_log(f"Rows: {len(mapping_df)}")
    write_log(f"Columns: {list(mapping_df.columns)}")
    write_log(f"Parquet: {MAPPING_PARQUET}")
    write_log(f"CSV: {MAPPING_CSV}")
    write_log(f"XLSX: {MAPPING_XLSX}")

    write_log("\nVerification dataset:")
    write_log(f"Rows: {len(verification_df)}")
    write_log(f"Columns: {list(verification_df.columns)}")
    write_log(f"Parquet: {VERIFICATION_PARQUET}")
    write_log(f"CSV: {VERIFICATION_CSV}")
    write_log(f"XLSX: {VERIFICATION_XLSX}")

    write_log("\nImportant rule:")
    write_log("description_for_model was created from final_description.")

    write_log("=" * 80)
    write_log("Main Experiment Input Creation Complete")
    write_log("=" * 80)


if __name__ == "__main__":
    main()