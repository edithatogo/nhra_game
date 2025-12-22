from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pandas as pd


def md_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    if len(df) > max_rows:
        df = df.head(max_rows)
    return df.to_markdown(index=False)


def main() -> None:
    out = Path("outputs/v17")
    tables = out / "tables"
    plots = out / "plots"

    repdir = Path("reports")
    repdir.mkdir(parents=True, exist_ok=True)

    traj = pd.read_csv(tables / "trajectory.csv")
    nep = pd.read_csv(tables / "nep_series.csv")
    scen = pd.read_csv(tables / "scenario_summary.csv")
    interv = pd.read_csv(tables / "intervention_scenarios.csv")
    deltas = pd.read_csv(tables / "intervention_deltas.csv")
    eq_grid = pd.read_csv(tables / "equilibria_grid.csv")
    eq_year = pd.read_csv(tables / "equilibria_by_year.csv")

    # Baseline end-year summary
    end_year = int(traj.iloc[-1]["year"])
    baseline_end = traj.iloc[-1][
        [
            "rr_mean",
            "pressure_mean",
            "offload_mean",
            "within4_mean",
            "effgap_mean",
            "occupancy_mean",
        ]
    ].to_frame().T
    nep_end = nep[nep["year"] == end_year][["nep_per_nwau", "efficient_payment"]]
    if len(nep_end) == 1:
        baseline_end["nep_per_nwau"] = float(nep_end.iloc[0]["nep_per_nwau"])
        baseline_end["efficient_payment"] = float(nep_end.iloc[0]["efficient_payment"])
    baseline_end.insert(0, "year", end_year)

    # Equilibria summaries
    eq_summary = (
        eq_grid.groupby("game")
        .agg(n_grid_points=("n_equilibria", "size"), mean_n=("n_equilibria", "mean"), any_mixed=("has_mixed", "max"))
        .reset_index()
    )
    eqcount = (
        eq_year.groupby(["year", "game"])["n_equilibria_in_game"]
        .max()
        .reset_index()
        .rename(columns={"n_equilibria_in_game": "n_equilibria"})
    )

    md: list[str] = []
    md.append("# NHRA game-theory mechanism simulation — v17 report (2025–2030)")
    md.append("")
    md.append("**Date:** 21 Dec 2025  \
**Version:** v17 (Round 2 implementation)  \
**Purpose:** Provide decision-relevant outputs for RACMA policy positioning. This is a **stylised mechanism model** intended to clarify incentive structures and plausible directions of effect, not to generate point forecasts.")
    md.append("")
    md.append("## Abbreviations")
    md.append("")
    md.append(
        dedent(
            """
            - **ABF** activity-based funding  
            - **ED** emergency department  
            - **IHACPA** Independent Health and Aged Care Pricing Authority  
            - **LHN/LHD** Local Hospital Network / Local Health District  
            - **NDIS** National Disability Insurance Scheme  
            - **NEP** National Efficient Price (annual **$/NWAU**)  
            - **NHRA** National Health Reform Agreement  
            - **NWAU** National Weighted Activity Unit  
            - **UCC** (Medicare) Urgent Care Clinic  
            - **VFI** vertical fiscal imbalance  
            """
        ).strip()
    )
    md.append("")
    md.append("## 1. Baseline dynamics (2025–2030)")
    md.append("")
    md.append("The baseline trajectory summarises how the model’s coupled state variables evolve when incentives are left in the default configuration. Outcomes are best interpreted as *directional indicators*.")
    md.append("")
    md.append("### Table 1. End-year baseline summary (mean values)")
    md.append("")
    md.append(md_table(baseline_end.round(4)))
    md.append("")
    md.append("### Figure 1. Baseline pressure (mean)")
    md.append("")
    md.append(f"![Baseline pressure]({plots/'baseline_pressure.png'})")
    md.append("")
    md.append("*Caption:* Pressure is a latent composite index capturing system stress and political salience. It rises when discharge delay and valuation divergence increase, and it falls when throughput improves.")
    md.append("")
    md.append("### Figure 2. Baseline ambulance offload delay (mean)")
    md.append("")
    md.append(f"![Baseline offload]({plots/'baseline_offload.png'})")
    md.append("")
    md.append("*Caption:* Offload delay is a proxy outcome driven by high occupancy and constrained patient flow. Interpret **direction and relative differences** across scenarios.")
    md.append("")
    md.append("### Figure 3. Baseline within-4-hours (mean)")
    md.append("")
    md.append(f"![Baseline within4]({plots/'baseline_within4.png'})")
    md.append("")
    md.append("*Caption:* Within-4-hours is treated as a throughput proxy. Declines indicate worsening access/exit block in the model’s simplified ED–ward coupling.")
    md.append("")
    md.append("### Figure 4. NEP scaffolding (index discipline)")
    md.append("")
    md.append(f"![NEP index]({plots/'baseline_nep_index.png'})")
    md.append("")
    md.append("*Caption:* NEP is an annual **$/NWAU index** (default starts at 1.0). Efficient payment is NEP×representative NWAU. The model does **not** implement IHACPA’s detailed NWAU calculators; NEP is included to keep the valuation story disciplined.")
    md.append("")
    md.append("## 2. Equilibria structure of stage games")
    md.append("")
    md.append("The model uses several 2×2 stage games (definition, bargaining, cost shifting, discharge coordination, governance integration, compliance). For transparency, v17 exports **all Nash equilibria** (pure + mixed) by year at the mean system state.")
    md.append("")
    md.append("### Table 2. Equilibria grid summary")
    md.append("")
    md.append(md_table(eq_summary.round(3)))
    md.append("")
    md.append("### Figure 5. Equilibrium multiplicity over time — DEF")
    md.append("")
    md.append(f"![Equilibria DEF]({plots/'equilibria_count_over_time_DEF.png'})")
    md.append("")
    md.append("*Caption:* Multiple equilibria correspond to plausible ‘regimes’ (cooperative vs adversarial). Policy levers that change pressure, valuation divergence, or discharge delay can move the system into regions where different equilibria are available or selected.")
    md.append("")
    md.append("## 3. Scenario analysis (structural regimes)")
    md.append("")
    md.append("Scenarios stress-test structural claims (fragmentation, cost shifting, cap mechanics) and equilibrium selection assumptions. Read differences as robustness checks for the governance narrative.")
    md.append("")
    md.append("### Table 3. End-year scenario summary (2030 means)")
    md.append("")
    md.append(md_table(scen.round(4), max_rows=30))
    md.append("")
    md.append("### Figure 6. Scenario risk proxy in 2030 (mean)")
    md.append("")
    md.append(f"![Scenario risk]({plots/'scenario_rr_bar.png'})")
    md.append("")
    md.append("*Caption:* The risk proxy aggregates pressure and offload delay with configurable weights. Lower values indicate improved system performance in the model’s simplified representation.")
    md.append("")
    md.append("## 4. Policy intervention scenarios (directional levers)")
    md.append("")
    md.append("Each intervention is implemented as an interpretable parameter shift corresponding to a negotiable policy lever. Outputs are provided as both endpoints and **deltas vs baseline** to prevent false precision.")
    md.append("")
    md.append("### Table 4. Intervention scenarios (2030 means)")
    md.append("")
    md.append(md_table(interv.round(4), max_rows=30))
    md.append("")
    md.append("### Table 5. Intervention deltas vs baseline (2030)")
    md.append("")
    md.append(md_table(deltas.round(4), max_rows=30))
    md.append("")
    md.append("### Figure 7. Intervention deltas — offload delay (2030)")
    md.append("")
    md.append(f"![Intervention offload delta]({plots/'intervention_delta_offload.png'})")
    md.append("")
    md.append("*Caption:* Negative values indicate reduced offload delay relative to baseline. Governance integration and discharge throughput reforms typically reduce occupancy pressure, which reduces offload delay in the model.")
    md.append("")
    md.append("## 5. Synthesis and implications for RACMA positioning")
    md.append("")
    md.append(
        dedent(
            """
            Across regimes, the model repeatedly expresses the same governance thesis: **split incentives** can dominate the marginal effect of funding share changes when upstream levers (primary care, aged care, disability supports) are not aligned with state-funded acute operational risk.

            The equilibrium structure makes this legible. Under high pressure and a large efficiency gap, adversarial cost-shifting strategies can become individually rational even when system outcomes worsen. This supports an advocacy posture that treats a nominal ‘45%’ as necessary but insufficient: it can be framed as a **platform for structural alignment**, not a substitute for it.

            Practical translation for RACMA is to argue for levers that change the state variables that create high-pressure regimes: (i) pooled funding pilots and governance integration that reduce fragmentation and cost shifting; (ii) valuation realism (indexation consistent with workforce cost growth); and (iii) discharge/placement throughput reforms that directly reduce access/exit block.
            """
        ).strip()
    )
    md.append("")
    md.append("## 6. Limitations and next steps")
    md.append("")
    md.append(
        dedent(
            """
            This is a stylised mechanism model, not an econometric or operations-research forecast. It compresses multiple system processes into a small set of interpretable latent indices and simple functional relationships. Its value is explanatory: clarifying incentives, equilibria, and regime shifts.

            Next steps include incorporating more explicit time-varying valuation drift (NEP vs input-cost divergence), exploring alternative equilibrium selection rules and behavioural assumptions, and tightening calibration around a limited set of measurable outcomes (offload delay distributions; discharge delay distributions; occupancy) while preserving communicability to policy audiences.
            """
        ).strip()
    )
    md.append("")

    md_text = "\n".join(md)
    md_path = repdir / "v17_report_20251221.md"
    md_path.write_text(md_text, encoding="utf-8")

    # HTML render (self-contained)
    html_path = repdir / "v17_report_20251221.html"
    import subprocess

    subprocess.run(
        ["bash", "-lc", f"pandoc {md_path} -o {html_path} --self-contained --resource-path=.:reports:outputs"],
        check=False,
    )


if __name__ == "__main__":
    main()
