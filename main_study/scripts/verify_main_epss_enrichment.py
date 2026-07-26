from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "processed"
    / "main_candidate_pool_with_epss.parquet"
)


def main():
    df = pd.read_parquet(INPUT_FILE)

    print("=" * 80)
    print("EPSS Verification")
    print("=" * 80)

    print("\nRows:")
    print(len(df))

    print("\nHas EPSS value counts:")
    print(df["has_epss"].value_counts(dropna=False))

    print("\nSample EPSS values:")
    print(
        df[
            [
                "cve_id",
                "epss_score",
                "epss_percentile",
                "has_epss",
            ]
        ]
        .sample(10, random_state=42)
        .to_string(index=False)
    )

    print("\nEPSS score summary:")
    print(df["epss_score"].describe())

    print("\nNull EPSS scores:")
    print(df["epss_score"].isna().sum())

    print("\nUnique EPSS dates:")
    print(df["epss_date"].nunique())

    print("\nSample EPSS source:")
    print(df["epss_source"].iloc[0])


if __name__ == "__main__":
    main()