"""
CPE-driven CVE description sanitiser.

Redaction is driven primarily by each record's own CPE vendor/product tokens
(systematic, per-record, reproducible) rather than a static allowlist. Regex
handles the structural artefacts CPE does not cover: identifiers, version
strings, and file paths / API routes. A small allowlist remains ONLY as a
backstop for records whose CPE configuration is empty.

Pipeline per description:
  1. identifiers (CVE/CWE/advisory/URL/email)
  2. versions (ranges, dotted, bare-major)
  3. CPE-driven vendor/product redaction (de-normalised token matching)
  4. backstop allowlist (only adds coverage; never the primary mechanism)
  5. file paths / API routes
  6. opener-template normalisation
  7. whitespace + scar cleanup
Then residual_leak_tokens() verifies nothing identity-like survived.
"""

import re
import pandas as pd

INPUT_FILE = "data/raw/nvd_pilot_raw.xlsx"
OUTPUT_FILE = "data/processed/nvd_pilot_sanitised.xlsx"
AUDIT_FILE = "data/processed/nvd_pilot_sanitisation_audit.xlsx"

VENDOR_PLACEHOLDER = "Vendor X"
VERSION_PLACEHOLDER = "version Z"

# ---------------------------------------------------------------------------
# 1. Identifiers
# ---------------------------------------------------------------------------
IDENTIFIER_PATTERNS = [
    (re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE), "the vulnerability"),
    (re.compile(r"\bCWE-\d{1,4}\b", re.IGNORECASE), "a weakness"),
    (re.compile(r"\bGHSA-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}\b", re.IGNORECASE), "an advisory"),
    (re.compile(r"\b(?:RHSA|RHBA|MSRC|DSA|USN|ELSA|TALOS)-?\d[\w-]*\b", re.IGNORECASE), "an advisory"),
    (re.compile(r"\bZDI-(?:CAN-)?\d+\b", re.IGNORECASE), "an advisory"),
    # VulDB (VDB-NNN) and other numeric advisory identifiers
    (re.compile(r"\bVDB-\d+\b", re.IGNORECASE), "an advisory"),
    (re.compile(r"\b(?:WPVDB|SNYK|VU|JVN|HackerOne|HackerOne-)[#-]?\d[\w-]*\b", re.IGNORECASE), "an advisory"),
    (re.compile(r"https?://\S+", re.IGNORECASE), "a reference link"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "a contact"),
]

# ---------------------------------------------------------------------------
# 2. Versions
# ---------------------------------------------------------------------------
VERSION_RANGE = re.compile(
    r"\b(before|through|prior to|up to|up through|until|from|thru)\s+"
    r"(?:v|version\s+)?\d+(?:\.\d+){0,4}[a-z0-9._-]*\b", re.IGNORECASE)
VERSION_DOTTED = re.compile(
    r"\b(?:v|version\s+)?\d+(?:\.\d+){1,4}(?:[-_][a-z0-9.]+)?\b", re.IGNORECASE)
VERSION_BARE_MAJOR = re.compile(r"\b(?:v|version)\s*\d+\b", re.IGNORECASE)

# ---------------------------------------------------------------------------
# 4. Backstop allowlist — ONLY used when a record has no CPE data.
# ---------------------------------------------------------------------------
BACKSTOP_VENDORS = sorted([
    "Microsoft", "Windows", "Linux", "Oracle", "Cisco", "Apple", "Google",
    "Apache", "IBM", "VMware", "Fortinet", "Adobe", "Mozilla", "WordPress",
    "GitLab", "Jenkins", "Drupal", "OpenSSL", "Kubernetes", "Docker",
], key=len, reverse=True)
_backstop_alt = "|".join(re.escape(t) for t in BACKSTOP_VENDORS)
BACKSTOP_RE = re.compile(rf"(?<![\w-])(?:{_backstop_alt})(?![\w-])", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Distribution platforms / code repositories.
# These often appear in CVE descriptions but are not represented in CPE.
# This is deliberately small and targeted; it is not a general vendor list.
# ---------------------------------------------------------------------------
DISTRIBUTION_PLATFORMS = sorted([
    "SourceCodester",
    "PHPGurukul",
    "CodeAstro",
    "code-projects",
    "itsourcecode",
], key=len, reverse=True)

_platform_alt = "|".join(re.escape(t) for t in DISTRIBUTION_PLATFORMS)
PLATFORM_RE = re.compile(rf"(?<![\w-])(?:{_platform_alt})(?![\w-])", re.IGNORECASE)

# ---------------------------------------------------------------------------
# 5. File paths / API routes / source filenames / distinctive function names.
# Three patterns cover: forward-slash paths, backslash (Windows-style) paths,
# bare PHP/Python/JS source filenames, and dotted function-call identifiers
# that act as strong product fingerprints (e.g. runtime.pingTest).
# Generic parameter names like 'CityName' or 'Password' are intentionally
# NOT matched here — they are weak fingerprints carrying technical signal.
# ---------------------------------------------------------------------------
PATH_FWD = re.compile(r"(?<!\w)/[A-Za-z0-9._\-]+(?:/[A-Za-z0-9._\-]+)+")
PATH_BACK = re.compile(r"(?<!\w)\\[A-Za-z0-9._\-]+(?:\\[A-Za-z0-9._\-]+)+")
SOURCE_FILE = re.compile(r"\b[A-Za-z0-9_\-]+\.(?:php|py|js|jsp|aspx?|rb|go|lua|sh|pl|cgi)\b", re.IGNORECASE)
# function-call-ish identifier: word.camelCaseWord or word.snake_case (distinctive)
FUNCTION_REF = re.compile(r"\b[a-z][a-zA-Z0-9_]*\.[a-z][a-zA-Z]*[A-Z][a-zA-Z0-9_]*\b")

# ---------------------------------------------------------------------------
# 6. Opener templates
# ---------------------------------------------------------------------------
OPENER_PATTERNS = [
    (re.compile(r"\bA vulnerability (?:was found|was determined|has been found|classified as \w+) in\b", re.IGNORECASE),
     "A vulnerability exists in"),
    (re.compile(r"\bAn issue was discovered in\b", re.IGNORECASE),
     "A security issue exists in"),
]


def _denormalise_cpe_token(token):
    """Turn an NVD CPE token into a regex matching its surface forms.

    'rx2_pro'     -> matches 'rx2 pro', 'rx2-pro', 'rx2_pro' (case-insensitive)
    'i-educar'    -> matches 'i educar', 'i-educar', 'i_educar'
    'wp_go_maps'  -> matches 'wp go maps' etc.
    Very short/generic tokens are skipped to avoid over-redaction.
    """
    token = token.strip().strip("\\")
    if not token or token in ("*", "-"):
        return None
    # split on the normalisation separators
    words = re.split(r"[_\s]+", token)
    words = [w for w in words if w]
    if not words:
        return None
    # skip a single token that is too short/generic (e.g. 'a', 'go', 'os')
    if len(words) == 1 and len(words[0]) <= 2:
        return None
    # build: word(sep)word(sep)... where sep is space/hyphen/underscore
    sep = r"[\s_\-]+"
    parts = [re.escape(w) for w in words]
    pattern = sep.join(parts)
    # word-ish boundaries that tolerate hyphens (so 'i-educar' matches fully)
    return re.compile(rf"(?<![\w-])(?:{pattern})(?![\w-])", re.IGNORECASE)


def build_cpe_matchers(vendors_field, products_field):
    """From the |-joined CPE fields, build a de-duplicated, length-sorted list
    of compiled matchers. Longer (multi-word) names first so 'wp go maps'
    redacts before a bare 'maps' could."""
    raw = []
    for field in (vendors_field, products_field):
        if isinstance(field, str) and field:
            raw.extend(field.split("|"))
    # sort by word count then length, descending, so multiword names win
    raw = sorted(set(raw), key=lambda t: (t.count("_"), len(t)), reverse=True)
    matchers = []
    for tok in raw:
        m = _denormalise_cpe_token(tok)
        if m:
            matchers.append(m)
    return matchers


def sanitise_description(text, cpe_vendors="", cpe_products="", has_cpe=True):
    counts = {"identifiers": 0, "versions": 0, "cpe_redactions": 0,
              "backstop_redactions": 0, "platform_redactions": 0, "paths": 0}
    if not isinstance(text, str) or not text.strip():
        return "", counts
    s = text.strip()

    # 1. identifiers
    for pat, repl in IDENTIFIER_PATTERNS:
        s, n = pat.subn(repl, s)
        counts["identifiers"] += n

    # 2. versions
    for pat, repl in [(VERSION_RANGE, lambda m: m.group(1) + " a certain version"),
                      (VERSION_DOTTED, VERSION_PLACEHOLDER),
                      (VERSION_BARE_MAJOR, VERSION_PLACEHOLDER)]:
        s, n = pat.subn(repl, s)
        counts["versions"] += n
    s = re.sub(rf"\b({re.escape(VERSION_PLACEHOLDER)})(\s+{re.escape(VERSION_PLACEHOLDER)})+\b", r"\1", s)

    # 3. CPE-driven vendor/product redaction
    for matcher in build_cpe_matchers(cpe_vendors, cpe_products):
        s, n = matcher.subn(VENDOR_PLACEHOLDER, s)
        counts["cpe_redactions"] += n

    # 4. backstop ONLY when this record had no CPE data
    if not has_cpe:
        s, n = BACKSTOP_RE.subn(VENDOR_PLACEHOLDER, s)
        counts["backstop_redactions"] += n

    # 4b. distribution platforms / code repositories.
    # These are applied regardless of CPE availability because they often
    # appear in descriptions but not in CPE vendor/product fields.
    s, n = PLATFORM_RE.subn(VENDOR_PLACEHOLDER, s)
    counts["platform_redactions"] += n

    # collapse repeated vendor placeholders ("Vendor X Vendor X")
    s = re.sub(rf"\b({re.escape(VENDOR_PLACEHOLDER)})(\s+{re.escape(VENDOR_PLACEHOLDER)})+\b", r"\1", s)

    # 5. file paths / API routes / source filenames / function refs
    total_paths = 0
    for pat, repl in [(PATH_FWD, " a specific endpoint"),
                      (PATH_BACK, " a specific endpoint"),
                      (SOURCE_FILE, "a source file"),
                      (FUNCTION_REF, "a specific function")]:
        s, n = pat.subn(repl, s)
        total_paths += n
    counts["paths"] = total_paths

    # 6. opener templates
    for pat, repl in OPENER_PATTERNS:
        s = pat.sub(repl, s)

    # 7. scar / punctuation cleanup + whitespace
    s = re.sub(r"\(\s*formerly[^)]*\)", "", s, flags=re.IGNORECASE)  # drop "(formerly ...)"
    s = re.sub(r"\s+([.,;:])", r"\1", s)        # space before punctuation
    s = re.sub(r"([.,;:])\1+", r"\1", s)         # doubled punctuation
    s = re.sub(r"\.\s*\.", ".", s)               # ". ." -> "."
    s = re.sub(r"\s+", " ", s).strip()
    return s, counts


# ---------------------------------------------------------------------------
# Residual-leak verification (technical-term aware)
# ---------------------------------------------------------------------------
ALLOWED_PLACEHOLDERS = {"Vendor", "Software", "Z", "X", "Y", "A", "An", "The"}
TECHNICAL_TERMS = {
    "code", "execution", "remote", "local", "arbitrary", "vulnerability",
    "vulnerabilities", "integer", "underflow", "overflow", "buffer",
    "injection", "traversal", "disclosure", "escalation", "privilege",
    "privileges", "denial", "service", "authentication", "authenticated",
    "unauthenticated", "authorization", "authorisation", "bypass", "exploit",
    "exploited", "exploitation", "memory", "pointer", "stack", "heap",
    "deserialization", "deserialisation", "validation", "parsing", "crafted",
    "malicious", "payload", "request", "response", "attacker", "attackers",
    "scripting", "spoofing", "tampering", "redirect", "race", "condition",
    "command", "manipulation", "argument", "function", "interface", "binary",
    "macro", "macros", "improper", "limited", "partial", "stored", "reflected",
    "network-adjacent", "user-supplied", "use-after-free", "out-of-bounds",
    "sql", "html", "javascript", "json", "xml", "xss", "csrf", "ssrf", "rce",
    "lfi", "rfi", "api", "rest", "soap", "http", "https", "tcp", "udp", "dns",
    "tls", "ssl", "ssh", "ftp", "smtp", "smb", "ldap", "oauth", "jwt", "uri",
    "url", "spf", "cors", "php", "cgi", "dom", "ascii", "utf", "regex", "yaml",
    "csv", "access", "controls", "control", "web", "management", "portal",
    "system", "data", "user", "users", "file", "files", "site", "cross",
    "server", "client", "network", "process", "account", "specific", "flaw",
    "issue", "affected", "installations", "context", "endpoint",
    # acronyms & technical terms surfaced during pilot review
    "gui", "ui", "uuid", "sd-wan", "ucpe", "cdn", "guid", "url", "iv",
    "cli", "ide", "sdk", "tcp/ip", "ipv4", "ipv6", "csv", "yaml", "json",
    "saml", "xpath", "xslt", "websocket", "websockets", "graphql",
    # frequently sentence-initial in NVD/advisory prose (false-positive control)
    "there", "status", "mitigation", "workarounds", "exploitation", "proof",
    "executing", "successful", "additionally", "however", "note", "patched",
    "fixed", "discovered", "reported", "according",
    # additional false-positive terms surfaced during sanitisation review
    "during", "generation", "input", "neutralization", "neutralisation",
    "page", "form", "edit", "post", "draft", "mass", "assignment",
    "own", "id", "lte", "idor", "toctou", "uiextension", "impact",
    "login", "with", "cross-site", "behavior", "behaviour", "panel",
}


def residual_leak_tokens(sanitised):
    flags = []
    for m in re.finditer(r"\b[A-Za-z][A-Za-z0-9.+_-]{1,}\b", sanitised):
        tok = m.group(0)
        start = m.start()
        if tok in ALLOWED_PLACEHOLDERS or tok.lower() in TECHNICAL_TERMS:
            continue
        has_internal_signal = bool(re.search(r"[A-Z0-9]", tok[1:])) or "-" in tok
        if not has_internal_signal:
            if start == 0:
                continue
            if sanitised[max(0, start - 2):start].strip().endswith((".", "!", "?")):
                continue
            if not tok[0].isupper():
                continue
        flags.append(tok)
    return sorted(set(flags))


def main():
    df = pd.read_excel(INPUT_FILE)
    results, audits, leaks = [], [], []
    for _, row in df.iterrows():
        clean, counts = sanitise_description(
            row.get("original_description", ""),
            cpe_vendors=row.get("cpe_vendors", "") or "",
            cpe_products=row.get("cpe_products", "") or "",
            has_cpe=bool(row.get("has_cpe", True)),
        )
        results.append(clean)
        audits.append(counts)
        leaks.append(", ".join(residual_leak_tokens(clean)))

    df["sanitised_description"] = results
    df["residual_flags"] = leaks
    audit_df = pd.DataFrame(audits)

    keep = [c for c in [
        "cve_id", "original_description", "sanitised_description",
        "residual_flags", "cpe_vendors", "cpe_products", "has_cpe",
        "official_cvss_vector", "official_base_score", "official_severity",
        "published_date",
    ] if c in df.columns]
    df[keep].to_excel(OUTPUT_FILE, index=False)
    audit_df.sum().to_frame("total").to_excel(AUDIT_FILE)

    print(f"Sanitised dataset saved to: {OUTPUT_FILE}")
    print(f"Audit summary saved to:    {AUDIT_FILE}\n")
    print("Removal totals:")
    print(audit_df.sum().to_frame("total"))
    flagged = int((df["residual_flags"].str.len() > 0).sum())
    print(f"\nDescriptions with residual flags: {flagged} of {len(df)}")
    print("\nPreview:")
    for _, row in df.head(5).iterrows():
        print("\n--- CVE:", row.get("cve_id", "n/a"))
        print("Sanitised:", row["sanitised_description"])
        if row["residual_flags"]:
            print("Residual flags:", row["residual_flags"])


if __name__ == "__main__":
    main()