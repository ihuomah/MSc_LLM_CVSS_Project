#!/usr/bin/env python3
"""
verify_main_inference_dataset.py

HARD GATE before any model run. Validates the exact file that will be sent to
OpenAI / Gemini / Ollama and confirms it cannot leak the answer.

Exit code 0  -> all hard checks passed; safe to run the experiment.
Exit code 1  -> at least one hard check failed; DO NOT run the experiment.

Hard checks (block the run):
  - row counts == 1000 across inference / mapping / verification
  - record_id is a clean 1:1 key across all three files (no dupes, no orphans)
  - inference file has EXACTLY [record_id, description_for_model]
  - every description_for_model == its final_description in the frozen master
  - no description_for_model is empty / null
  - no CVE IDs in any description (generic pattern + each record's own cve_id)
  - no CVSS vector in any description (generic pattern + each record's own vector)
  - each record's own base score appearing in a CVSS context
  - no EPSS score / percentile values (full precision) in any description

Warnings (listed, do NOT block):
  - bare base-score numbers (collide with version strings, e.g. "7.5")
  - very short descriptions (possible over-sanitisation)
  - CPE vendor/product tokens surfacing in a description (advisory residue check)

Usage:
    python main_study/scripts/verify_main_inference_dataset.py
    python verify_main_inference_dataset.py <experiment_inputs_dir> <master_parquet>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

# ----------------------------------------------------------------------
# Paths (override via argv for testing)
# ----------------------------------------------------------------------
EXP_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("main_study/experiment_inputs")
MASTER = (Path(sys.argv[2]) if len(sys.argv) > 2
          else Path("main_study/datasets/frozen/main_dataset_sanitised_final_v2.parquet"))

INFERENCE = EXP_DIR / "main_inference_dataset_v1.parquet"
MAPPING = EXP_DIR / "main_record_mapping_v1.parquet"
VERIFICATION = EXP_DIR / "main_record_verification_v1.parquet"

EXPECTED_ROWS = 1000
INFERENCE_COLUMNS = {"record_id", "description_for_model"}
MIN_DESC_LEN = 20            # below this -> warning (possible over-sanitisation)
SAMPLE_CAP = 10             # max offending record_ids to print per check

# ----------------------------------------------------------------------
# Patterns
# ----------------------------------------------------------------------
CVE_RE = re.compile(r"CVE-\d{4}-\d{3,7}", re.I)
# Three consecutive v3.1 metric tokens are unambiguously a CVSS vector fragment.
VECTOR_RE = re.compile(r"AV:[NALP]/AC:[LH]/PR:[NLH]", re.I)
SCORE_CONTEXT_RE = re.compile(r"(cvss|base[\s_-]*score|score\s*of|rated|severity)", re.I)

# ----------------------------------------------------------------------
# Result accumulator
# ----------------------------------------------------------------------
class Results:
    def __init__(self):
        self.rows = []  # (name, severity, passed, count, sample, note)

    def add(self, name, passed, severity="HARD", offenders=None, note=""):
        offenders = offenders or []
        self.rows.append((name, severity, passed, len(offenders),
                          offenders[:SAMPLE_CAP], note))

    def hard_failed(self):
        return any(sev == "HARD" and not ok for _, sev, ok, *_ in self.rows)

    def render(self):
        width = max(len(n) for n, *_ in self.rows) + 2
        lines = []
        for name, sev, ok, count, sample, note in self.rows:
            if ok:
                status = "PASS"
            else:
                status = "FAIL" if sev == "HARD" else "WARN"
            tag = "" if ok else f"  ({count} record(s))"
            lines.append(f"  [{status}] {name:<{width}}{tag}")
            if not ok and sample:
                lines.append(f"           e.g. {', '.join(map(str, sample))}")
            if not ok and note:
                lines.append(f"           {note}")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def load(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        sys.exit(f"ERROR: {label} not found: {path}")
    return pd.read_parquet(path)


def vector_core(v: str) -> str:
    v = str(v).strip()
    return v[len("CVSS:3.1/"):] if v.upper().startswith("CVSS:3.1/") else v


def score_str(s) -> str | None:
    if pd.isna(s):
        return None
    return f"{float(s):.1f}"            # CVSS base scores are 1 decimal


def epss_variants(x) -> list[str]:
    if pd.isna(x):
        return []
    # full-precision forms only: highly specific, no false positives
    return list({str(x), f"{float(x):.5f}"})


def context_hit(desc_lower: str, needle: str) -> bool:
    for m in re.finditer(re.escape(needle.lower()), desc_lower):
        window = desc_lower[max(0, m.start() - 40): m.end() + 40]
        if SCORE_CONTEXT_RE.search(window):
            return True
    return False


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main() -> None:
    print("=" * 78)
    print("Inference dataset HARD-GATE validation")
    print("=" * 78)

    inf = load(INFERENCE, "inference dataset")
    mp = load(MAPPING, "mapping dataset")
    ver = load(VERIFICATION, "verification dataset")
    master = load(MASTER, "frozen master")

    R = Results()

    # --- Structural -----------------------------------------------------
    for name, df in [("inference", inf), ("mapping", mp), ("verification", ver)]:
        R.add(f"row count == {EXPECTED_ROWS} ({name})", len(df) == EXPECTED_ROWS,
              note=f"got {len(df)}")

    R.add("inference columns are exactly {record_id, description_for_model}",
          set(inf.columns) == INFERENCE_COLUMNS,
          note=f"got {sorted(inf.columns)}")

    # record_id 1:1 key across the three files
    ids_inf, ids_mp, ids_ver = (set(inf["record_id"]), set(mp["record_id"]), set(ver["record_id"]))
    dupes = [c for df in (inf, mp, ver) for c in [df["record_id"].duplicated().sum()]]
    R.add("no duplicate record_id in any file", sum(dupes) == 0,
          note=f"duplicate counts inf/mp/ver = {dupes}")
    R.add("record_id sets identical across inference/mapping/verification",
          ids_inf == ids_mp == ids_ver,
          offenders=sorted((ids_inf ^ ids_mp) | (ids_inf ^ ids_ver)))

    # --- description_for_model == final_description ---------------------
    if "final_description" not in master.columns:
        R.add("master contains final_description", False,
              note="cannot verify sourcing without final_description column")
    else:
        merged = inf.merge(master[["record_id", "final_description"]], on="record_id", how="left")
        miss = merged["final_description"].isna()
        a = merged["description_for_model"].fillna("").astype(str).str.strip()
        b = merged["final_description"].fillna("").astype(str).str.strip()
        mismatch = merged.loc[miss | (a != b), "record_id"].tolist()
        R.add("description_for_model == final_description (every row)",
              len(mismatch) == 0, offenders=mismatch)

    # --- Empty descriptions --------------------------------------------
    desc = inf["description_for_model"]
    empty = inf.loc[desc.isna() | (desc.astype(str).str.strip() == ""), "record_id"].tolist()
    R.add("no empty / null description_for_model", len(empty) == 0, offenders=empty)

    # --- Per-record leakage scan ---------------------------------------
    key = ver.set_index("record_id")
    cve_generic, cve_own = [], []
    vec_generic, vec_own = [], []
    score_ctx, score_bare = [], []
    epss_leak = []
    short_desc = []

    has_cpe_cols = {"cpe_vendors", "cpe_products"}.issubset(master.columns)
    cpe = master.set_index("record_id") if has_cpe_cols else None
    cpe_residue = []

    for _, row in inf.iterrows():
        rid = row["record_id"]
        d = "" if pd.isna(row["description_for_model"]) else str(row["description_for_model"])
        dl = d.lower()

        if len(d.strip()) < MIN_DESC_LEN:
            short_desc.append(rid)

        if CVE_RE.search(d):
            cve_generic.append(rid)
        if VECTOR_RE.search(d):
            vec_generic.append(rid)

        if rid in key.index:
            meta = key.loc[rid]
            own_cve = str(meta.get("cve_id", "")).strip()
            if own_cve and own_cve.lower() in dl:
                cve_own.append(rid)

            own_vec = meta.get("official_cvss_vector", "")
            if pd.notna(own_vec):
                core = vector_core(own_vec).lower()
                if core and (core in dl or str(own_vec).lower() in dl):
                    vec_own.append(rid)

            ss = score_str(meta.get("official_base_score"))
            if ss:
                if context_hit(dl, ss):
                    score_ctx.append(rid)
                elif ss in dl:
                    score_bare.append(rid)

            for col in ("epss_score", "epss_percentile"):
                for v in epss_variants(meta.get(col)):
                    if v in dl:
                        epss_leak.append(rid)
                        break

        if cpe is not None and rid in cpe.index:
            tokens = []
            for col in ("cpe_vendors", "cpe_products"):
                val = cpe.loc[rid, col]
                if isinstance(val, str):
                    tokens += [t for t in re.split(r"[\s,;|]+", val) if len(t) >= 4]
            if any(t.lower() in dl for t in set(tokens)):
                cpe_residue.append(rid)

    # Hard leakage checks
    R.add("no CVE-ID pattern in any description", len(cve_generic) == 0, offenders=cve_generic)
    R.add("no record's own cve_id in its description", len(cve_own) == 0, offenders=cve_own)
    R.add("no CVSS vector pattern in any description", len(vec_generic) == 0, offenders=vec_generic)
    R.add("no record's own official vector in its description", len(vec_own) == 0, offenders=vec_own)
    R.add("no base score in a CVSS context", len(score_ctx) == 0, offenders=score_ctx)
    R.add("no EPSS score/percentile values in any description", len(epss_leak) == 0, offenders=epss_leak)

    # Warnings
    R.add("bare base-score numbers (review: may be version strings)",
          len(score_bare) == 0, severity="WARN", offenders=score_bare)
    R.add(f"descriptions >= {MIN_DESC_LEN} chars (review: over-sanitisation)",
          len(short_desc) == 0, severity="WARN", offenders=short_desc)
    if cpe is not None:
        R.add("no CPE vendor/product tokens in descriptions (advisory)",
              len(cpe_residue) == 0, severity="WARN", offenders=cpe_residue)

    # --- Report ---------------------------------------------------------
    print(R.render())
    print("=" * 78)
    if R.hard_failed():
        print("RESULT: FAIL — hard checks failed. DO NOT run the experiment.")
        print("=" * 78)
        sys.exit(1)
    warns = sum(1 for _, sev, ok, *_ in R.rows if sev == "WARN" and not ok)
    print(f"RESULT: PASS — all hard checks passed."
          + (f" ({warns} warning(s) to review.)" if warns else ""))
    print("=" * 78)
    sys.exit(0)


if __name__ == "__main__":
    main()