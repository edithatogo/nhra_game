"""Generates a Markdown inventory of all registered figures."""

import json
from pathlib import Path

import pandas as pd


def main() -> None:
    """Read registry and generate inventory report."""
    registry_path = Path("docs/reports/figure_registry.json")
    output_path = Path("docs/reports/figure_inventory.md")

    if not registry_path.exists():
        print(f"Registry not found at {registry_path}")
        return

    with open(registry_path) as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df.to_csv(registry_path.with_suffix(".csv"), index=False)

    lines = []
    lines.append("# Figure Inventory")
    lines.append("")
    lines.append(f"Generated from `{registry_path}`.")
    lines.append("")

    # Active Figures
    lines.append("## Active Figures")
    lines.append("")
    active_df = df[df["status"] == "active"]
    if not active_df.empty:
        lines.append("| ID | Description | Source | Output |")
        lines.append("|---|---|---|---|")
        for _, row in active_df.iterrows():
            source = f"`{row['source_file']}`"
            if row["function_name"] != "(script)":
                source += f" (`{row['function_name']}`)"
            lines.append(
                f"| **{row['id']}** | {row['description']} | {source} | `{row['output_path']}` |"
            )
    else:
        lines.append("_No active figures found._")
    lines.append("")

    # Missing/Legacy Figures
    lines.append("## Missing / Legacy Figures")
    lines.append("")
    missing_df = df[df["status"] == "missing"]
    if not missing_df.empty:
        lines.append("| ID | Description | Source | Output |")
        lines.append("|---|---|---|---|")
        for _, row in missing_df.iterrows():
            lines.append(
                f"| **{row['id']}** | {row['description']} | {row['source_file']} | `{row['output_path']}` |"
            )
    else:
        lines.append("_No missing figures identified._")
    lines.append("")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Report generated at {output_path}")


if __name__ == "__main__":
    main()
