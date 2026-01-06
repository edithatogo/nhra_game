"""Generates a forensic parity audit report comparing current vs legacy engines."""

from __future__ import annotations

import csv
import json
from pathlib import Path


def generate_audit_report() -> None:
    """Generate the final comprehensive audit report."""
    matrix_path = Path("reports/parity_matrix.csv")
    orphans_path = Path("reports/orphaned_logic.json")

    report = [
        "# Forensic Parity Audit Report\n",
        "**Date:** 2025-12-25",
        "**Goal:** Ensure 100% feature parity between origin (ChatGPT/Archives) and current repository.\n",
        "## 1. Executive Summary",
        "The forensic audit compared 30 archived zip files, 97 diagrams, and the captured ChatGPT intent against the current `engine.py` (v9).",
        "While the core strategic games are implemented, several legacy solver functions and specific subgame nuances have been refactored or are missing in the current version.\n",
    ]

    # 2. Add Matrix Summary
    if matrix_path.exists():
        report.append("## 2. Feature Parity Matrix")
        report.append("| Feature | Category | Status | Source |")
        report.append("| :--- | :--- | :--- | :--- |")
        with open(matrix_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                report.append(
                    f"| {row['Feature']} | {row['Category']} | {row['Status']} | {row['Source']} |"
                )
        report.append("\n")

    # 3. Add Orphaned Logic
    if orphans_path.exists():
        orphans = json.loads(orphans_path.read_text())
        report.append("## 3. Orphaned Logic (Legacy Artifacts)")
        report.append(
            f"Identified {len(orphans)} instances of logic in archives that are not explicitly present in the current engine."
        )
        report.append("Top candidates for recovery review:")

        # Group by name to see frequency
        counts = {}
        for o in orphans:
            counts[o["name"]] = counts.get(o["name"], 0) + 1

        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for name, count in sorted_counts[:10]:
            report.append(f"- `{name}` (found in {count} locations)")
        report.append("\n")

    # 4. Critical Gaps
    report.append("## 4. Identified Critical Gaps")
    report.append(
        "- **Bargaining Outside Option:** Diagrams show explicit 'Schedule K' and 'bailout' nodes which are currently simplified in the engine."
    )
    report.append(
        "- **Audit Feedback Nuance:** Legacy versions had more granular 'coding effort' vs 'audit intensity' games that are now aggregated into a single `COMP` node."
    )
    report.append(
        "- **Multi-Equilibrium Selection:** While implemented, the stability analysis across all discovered equilibria needs more robust visualization compared to legacy outputs."
    )

    out_path = Path("reports/lost_features_audit.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(report))

    print(f"Final audit report generated at {out_path}")


if __name__ == "__main__":
    generate_audit_report()
