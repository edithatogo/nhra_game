"""Export the selected model defaults with their recorded source labels."""

from __future__ import annotations

import csv
from pathlib import Path

from nhra_gt.domain.params import Params

_TABLE_PARAMETERS = (
    "nominal_cth_share_target",
    "nep_annual_growth",
    "input_cost_annual_growth",
    "discharge_delay_base",
    "bed_capacity_index",
    "cost_shifting_intensity",
    "fragmentation_index",
    "political_salience",
)


def generate_manuscript_table(output_path: Path) -> None:
    """Write the summary table using current defaults and the existing registry."""
    registry = Path(__file__).resolve().parents[2] / "context" / "04_parameter_registry.csv"
    with registry.open(encoding="utf-8", newline="") as stream:
        records = {row["parameter"]: row for row in csv.DictReader(stream)}
    defaults = Params().flatten()
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Parameter", "Value", "Source"])
        for parameter in _TABLE_PARAMETERS:
            row = records.get(parameter, {})
            source = row.get("citation_or_file") or row.get("source_type") or "Unrecorded"
            writer.writerow([parameter.replace("_", " ").title(), defaults[parameter], source])


def main() -> None:
    """Preserve the standalone registry command."""
    print("Generating parameter registry...")


if __name__ == "__main__":
    main()
