from __future__ import annotations

from pathlib import Path

import pandas as pd

DATE = "20251221"

def md_image(path: Path, alt: str) -> str:
    return f"![{alt}]({path.as_posix()})"

def main() -> None:
    out = Path("outputs/v16")
    plots = out / "plots"
    tables = out / "tables"
    rep_dir = Path("reports")
    rep_dir.mkdir(exist_ok=True)

    pd.read_csv(tables / "trajectory.csv")
    scen = pd.read_csv(tables / "scenario_summary.csv")
    pd.read_csv(tables / "equilibria_by_year.csv")
    pd.read_csv(tables / "sensitivity_oneway.csv")
    pd.read_csv(tables / "influence_edges.csv")

    md = []
    md.append("# NHRA game-theory modelling report (v16)\n\n**Date:** 21 December 2025\n\n")
    md.append("## Abbreviations\n")
    md.append("- **NHRA**: National Health Reform Agreement\n- **NEP**: National Efficient Price (annual $/NWAU)\n- **NWAU**: National Weighted Activity Unit\n- **VFI**: Vertical fiscal imbalance\n- **UCC**: Medicare Urgent Care Clinic\n")
    md.append("\n## 1. What this model is for\n")
    md.append("This report presents a stylised systems-and-games model of NHRA negotiation dynamics. The intent is not to predict a single ‘correct’ future, but to clarify **mechanisms**: how incentives and funding rules can translate into hospital flow constraints and clinical risk proxies. All quantitative outputs should be interpreted as **scenario comparisons** rather than point forecasts.\n")

    md.append("\n## 2. Baseline dynamics\n")
    md.append("The baseline simulation traces pressure, occupancy, discharge delay, and a simple ambulance offload proxy from 2025–2030. The variables are dimensionless indices; changes are interpretable as relative worsening/improvement rather than absolute minutes or dollars.\n")
    for fn, cap in [
        ("baseline_pressure.png", "Figure 1. Baseline system pressure index over time."),
        ("baseline_within4.png", "Figure 2. Baseline within-4-hours proxy over time."),
        ("baseline_rr_proxy.png", "Figure 3. Baseline safety-risk proxy over time."),
        ("baseline_effgap.png", "Figure 4. Baseline efficiency-gap index over time."),
        ("baseline_offload.png", "Figure 5. Baseline ambulance offload proxy over time."),
    ]:
        p = plots / fn
        if p.exists():
            md.append("\n" + md_image(p, cap) + f"\n\n*{cap}*\n")

    md.append("\n### Interpretation\n")
    md.append("In the baseline, pressure rises when demand and discharge constraints outpace system capacity. The model represents the widely observed feedback loop in which delayed discharge increases occupancy, which in turn impairs ED throughput and ambulance offload.\n")

    md.append("\n## 3. Strategic ‘games’ and equilibrium behaviour\n")
    md.append("Each year’s state (pressure, efficiency gap, discharge delay) parameterises a set of small strategic subgames (definition, bargaining, cost shifting, discharge coordination, governance integration, compliance). We solve **all Nash equilibria** (pure and mixed where applicable) and report equilibrium multiplicity and representative equilibria at each year’s mean state.\n")
    for fn, cap in [
        ("equilibria_count_over_time_DEF.png", "Figure 6. Number of Nash equilibria over time (Definition game)."),
        ("equilibria_count_over_time_SHIFT.png", "Figure 7. Number of Nash equilibria over time (Cost-shifting game)."),
        ("equilibria_grid_DEF.png", "Figure 8. Equilibrium regions for the Definition game over the pressure × efficiency-gap grid."),
        ("equilibria_grid_SHIFT.png", "Figure 9. Equilibrium regions for the Cost-shifting game over the pressure × efficiency-gap grid."),
    ]:
        p = plots / fn
        if p.exists():
            md.append("\n" + md_image(p, cap) + f"\n\n*{cap}*\n")

    md.append("\n### Interpretation\n")
    md.append("Where multiple equilibria exist, the system can ‘flip’ between strategies under small changes in pressure or valuation conditions. This is one reason the model emphasises scenario robustness and equilibrium-selection sensitivity in later versions.\n")

    md.append("\n## 4. Scenario analysis of policy interventions\n")
    md.append("Scenarios are configured as parameter packages corresponding to realistic negotiation levers (e.g., reducing fragmentation through governance integration, improving discharge coordination, or reducing avoidable demand). The scenario table below reports end-of-horizon outcomes.\n\n")
    md.append(scen.to_markdown(index=False))
    md.append("\n\n**Table 1.** Scenario summary (end-of-horizon outcomes).\n")

    md.append("\n### Interpretation\n")
    md.append("The key comparison is between funding-only changes and governance packages that reduce fragmentation and discharge constraints. In this model class, interventions that shift incentives and reduce the discharge bottleneck produce larger improvements in flow proxies than nominal share adjustments alone.\n")

    md.append("\n## 5. Uncertainty and sensitivity\n")
    md.append("A one-way sensitivity analysis varies each parameter around its baseline value and re-simulates the system. This highlights which assumptions matter most for the ambulance offload proxy.\n")
    for fn, cap in [
        ("sensitivity_tornado_offload_2030.png", "Figure 10. One-way sensitivity tornado plot for ambulance offload (2030)."),
        ("influence_edges_bar.png", "Figure 11. Influence edges (one-way effects) on ambulance offload (2030)."),
    ]:
        p = plots / fn
        if p.exists():
            md.append("\n" + md_image(p, cap) + f"\n\n*{cap}*\n")

    md.append("\n### Interpretation\n")
    md.append("Parameters governing demand growth, discharge performance, and fragmentation typically dominate the offload outcome. This supports RACMA’s framing that governance and system integration can be as important as the headline Commonwealth contribution rate.\n")

    md.append("\n## 6. Synthesis and conclusion\n")
    md.append("Across baseline, scenario, and sensitivity analyses, the model consistently indicates that **structural alignment** (reduced fragmentation and improved discharge coordination) is a high-leverage pathway to safer throughput. A negotiation position that treats the 45% target as a facilitator for integration—rather than a standalone fix—is more robust to uncertainty in valuation and cost conditions.\n")

    out_md = rep_dir / f"v16_report_{DATE}.md"
    out_md.write_text("\n".join(md), encoding="utf-8")

if __name__ == "__main__":
    main()
