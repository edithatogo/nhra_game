from __future__ import annotations

"""Public-only grounding check for model inputs.

This enforces that every parameter used by the model is documented in
`context/04_parameter_registry.csv`, and that evidence-linked parameters
use publicly retrievable sources (http/https URLs).

Rules:
- Registry must contain exactly the parameters in `nhra_gt.engine.Params`
- For `source_type` in {"primary","secondary","calibrated"}:
    - `citation_or_file` must be a public URL (http/https)
    - `locator` must be non-empty
- For `source_type` in {"assumed","normalisation"}:
    - `justification` must be detailed (>=150 chars)
- For numeric parameters:
    - `range_low` and `range_high` must be provided (for sensitivity)

Usage:
    python scripts/check_parameters_grounded.py
"""

import csv
import sys
from dataclasses import fields
from pathlib import Path

URL_PREFIXES = ("http://", "https://")
EVIDENCE_TYPES_NEED_URL = {"primary", "secondary", "calibrated"}
EVIDENCE_TYPES_NEED_JUSTIFICATION = {"assumed", "normalisation"}

REQUIRED_COLS = [
    "parameter",
    "description",
    "value",
    "units",
    "source_type",
    "citation_or_file",
    "locator",
    "range_low",
    "range_high",
    "justification",
]


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def is_public_url(s: str) -> bool:
    s = (s or "").strip()
    return s.startswith(URL_PREFIXES)


def is_boolish(v: str) -> bool:
    return v.strip().lower() in {"true", "false"}


def is_numeric(v: str) -> bool:
    if is_boolish(v):
        return False
    try:
        float(v)
        return True
    except Exception:
        return False


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    reg_path = root / "context" / "04_parameter_registry.csv"
    if not reg_path.exists():
        die(f"Missing registry: {reg_path}")

    # Import model parameters
    sys.path.insert(0, str(root / "src"))
    try:
        from nhra_gt.engine import Params  # type: ignore
    except Exception as e:
        die(f"Could not import nhra_gt.engine.Params: {e}")

    model_params = {f.name for f in fields(Params)}

    with reg_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if list(reader.fieldnames or []) != REQUIRED_COLS:
            die(
                "Registry header must match required columns exactly. "
                f"Expected {REQUIRED_COLS}; got {list(reader.fieldnames or [])}"
            )
        rows = list(reader)

    registry_params = [r["parameter"].strip() for r in rows]
    if len(set(registry_params)) != len(registry_params):
        dups = sorted({p for p in registry_params if registry_params.count(p) > 1})
        die(f"Duplicate parameters in registry: {dups}")

    extra = sorted(set(registry_params) - model_params)
    missing = sorted(model_params - set(registry_params))
    if extra:
        die(f"Registry contains parameters not in model Params: {extra}")
    if missing:
        die(f"Registry missing parameters from model Params: {missing}")

    failures: list[str] = []
    for idx, r in enumerate(rows, start=2):
        st = (r["source_type"] or "").strip().lower()
        cite = (r["citation_or_file"] or "").strip()
        loc = (r["locator"] or "").strip()
        just = (r["justification"] or "").strip()

        if st in EVIDENCE_TYPES_NEED_URL:
            if not is_public_url(cite):
                failures.append(
                    f"L{idx}: {r['parameter']}: source_type={st} requires public URL in citation_or_file"
                )
            if not loc:
                failures.append(
                    f"L{idx}: {r['parameter']}: source_type={st} requires non-empty locator"
                )

        if st in EVIDENCE_TYPES_NEED_JUSTIFICATION and len(just) < 150:
            failures.append(
                f"L{idx}: {r['parameter']}: source_type={st} requires detailed justification (>=150 chars)"
            )

        if cite.startswith("internal://"):
            failures.append(f"L{idx}: {r['parameter']}: citation_or_file cannot be internal://")

        # Numeric sensitivity bounds required
        if is_numeric(r["value"]):
            lo = (r["range_low"] or "").strip()
            hi = (r["range_high"] or "").strip()
            if lo == "" or hi == "":
                failures.append(
                    f"L{idx}: {r['parameter']}: numeric value requires range_low and range_high"
                )
            else:
                try:
                    lo_f = float(lo)
                    hi_f = float(hi)
                    if lo_f > hi_f:
                        failures.append(f"L{idx}: {r['parameter']}: range_low > range_high")
                except Exception:
                    failures.append(f"L{idx}: {r['parameter']}: range_low/high must be numeric")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        die(f"{len(failures)} grounding failures in {reg_path}")

    print(f"OK: grounding check passed ({len(rows)} parameters).")


if __name__ == "__main__":
    main()
