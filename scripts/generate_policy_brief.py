from __future__ import annotations

import argparse
import sys
from pathlib import Path

import plotly.io as pio
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Add src to path
sys.path.append("src")

from nhra_gt.engine import Params, run_hybrid, summarise_outcome
from nhra_gt.visualization.interactive import plot_phase_space, plot_vfi_waterfall


def generate_brief(scenario_name: str, output_path: Path):
    """Generates a professional PDF policy brief for a given scenario."""

    # 1. Run Simulation
    years = list(range(2025, 2031))
    p = Params()
    traj, _ = run_hybrid(years, p, n_mc=50, seed=42)
    summary = summarise_outcome(traj)

    # 2. Generate Static Figures
    tmp_dir = Path("outputs/temp_reports")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Waterfall
    fig_wf = plot_vfi_waterfall(
        nominal_share=summary["effshare_nominal_2030"],
        indexation_loss=summary["leakage_indexation"],
        cap_loss=summary["leakage_cap"],
        audit_loss=summary["leakage_audit"],
        adjustment_loss=summary["leakage_adjustment"],
        effective_share=summary["effshare_effective_2030"],
    )
    wf_img_path = tmp_dir / "waterfall.png"
    pio.write_image(fig_wf, str(wf_img_path), width=800, height=400)

    # Phase Space
    fig_ps = plot_phase_space(traj)
    ps_img_path = tmp_dir / "phase_space.png"
    pio.write_image(fig_ps, str(ps_img_path), width=800, height=400)

    # 3. Build PDF
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"NHRA Strategic Policy Brief: {scenario_name}", styles["Title"]))
    story.append(Paragraph("Date: 2025-12-28", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Executive Summary
    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    summary_text = (
        f"This simulation forecasts hospital system performance and funding dynamics for the 2025-2030 period. "
        f"By 2030, the effective Commonwealth funding share is projected to reach **{summary['effshare_effective_2030']*100:.1f}%**, "
        f"representing a significant departure from the nominal target of **{summary['effshare_nominal_2030']*100:.1f}%** due to indexation and cap leakage."
    )
    story.append(Paragraph(summary_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Funding Leakage
    story.append(Paragraph("1. Funding Leakage Analysis (VFI)", styles["Heading3"]))
    story.append(Image(str(wf_img_path), width=450, height=225))
    story.append(
        Paragraph(
            "The waterfall above decomposes the 'leakage' between policy commitment and operational reality.",
            styles["Italic"],
        )
    )
    story.append(Spacer(1, 12))

    # System Dynamics
    story.append(Paragraph("2. System Stability & Hysteresis", styles["Heading3"]))
    story.append(Image(str(ps_img_path), width=450, height=225))
    story.append(
        Paragraph(
            "The phase-space trajectory highlights the relationship between pressure and occupancy, indicating potential recovery paths from crisis modes.",
            styles["Italic"],
        )
    )
    story.append(Spacer(1, 12))

    # Metrics Table
    story.append(Paragraph("3. Summary Metrics (2030 Forecast)", styles["Heading3"]))
    data = [
        ["Metric", "Value"],
        ["Effective Share (%)", f"{summary['effshare_effective_2030']*100:.1f}%"],
        ["Relative Risk Proxy", f"{summary['rr_2030']:.2f}"],
        ["Within 4 Hours (%)", f"{summary['within4_2030']*100:.1f}%"],
        ["Cumulative Pressure", f"{summary['cumulative_pressure_2030']:.2f}"],
    ]

    t = Table(data, colWidths=[200, 100])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(t)

    doc.build(story)
    print(f"Policy Brief generated: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate NHRA Policy Brief PDF")
    parser.add_argument("--name", type=str, default="Baseline Scenario")
    parser.add_argument("--output", type=str, default="reports/policy_brief_2030.pdf")
    args = parser.parse_args()

    out_file = Path(args.output)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    generate_brief(args.name, out_file)
