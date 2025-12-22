from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


def md_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    if len(df) > max_rows:
        df = df.head(max_rows)
    return df.to_markdown(index=False)


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    tables = repo / "outputs" / "v19" / "tables"
    plots = repo / "outputs" / "v19" / "plots"
    out = repo / "reports"
    out.mkdir(parents=True, exist_ok=True)

    traj = pd.read_csv(tables / "trajectory_baseline.csv")
    scen = pd.read_csv(tables / "scenario_endpoints.csv")
    nep = pd.read_csv(tables / "nep_cost_series.csv")
    eq_grid = pd.read_csv(tables / "equilibria_grid.csv")
    eq_year = pd.read_csv(tables / "equilibria_by_year.csv")
    strat = pd.read_csv(tables / "strategy_freq_baseline.csv")
    scen_ts = pd.read_csv(tables / "scenario_timeseries.csv")

    # abbreviations block
    abbr = """**Abbreviations**

* **NEP**: National Efficient Price (dollars per NWAU; treated here as an index for dynamics)
* **NWAU**: National Weighted Activity Unit (activity weight; payment = NEP × NWAU)
* **VFI**: Vertical fiscal imbalance
* **ED≤4h**: Emergency department presentations completed within 4 hours
* **RR**: Relative risk proxy (dimensionless index; higher is worse)
"""

    # narrative helper
    def fig(path: Path, caption: str) -> str:
        rel = path.relative_to(repo)
        return f"![{caption}]({rel.as_posix()})\n\n*Figure:* {caption}\n"

    # --- build report ---
    report = []
    report.append(f"# NHRA game-theory simulation report (v19)\n\nDate: {date.today()}\n")
    report.append(
        "This report synthesises a stylised, policy-facing simulation of the NHRA negotiation environment as a coupled system of stage games (definition, bargaining, cost shifting, discharge coordination, governance integration, and compliance). "  # noqa: E501
        "The model is not intended to predict an agreed funding share. It is designed to make incentive misalignment legible, stress-test plausible interventions, and surface equilibrium patterns that align with observed operational constraints.\n"
    )
    report.append(abbr)
    report.append("\n## 1. Baseline dynamics\n")
    report.append(
        "Baseline outputs are the mean of Monte Carlo runs from 2025–2030. The core dynamic is a feedback loop: rising pressure worsens discharge and offload, degrading ED performance and raising risk, which in turn increases political salience and audit intensity in the stage games.\n"
    )
    report.append(fig(plots / "baseline_pressure.png", "Baseline system pressure (mean)"))  # noqa: E501
    report.append(fig(plots / "baseline_offload.png", "Baseline ambulance offload delay (mean minutes)"))  # noqa: E501
    report.append(fig(plots / "baseline_within4.png", "Baseline ED performance (proportion within 4 hours)"))  # noqa: E501
    report.append(fig(plots / "baseline_rr.png", "Baseline clinical risk proxy (RR index)"))  # noqa: E501

    report.append("### Table 1. Baseline trajectory summary\n")
    report.append(
        "The table below provides the first years of the baseline trajectory. Full tables are available in `outputs/v19/tables`.\n"
    )
    report.append(md_table(traj[[
        "year","pressure_mean","occupancy_mean","discharge_mean","offload_mean","within4_mean","rr_mean","effgap_mean","cth_effective_mean"
    ]], max_rows=6))
    report.append("\n\n*Interpretation:* pressure and occupancy jointly govern throughput. As the efficiency gap widens, the effective Commonwealth share falls in the model’s accounting identity, intensifying the incentive for cost-shifting.\n")

    report.append("\n## 2. Macro drift: NEP vs input costs\n")
    report.append(
        "IHACPA’s NEP is an annual price per NWAU; the activity-funded payment for a case is the product of NEP and the NWAU weight assigned by the relevant classification. "  # noqa: E501
        "In this model we track NEP and input costs as indices to represent the *direction* of drift and its incentive effects, not the dollar value of any particular DRG.\n"
    )
    report.append(fig(plots / "macro_nep_vs_cost.png", "NEP vs input costs (indices, 2025=1.0)"))  # noqa: E501
    report.append(fig(plots / "macro_nep_to_cost_ratio.png", "NEP-to-cost ratio over time"))  # noqa: E501
    report.append("### Table 2. NEP-to-cost series\n")
    report.append(md_table(nep, max_rows=6))
    report.append(
        "\n\n*Interpretation:* when input costs grow faster than NEP, the NEP-to-cost ratio falls and the ‘efficiency gap’ in practice widens for higher-cost settings (regional, rural, remote). "  # noqa: E501
        "In the model this drift pushes the system toward higher-pressure equilibria unless offset by either NEP realism or demand-relief interventions.\n"
    )

    report.append("\n## 3. Stage-game equilibria\n")
    report.append(
        "Stage games are solved as normal-form games each year using the mean state (pressure, efficiency gap, discharge delay). We enumerate pure-strategy Nash equilibria and compute mixed equilibria for 2×2 games where applicable.\n"  # noqa: E501
    )
    report.append("### Table 3. Equilibria by year and game (first 18 rows)\n")
    report.append(md_table(eq_year.head(18), max_rows=18))
    report.append(
        "\n\n*Interpretation:* multiple equilibria indicate that small changes in assumptions (e.g., political salience or audit intensity) can flip the system between materially different strategic outcomes (e.g., cooperate vs shift). "  # noqa: E501
        "This is why ‘hybrid’ sensitivity analysis is useful: it captures regime switching rather than smooth marginal effects.\n"
    )

    report.append("### Figure set: equilibria count grids\n")
    for g in sorted(eq_grid["game"].unique()):
        report.append(fig(plots / f"equilibria_grid_{g}.png", f"Number of Nash equilibria across a pressure × efficiency-gap grid for {g}"))  # noqa: E501

    report.append("\n## 4. Policy scenarios and intervention effects\n")
    report.append(
        "Scenarios apply individual levers (e.g., pooled funding, UCC integration, aged/NDIS capacity) and two packages. All scenarios are run with the same random seed and Monte Carlo count to support like-for-like comparison.\n"  # noqa: E501
    )
    report.append(fig(plots / "scenario_rr_2030.png", "2030 risk proxy across scenarios"))  # noqa: E501
    report.append(fig(plots / "scenario_pressure_timeseries.png", "Pressure trajectories for key packages"))  # noqa: E501
    report.append(fig(plots / "scenario_rr_timeseries.png", "Risk trajectories for key packages"))  # noqa: E501

    report.append("### Table 4. Scenario endpoints (2030)\n")
    report.append(md_table(scen, max_rows=20))
    report.append(
        "\n\n*Interpretation:* integration levers primarily operate by reducing fragmentation and cost shifting, which lowers demand growth and pressure; macro-alignment levers operate by reducing the NEP-to-cost drift, which narrows the efficiency gap. The full package combines both, and therefore tends to produce the largest reductions in the model’s risk proxy.\n"  # noqa: E501
    )

    report.append("\n## 5. Strategy frequencies\n")
    report.append(
        "The table below reports the most common strategies selected in the Monte Carlo baseline. These are not ‘true’ probabilities; they summarise the model’s behavioural rule under uncertainty.\n"  # noqa: E501
    )
    report.append(md_table(strat.sort_values(["game","freq"], ascending=[True, False]).head(18), max_rows=18))
    report.append(
        "\n\n*Interpretation:* when the model persistently selects cost-shifting or non-integration strategies, it typically reflects a parameterisation where downstream operational costs are externalised across jurisdictions.\n"  # noqa: E501
    )

    report.append("\n## Synthesis and conclusion\n")
    report.append(
        "Across the baseline and scenario analyses, the dominant mechanism is split incentives under VFI: upstream capacity constraints shift demand to the state-funded acute sector, while capped funding and a drifting NEP-to-cost ratio intensify the effective state share and operational risk. "  # noqa: E501
        "In this stylised environment, governance-alignment interventions (pooled funding, UCC integration, aged/NDIS capacity) reduce pressure and risk more reliably than increasing a nominal funding share alone, because they alter the strategic game rather than only the budget envelope. "  # noqa: E501
        "The equilibrium mapping reinforces a practical message for advocates: where multiple equilibria exist, small commitments (e.g., hard interoperability conditions, pooled pilots with credible governance) can ‘select’ the cooperative equilibrium and produce discontinuous improvements in throughput and safety.\n"  # noqa: E501
    )

    out_path = out / f"NHRA_game_theory_report_v19_{date.today().strftime('%Y%m%d')}.md"
    out_path.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote report to: {out_path}")


if __name__ == "__main__":
    main()
