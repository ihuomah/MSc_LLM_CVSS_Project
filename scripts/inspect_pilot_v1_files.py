from pathlib import Path
import pandas as pd


BASE = Path("data/frozen_pilot_v1/datasets")

FILES = [
    "nvd_pilot_raw.xlsx",
    "nvd_pilot_final.xlsx",
    "pilot_inference_input_v1.xlsx",
    "pilot_record_id_mapping_v1.xlsx",
    "pilot_record_id_verification_v1.xlsx",
]


def main():
    for filename in FILES:
        path = BASE / filename

        print("=" * 80)
        print(filename)

        if not path.exists():
            print("NOT FOUND")
            continue

        df = pd.read_excel(path)
        print(f"Rows: {len(df)}")
        print("Columns:")
        for col in df.columns:
            print(f" - {col}")


if __name__ == "__main__":
    main()