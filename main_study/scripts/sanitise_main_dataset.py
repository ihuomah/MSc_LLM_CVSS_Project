import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "datasets"
    / "frozen"
    / "main_dataset_frozen_v1.parquet"
)

SANITISED_DIR = PROJECT_ROOT / "main_study" / "datasets" / "sanitised"
AUDIT_DIR = PROJECT_ROOT / "main_study" / "audit"

SANITISED_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PARQUET = SANITISED_DIR / "main_dataset_sanitised_auto_v1.parquet"
OUTPUT_CSV = SANITISED_DIR / "main_dataset_sanitised_auto_v1.csv"
OUTPUT_XLSX = SANITISED_DIR / "main_dataset_sanitised_auto_v1.xlsx"

LOG_FILE = AUDIT_DIR / "main_sanitisation_auto_log_v1.txt"


def write_log(message):
    print(message)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def split_tokens(value):
    if not isinstance(value, str) or not value.strip():
        return []
    return [token.strip() for token in value.split("|") if token.strip()]


def normalise_cpe_token(token):
    token = str(token)
    token = token.replace("\\", "")
    token = token.replace("_", " ")
    return token.strip()


def generate_variants(token):
    token = normalise_cpe_token(token)

    if not token or len(token) < 3:
        return []

    variants = set()

    variants.add(token)
    variants.add(token.lower())
    variants.add(token.upper())
    variants.add(token.title())

    if " " in token:
        variants.add(token.replace(" ", "_"))
        variants.add(token.replace(" ", "-"))

    return sorted({v for v in variants if len(v.strip()) >= 3}, key=len, reverse=True)


def safe_replace(text, term, replacement):
    """
    Safer replacement:
    - avoids replacing tiny fragments
    - avoids replacing inside longer alphanumeric strings
    - still supports package-like names such as @vendor/product
    """
    if not isinstance(text, str) or not term:
        return text, 0

    term = str(term).strip()
    if len(term) < 3:
        return text, 0

    escaped = re.escape(term)

    pattern = re.compile(
        rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])",
        re.IGNORECASE,
    )

    return pattern.subn(replacement, text)


def redact_terms(text, terms, replacement):
    total = 0

    # Longest terms first prevents partial corruption.
    for term in sorted(set(terms), key=len, reverse=True):
        text, count = safe_replace(text, term, replacement)
        total += count

    return text, total


def build_compound_terms(vendors, products):
    compound_terms = []

    for vendor in vendors:
        vendor_clean = normalise_cpe_token(vendor)
        for product in products:
            product_clean = normalise_cpe_token(product)

            if not vendor_clean or not product_clean:
                continue

            compound_terms.extend([
                f"{vendor_clean} {product_clean}",
                f"{vendor_clean}_{product_clean}",
                f"{vendor_clean}-{product_clean}",
                f"{vendor_clean}/{product_clean}",
                f"@{vendor_clean}/{product_clean}",
            ])

    return compound_terms


def build_residual_flags(text, vendor_terms, product_terms):
    flags = []

    if not isinstance(text, str):
        return ""

    lowered = text.lower()

    for term in vendor_terms:
        if len(term) >= 3 and term.lower() in lowered:
            flags.append(f"vendor:{term}")

    for term in product_terms:
        if len(term) >= 3 and term.lower() in lowered:
            flags.append(f"product:{term}")

    return "|".join(sorted(set(flags)))


def clean_text(text):
    text = re.sub(r"\b(Vendor X)(\s+Vendor X)+\b", r"\1", text)
    text = re.sub(r"\b(Product Y)(\s+Product Y)+\b", r"\1", text)
    text = re.sub(r"Vendor X/Product Y", "Vendor X/Product Y", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def sanitise_row(row):
    original = row["original_description"]

    vendors = split_tokens(row.get("cpe_vendors", ""))
    products = split_tokens(row.get("cpe_products", ""))

    vendor_terms = []
    product_terms = []
    compound_terms = []

    for vendor in vendors:
        vendor_terms.extend(generate_variants(vendor))

    for product in products:
        product_terms.extend(generate_variants(product))

    compound_terms.extend(build_compound_terms(vendors, products))

    vendor_terms = sorted(set(vendor_terms), key=len, reverse=True)
    product_terms = sorted(set(product_terms), key=len, reverse=True)
    compound_terms = sorted(set(compound_terms), key=len, reverse=True)

    text = original

    # 1. Replace compound vendor/product forms first.
    text, compound_replacements = redact_terms(
        text,
        compound_terms,
        "Vendor X Product Y",
    )

    # 2. Replace product terms before vendor terms.
    text, product_replacements = redact_terms(
        text,
        product_terms,
        "Product Y",
    )

    # 3. Replace vendor terms last.
    text, vendor_replacements = redact_terms(
        text,
        vendor_terms,
        "Vendor X",
    )

    text = clean_text(text)

    residual_flags = build_residual_flags(
        text,
        vendor_terms,
        product_terms,
    )

    return pd.Series({
        "sanitised_description": text,
        "compound_replacements": compound_replacements,
        "vendor_replacements": vendor_replacements,
        "product_replacements": product_replacements,
        "total_replacements": (
            compound_replacements
            + vendor_replacements
            + product_replacements
        ),
        "residual_flags": residual_flags,
    })


def main():
    LOG_FILE.write_text("", encoding="utf-8")

    write_log("=" * 80)
    write_log("Starting Main Dataset Automated Sanitisation - Revised")
    write_log("=" * 80)

    df = pd.read_parquet(INPUT_FILE)

    required_cols = [
        "record_id",
        "cve_id",
        "original_description",
        "cpe_vendors",
        "cpe_products",
        "has_cpe",
    ]

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Input dataset missing required columns: {missing}")

    write_log(f"Input rows: {len(df)}")

    sanitised_fields = df.apply(sanitise_row, axis=1)
    output = pd.concat([df, sanitised_fields], axis=1)

    output.to_parquet(OUTPUT_PARQUET, index=False)
    output.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    output.to_excel(OUTPUT_XLSX, index=False)

    no_cpe_count = int((output["has_cpe"] == False).sum())
    replacement_count = int(output["total_replacements"].sum())
    rows_with_replacements = int((output["total_replacements"] > 0).sum())
    residual_count = int(output["residual_flags"].fillna("").str.len().gt(0).sum())

    write_log("\nSanitisation Summary")
    write_log(f"Rows processed: {len(output)}")
    write_log(f"No-CPE rows: {no_cpe_count}")
    write_log(f"Rows with replacements: {rows_with_replacements}")
    write_log(f"Total replacements: {replacement_count}")
    write_log(f"Rows with residual flags: {residual_count}")

    write_log("\nOutputs:")
    write_log(f"Parquet: {OUTPUT_PARQUET}")
    write_log(f"CSV: {OUTPUT_CSV}")
    write_log(f"XLSX: {OUTPUT_XLSX}")
    write_log(f"Log: {LOG_FILE}")

    write_log("=" * 80)
    write_log("Main Dataset Automated Sanitisation Revised Complete")
    write_log("=" * 80)


if __name__ == "__main__":
    main()