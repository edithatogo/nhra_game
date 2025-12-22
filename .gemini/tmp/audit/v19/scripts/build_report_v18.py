from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from datetime import date

import pandas as pd


def md_table(df: pd.DataFrame, max_rows: int = 18) -> str:
    if len(df) > max_rows:
        df = df.head(max_rows)
    return df.to_markdown(index=False)


def main() -> None:
    out = Path("outputs/v18")
    tables = out / "tables"
    plots = out / "plots"

    repdir = Path("reports/generated")
    repdir.mkdir(parents=True, exist_ok=True)

    traj = pd.read_csv(tables / "trajectory_baseline.csv")
    eq = pd.read_csv(tables / "equilibria_all_games.csv")
    sens = pd.read_csv(tables / "sensitivity_oneway.csv")
    scen = pd.read_csv(tables / "intervention_scenarios.csv")
    nep = pd.read_csv(tables / "nep_cost_series.csv")

    # Summaries for reporting
    end_year = int(traj["year"].max())
    end = traj[traj["year"] == end_year].iloc[0]

    md_text = dedent(
        f"""
        # NHRA game-theory simulation (v18) — results report ({date.today().isoformat()})

        This report summarises the outputs from **v18**, which extends the stylised NHRA hybrid model by
        explicitly modelling **NEP ($/NWAU)** and **input-cost indices** over time (macro drift). The model is not a
        forecasting tool; it is intended to clarify **mechanisms** and support structured sensitivity and scenario analysis.

        ## Abbreviations

        * **ABF**: Activity-based funding  
        * **NEP**: National Efficient Price (in $/NWAU)  
        * **NWAU**: National Weighted Activity Unit  
        * **RR proxy**: Stylised “rural risk” indicator used as a safety-relevant outcome  
        * **Efficiency gap**: Difference between NEP-recognised valuation and realised input costs (macro drift) plus a game-driven “micro” component

        ## 1. Baseline dynamics (2025–{end_year})

        The baseline run uses a single parameter set (see `outputs/v18/tables/metadata.json` and `nep_cost_series.csv`),
        with Monte Carlo rollouts to include small stochastic perturbations around an otherwise deterministic backbone.

        By {end_year}, the model’s mean outcomes were:

        * **Pressure**: {end['pressure_mean']:.3f}  
        * **Ambulance offload (min)**: {end['offload_mean']:.1f}  
        * **ED within 4 hours**: {end['within4_mean']:.3f}  
        * **Efficiency gap (total)**: {end['effgap_mean']:.3f}  
        * **RR proxy**: {end['rr_mean']:.3f}

        ### Figure 1. Baseline trajectories (pressure, offload, within-4, RR)

        ![Baseline system pressure](outputs/v18/plots/baseline_pressure.png)

        *Caption:* Mean system pressure over time (higher indicates more downstream stress).

        ![Baseline ambulance offload](outputs/v18/plots/baseline_offload.png)

        *Caption:* Mean ambulance offload minutes; increases reflect access block and ED congestion.

        ![Baseline ED within 4 hours](outputs/v18/plots/baseline_within4.png)

        *Caption:* Mean proportion of ED presentations completed within 4 hours (stylised).

        ![Baseline RR proxy](outputs/v18/plots/baseline_rr.png)

        *Caption:* A stylised safety-relevant indicator that worsens with pressure, delay, and valuation divergence.

        ### Figure 2. Macro valuation drift (NEP vs input costs)

        ![Baseline NEP-to-cost index](outputs/v18/plots/baseline_nep_to_cost.png)

        *Caption:* The ratio of the NEP index to an input-cost index. When costs grow faster than NEP,
        the ratio declines and the macro component of the efficiency gap widens.

        ### Table 1. Illustrative NEP and input-cost series

        {md_table(nep, max_rows=12)}

        *Caption:* NEP is represented as $/NWAU (index units). Payments in ABF are NEP × NWAU; this model
        keeps the weighting implicit and tracks the valuation drift component over time.

        ## 2. Stage-game equilibria (baseline representative state)

        The model includes several “games” (e.g., bargaining, cost-shifting, governance integration). The equilibria below
        are **stage-game** Nash equilibria for a representative baseline state; they are not claims about negotiated outcomes.

        ### Table 2. All Nash equilibria by stage game

        {md_table(eq, max_rows=18)}

        *Caption:* Each profile is a strategy tuple; payoffs are utility numbers within the model.

        ## 3. Sensitivity analysis

        One-way sensitivity varies each parameter up/down (see `sensitivity_oneway.csv`) and records end-year (2030) outcomes.
        This helps identify which assumptions most influence congestion and safety proxies.

        ### Figure 3. One-way sensitivity: offload_mean_2030

        ![Sensitivity offload](outputs/v18/plots/sensitivity_offload_bar.png)

        *Caption:* Change in offload minutes at 2030 when each parameter is moved from “low” to “high”.

        ### Figure 4. One-way sensitivity: RR proxy (2030)

        ![Sensitivity RR](outputs/v18/plots/sensitivity_rr_bar.png)

        *Caption:* Change in the RR proxy at 2030 when each parameter is moved from “low” to “high”.

        ### Table 3. One-way sensitivity (head)

        {md_table(sens.sort_values(['parameter','level']), max_rows=18)}

        *Caption:* Each row contains the parameter, the level, and the resulting end-year outcomes.

        ### Figure 5. Influence network derived from sensitivity edges

        ![Influence network](outputs/v18/plots/influence_network.png)

        *Caption:* A simple directed network showing which parameters most move which outcomes (edge widths scale with effect size).

        ## 4. Intervention scenarios (policy choices)

        Intervention scenarios combine stylised levers (e.g., pooled funding, integration, NEP indexation uplift, input-cost containment).
        The model reports **differences** vs baseline at 2030.

        ### Figure 6. Scenario deltas: offload (2030)

        ![Scenario Δ offload](outputs/v18/plots/scenario_delta_offload.png)

        *Caption:* Change in offload minutes at 2030 vs baseline.

        ### Figure 7. Scenario deltas: RR proxy (2030)

        ![Scenario Δ RR](outputs/v18/plots/scenario_delta_rr.png)

        *Caption:* Change in RR proxy at 2030 vs baseline.

        ### Table 4. Intervention scenario results

        {md_table(scen.sort_values('scenario'), max_rows=20)}

        *Caption:* End-year outcomes and deltas vs baseline.

        ## 5. Synthesis

        Across baseline, sensitivity, and scenario runs, the model consistently shows that **valuation divergence** (NEP vs realised costs),
        **discharge delay**, and **cost-shifting intensity** are strong drivers of downstream congestion. Governance levers that reduce
        fragmentation and improve discharge coordination tend to improve both access metrics (offload, within-4) and the safety proxy,
        especially when paired with macro alignment (indexation uplift and/or cost containment).

        The primary use of these outputs is to support structured policy argumentation: which assumptions matter most, and which
        levers are robustly favourable across plausible ranges.
        """
    ).strip() + "\n"

    md_path = repdir / "v18_report_20251221.md"
    md_path.write_text(md_text, encoding="utf-8")

    # Plain text summary (full sentences)
    txt_summary = dedent(
        f"""
        NHRA simulation v18 summarises a stylised model of intergovernmental bargaining, cost-shifting and operational risk in the Australian health system.
        The model explicitly represents NEP as an annual $/NWAU index and tracks an input-cost index over time. When input costs grow faster than NEP, the
        macro component of the efficiency gap widens, reducing the effective Commonwealth share and increasing downstream pressure.

        In the baseline run from 2025 to {end_year}, average pressure and ambulance offload increased as discharge delays and valuation divergence compounded,
        and the ED within-four-hours metric deteriorated. One-way sensitivity analysis indicated that cost-shifting intensity, discharge delay, and the parameters
        governing NEP-to-cost alignment were among the most influential on congestion and the rural-risk proxy.

        Intervention scenarios suggested that governance and integration measures (pooled funding and formal integration of diversionary services) improved access
        metrics, particularly when combined with macro-alignment levers that either increase NEP indexation growth or reduce input-cost growth. The model is not a
        forecast and does not estimate real-world effect sizes; its value is in clarifying mechanism interactions, identifying influential assumptions, and comparing
        intervention packages under uncertainty.
        """
    ).strip() + "\n"
    (repdir / "v18_plaintext_summary_20251221.txt").write_text(txt_summary, encoding="utf-8")

    # HTML render (self-contained)
    html_path = repdir / "v18_report_20251221.html"
    import subprocess

    subprocess.run(
        ["bash", "-lc", f"pandoc {md_path} -o {html_path} --self-contained --resource-path=.:reports:outputs"],
        check=False,
    )


if __name__ == "__main__":
    main()
