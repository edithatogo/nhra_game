"""Render the baseline scenario summary and its existing figures as a PDF."""

from __future__ import annotations

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape

from plotly.io import write_images
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table

from nhra_gt.engine import Params, run_hybrid, summarise_outcome
from nhra_gt.visualization.interactive import plot_phase_space, plot_vfi_waterfall


def generate_brief(scenario_name: str, output_path: Path) -> None:
    """Generate a PDF of the baseline rollout with the supplied display name."""
    years = list(range(2025, 2031))
    trajectory, _ = run_hybrid(years, Params(), n_mc=50, seed=42)
    summary = summarise_outcome(trajectory)
    funding = plot_vfi_waterfall(
        nominal_share=summary["effshare_nominal_2030"],
        indexation_loss=summary["leakage_indexation"],
        cap_loss=summary["leakage_cap"],
        audit_loss=summary["leakage_audit"],
        adjustment_loss=summary["leakage_adjustment"],
        effective_share=summary["effshare_effective_2030"],
    )
    phase_space = plot_phase_space(trajectory)
    styles = getSampleStyleSheet()
    table = [
        ["Metric", "2030 simulated value"],
        ["Nominal Commonwealth share", f"{summary['effshare_nominal_2030']:.1%}"],
        ["Effective Commonwealth share", f"{summary['effshare_effective_2030']:.1%}"],
        ["Relative risk proxy", f"{summary['rr_2030']:.2f}"],
        ["Within four hours", f"{summary['within4_2030']:.1%}"],
        ["Cumulative pressure", f"{summary['cumulative_pressure_2030']:.2f}"],
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".nhra-brief-", dir=output_path.parent) as temp:
        scratch = Path(temp)
        waterfall = scratch / "waterfall.png"
        phase = scratch / "phase-space.png"
        write_images([funding, phase_space], [waterfall, phase], width=800, height=400)
        document = scratch / "brief.pdf"
        SimpleDocTemplate(str(document), pagesize=A4).build(
            [
                Paragraph(f"NHRA Policy Brief — {escape(scenario_name)}", styles["Title"]),
                Paragraph(
                    "Baseline model results for 2025 to 2030 from 50 simulations with seed 42.",
                    styles["Normal"],
                ),
                Paragraph("Funding leakage", styles["Heading2"]),
                Image(str(waterfall), width=450, height=225),
                Paragraph("Pressure and occupancy", styles["Heading2"]),
                Image(str(phase), width=450, height=225),
                Paragraph("Summary metrics", styles["Heading2"]),
                Table(table, colWidths=[220, 140]),
            ]
        )
        document.replace(output_path)


def main() -> None:
    """Write the baseline PDF brief."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="Baseline Scenario")
    parser.add_argument("--output", type=Path, default=Path("reports/policy_brief_2030.pdf"))
    args = parser.parse_args()
    generate_brief(args.name, args.output)


if __name__ == "__main__":
    main()
