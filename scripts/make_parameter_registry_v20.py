from __future__ import annotations

"""Generate (or regenerate) the parameter registry for v9.Params.

This script is intended to be run whenever Params changes.
It writes:
  context/04_parameter_registry.csv

It pre-populates a handful of parameters with public sources.
Everything else is marked as 'assumed' with a required justification and plausible range.

Usage:
  python scripts/make_parameter_registry_v20.py

No network calls are performed.
"""

import csv
from dataclasses import fields
from pathlib import Path


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    ctx = repo / "context"
    ctx.mkdir(exist_ok=True)

    # Import Params
    import sys

    sys.path.insert(0, str(repo / "src"))
    from nhra_game_theory.engine import Params  # type: ignore

    p = Params()

    # Public sources (URLs only; no bundled copyrighted documents)
    SOURCES = {
        "cap_growth": {
            "evidence_type": "primary",
            "units": "fraction per year",
            "model_component": "NHRA cap",
            "source_url": "https://www.publichospitalfunding.gov.au/basis-national-health-reform-funding-commonwealth-2020-21-2024-25",
            "source_locator": "Funding Cap (A56): 6.5%",
            "notes": "NHFB summary of Addendum clause A56 / funding cap.",
        },
        "within4_base": {
            "evidence_type": "secondary",
            "units": "fraction",
            "model_component": "ED performance",
            "source_url": "https://www.aihw.gov.au/reports-data/myhospitals/sectors/emergency-department-care",
            "source_locator": "Indicator: ED presentations completed within 4 hours",
            "notes": "Use latest available national figure when updating.",
        },
        "nep_per_nwau_start": {
            "evidence_type": "primary",
            "units": "$ per NWAU (or index=1)",
            "model_component": "IHACPA NEP",
            "source_url": "https://www.ihacpa.gov.au/resources/national-efficient-price-determination-2025-26",
            "source_locator": "NEP value (annual $/NWAU)",
            "notes": "Model uses NEP mostly for reporting; set to index=1 unless using actual $/NWAU.",
        },
        "nep_annual_growth": {
            "evidence_type": "primary",
            "units": "fraction per year",
            "model_component": "IHACPA NEP",
            "source_url": "https://www.ihacpa.gov.au/resources/national-efficient-price-determination-2025-26",
            "source_locator": "Indexation / growth assumptions (update manually)",
            "notes": "Keep as scenario parameter; use public determination for plausibility.",
        },
        "input_cost_annual_growth": {
            "evidence_type": "primary",
            "units": "fraction per year",
            "model_component": "Input cost drift",
            "source_url": "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia",
            "source_locator": "WPI: Health care and social assistance (use latest annual change)",
            "notes": "Proxy for workforce cost growth; adjust as needed.",
        },
    }

    # Default templates
    def default_row(name: str, value: object) -> dict[str, str]:
        return {
            "parameter": name,
            "default_value": str(value),
            "units": "unitless",
            "model_component": "mechanism",
            "evidence_type": "assumed",
            "source_url": "",
            "source_locator": "",
            "justification": (
                "Stylised mechanism parameter used for scenario comparison rather than forecasting. "
                "Default chosen for face-valid dynamics; explored in sensitivity analysis."
            ),
            "plausible_range": "see sensitivity grid",
            "notes": "",
        }

    rows: list[dict[str, str]] = []
    for f in fields(Params):
        name = f.name
        value = getattr(p, name)
        row = default_row(name, value)
        if name in SOURCES:
            row.update({k: str(v) for k, v in SOURCES[name].items()})
            # Evidence types with source don't require long justification
            row["justification"] = "Public source provides a defensible anchor; treat as scenario input when uncertain."
            row["plausible_range"] = "(scenario)"
        else:
            # Provide parameter-specific plausible ranges where helpful
            if isinstance(value, int | float):
                if name.endswith("_growth"):
                    row["plausible_range"] = "0.00–0.08"
                elif "share" in name:
                    row["plausible_range"] = "0.25–0.55"
                elif "ratio" in name:
                    row["plausible_range"] = "0.60–1.05"
                elif "weight" in name:
                    row["plausible_range"] = "0.00–0.60"
                elif "base" in name:
                    row["plausible_range"] = "±25%"
                elif "noise" in name:
                    row["plausible_range"] = "0.00–0.10"

        rows.append(row)

    out = ctx / "04_parameter_registry.csv"
    header = [
        "parameter",
        "default_value",
        "units",
        "model_component",
        "evidence_type",
        "source_url",
        "source_locator",
        "justification",
        "plausible_range",
        "notes",
    ]

    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
