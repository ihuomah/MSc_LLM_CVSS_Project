from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "sanitised"
    / "main_dataset_sanitised_auto_v1.parquet"
)

REVIEW_DIR = PROJECT_ROOT / "main_study" / "datasets" / "sanitised" / "review"
AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"

REVIEW_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

FULL_REVIEW_FILE = REVIEW_DIR / "main_full_sanitisation_review.xlsx"
HEAVY_REPLACEMENT_FILE = REVIEW_DIR / "main_heavy_replacement_review.xlsx"
NO_REPLACEMENT_FILE = REVIEW_DIR / "main_no_replacement_review.xlsx"
RANDOM_SAMPLE_FILE = REVIEW_DIR / "main_random_review_sample.xlsx"
RESIDUAL_FLAGS_FILE = REVIEW_DIR / "main_residual_flags_review.xlsx"

LOG_FILE = AUDIT_DIR / "main_sanitisation_review_log_v1.txt"

RANDOM_SEED = 42
RANDOM_SAMPLE_SIZE = 50
HEAVY_REPLACEMENT_TOP_N = 100


REVIEW_COLUMNS = [
    "record_id",
    "cve_id",
    "official_severity",
    "published_year",
    "has_cpe",
    "cpe_vendors",
    "cpe_products",
    "original_description",
    "sanitised_description",
    "vendor_replacements",
    "product_replacements",
    "total_replacements",
    "residual_flags",
    "official_cvss_vector",
    "official_base_score",
    "epss_score",
    "epss_percentile",
]


def write_log(message):
    print(message)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def main():
    LOG_FILE.write_text("", encoding="utf-8")

    write_log("=" * 80)
    write_log("Starting Main Sanitisation Review File Generation")
    write_log("=" * 80)

    df = pd.read_parquet(INPUT_FILE)

    review_columns = [col for col in REVIEW_COLUMNS if col in df.columns]

    full_review = df[review_columns].copy()

    residual_flags = df[
        df["residual_flags"].fillna("").astype(str).str.len() > 0
    ][review_columns].copy()

    heavy_replacement = (
        df[df["total_replacements"] > 0]
        .sort_values("total_replacements", ascending=False)
        .head(HEAVY_REPLACEMENT_TOP_N)
    )[review_columns].copy()

    no_replacement = df[df["total_replacements"] == 0][review_columns].copy()

    random_sample = df.sample(
        n=min(RANDOM_SAMPLE_SIZE, len(df)),
        random_state=RANDOM_SEED,
    )[review_columns].copy()

    full_review.to_excel(FULL_REVIEW_FILE, index=False)
    heavy_replacement.to_excel(HEAVY_REPLACEMENT_FILE, index=False)
    no_replacement.to_excel(NO_REPLACEMENT_FILE, index=False)
    random_sample.to_excel(RANDOM_SAMPLE_FILE, index=False)
    residual_flags.to_excel(RESIDUAL_FLAGS_FILE, index=False)

    write_log(f"Rows in full review: {len(full_review)}")
    write_log(f"Rows with residual flags: {len(residual_flags)}")
    write_log(f"Heavy replacement review rows: {len(heavy_replacement)}")
    write_log(f"No replacement review rows: {len(no_replacement)}")
    write_log(f"Random sample review rows: {len(random_sample)}")

    write_log("\nReplacement distribution:")
    write_log(str(df["total_replacements"].describe()))

    write_log("\nOutputs:")
    write_log(f"Full review: {FULL_REVIEW_FILE}")
    write_log(f"Heavy replacement review: {HEAVY_REPLACEMENT_FILE}")
    write_log(f"No replacement review: {NO_REPLACEMENT_FILE}")
    write_log(f"Random sample review: {RANDOM_SAMPLE_FILE}")
    write_log(f"Residual flags review: {RESIDUAL_FLAGS_FILE}")
    write_log(f"Log: {LOG_FILE}")

    write_log("=" * 80)
    write_log("Main Sanitisation Review File Generation Complete")
    write_log("=" * 80)


if __name__ == "__main__":
    main()