"""Public-only grounding check for model inputs.

This enforces that every parameter used by the model is documented in
`context/04_parameter_registry.csv`, and that evidence-linked parameters
use publicly retrievable sources (http/https URLs).

Rules:
- Registry must match the public defaults in `Params` and the inherited scalar
  defaults used only by `ParamsJax`.
- For `source_type` in {"primary","secondary","calibrated","calculated"}:
    - `citation_or_file` must be a public URL (http/https)
    - `locator` must be non-empty
- For `source_type` in {"assumed","normalisation"}:
    - `justification` must be detailed (>=150 chars)
- Numeric bounds must be finite and include the default. Equal endpoints
  identify a fixed reference value.

Usage:
    python scripts/check_parameters_grounded.py
"""

from __future__ import annotations

import csv
import math
import sys
from dataclasses import fields
from importlib import import_module
from pathlib import Path

MINIMUM_JUSTIFICATION_LENGTH = 150
URL_PREFIXES = ("http://", "https://")
EVIDENCE_TYPES_NEED_URL = {"primary", "secondary", "calibrated", "calculated"}
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
    """Print error message and exit with status code 2."""
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def is_public_url(s: str) -> bool:
    """Check if string starts with a known public URL prefix."""
    s = (s or "").strip()
    return s.startswith(URL_PREFIXES)


def scalar_defaults(params_cls):
    """Include scalar defaults used by JAX callers outside the public schema."""
    model = params_cls()
    defaults = model.flatten()
    runtime = model.to_params_jax()
    for field in fields(runtime):
        value = getattr(runtime, field.name)
        if field.name not in defaults and type(value) in (bool, int, float, str):
            defaults[field.name] = value
    return defaults


def _matches_default(raw: str, expected: object) -> bool:
    value = raw.strip()
    if type(expected) in (int, float):
        try:
            parsed = type(expected)(value)
        except ValueError:
            return False
        return parsed == expected and (type(parsed) is int or math.isfinite(parsed))
    if expected is None or isinstance(expected, bool):
        return value.casefold() == str(expected).casefold()
    return value == expected


def _bounds_error(low: str, high: str, default: float) -> str | None:
    if not low.strip() or not high.strip():
        return "numeric value requires range_low and range_high"
    try:
        lower, upper = float(low), float(high)
    except ValueError:
        return "range_low/high must be numeric"
    if not (math.isfinite(lower) and math.isfinite(upper)):
        return "range_low/high must be finite"
    if lower > upper:
        return "range_low > range_high"
    if not lower <= default <= upper:
        return "range_low/high must include the runtime default"
    return None


def _row_failures(rows: list[dict[str, str]], defaults: dict[str, object]) -> list[str]:
    failures: list[str] = []
    for idx, r in enumerate(rows, start=2):
        st = (r["source_type"] or "").strip().lower()
        cite = (r["citation_or_file"] or "").strip()
        loc = (r["locator"] or "").strip()
        just = (r["justification"] or "").strip()
        name = r["parameter"].strip()

        if st not in EVIDENCE_TYPES_NEED_URL | EVIDENCE_TYPES_NEED_JUSTIFICATION:
            failures.append(f"L{idx}: {name}: unknown source_type {st!r}")
        if not (r["description"].strip() and r["units"].strip()):
            failures.append(f"L{idx}: {name}: description and units are required")

        if st in EVIDENCE_TYPES_NEED_URL:
            if not is_public_url(cite):
                failures.append(
                    f"L{idx}: {r['parameter']}: source_type={st} requires public URL in citation_or_file"
                )
            if not loc:
                failures.append(
                    f"L{idx}: {r['parameter']}: source_type={st} requires non-empty locator"
                )

        if st in EVIDENCE_TYPES_NEED_JUSTIFICATION and len(just) < MINIMUM_JUSTIFICATION_LENGTH:
            failures.append(
                f"L{idx}: {r['parameter']}: source_type={st} requires detailed justification (>=150 chars)"
            )

        if cite.startswith("internal://"):
            failures.append(f"L{idx}: {r['parameter']}: citation_or_file cannot be internal://")

        if name not in defaults:
            continue
        expected = defaults[name]
        if not _matches_default(r["value"], expected):
            failures.append(
                f"L{idx}: {name}: documented value differs from runtime default {expected!r}"
            )
        if type(expected) in (int, float):
            bounds_error = _bounds_error(r["range_low"], r["range_high"], expected)
            if bounds_error is not None:
                failures.append(f"L{idx}: {r['parameter']}: {bounds_error}")
    return failures


def main() -> None:
    """Verify that all parameters in the registry have valid evidence."""
    root = Path(__file__).resolve().parents[1]
    reg_path = root / "context" / "04_parameter_registry.csv"
    if not reg_path.exists():
        die(f"Missing registry: {reg_path}")

    # Import model parameters
    sys.path.insert(0, str(root / "src"))
    try:
        params_cls = import_module("nhra_gt.domain.params").Params
    except ImportError as e:
        die(f"Could not import nhra_gt.domain.params.Params: {e}")

    defaults = scalar_defaults(params_cls)
    model_params = set(defaults)

    with reg_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        if headers not in (REQUIRED_COLS, [*REQUIRED_COLS, "group"]):
            die(
                "Registry header must match required columns exactly. "
                f"Expected {REQUIRED_COLS} with an optional trailing group; got {headers}"
            )
        rows = list(reader)
    if any(None in row or None in row.values() for row in rows):
        die("Registry rows must have the same columns as the header")

    registry_params = [r["parameter"].strip() for r in rows]
    if len(set(registry_params)) != len(registry_params):
        dups = sorted({p for p in registry_params if registry_params.count(p) > 1})
        die(f"Duplicate parameters in registry: {dups}")

    extra = sorted(set(registry_params) - model_params)
    missing = sorted(model_params - set(registry_params))
    failures: list[str] = []
    if extra:
        failures.append(
            f"Registry contains {len(extra)} parameters absent from model Params: {extra}"
        )
    if missing:
        failures.append(
            f"Registry is missing {len(missing)} parameters from model Params: {missing}"
        )
    failures.extend(_row_failures(rows, defaults))

    if failures:
        print("\n".join(failures), file=sys.stderr)
        die(f"{len(failures)} grounding failures in {reg_path}")

    print(f"OK: grounding check passed ({len(rows)} parameters).")


if __name__ == "__main__":
    main()
