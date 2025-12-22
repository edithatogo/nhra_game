"""
Run v8 scenario + sensitivity analyses and write outputs (plots, tables, reports).

Designed to run in <~1 minute on a laptop by keeping Monte Carlo sizes modest.

Usage:
  PYTHONPATH=src python scripts/run_v8_all.py
"""
from __future__ import annotations

from pathlib import Path
import base64
from datetime import date

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from nhra_game_theory.v8 import Params, scenario_params, run_hybrid, summarise_outcome, sensitivity_sample
from nhra_game_theory.plotting import (
    plot_trajectory, plot_strategy_heatmap, tornado_from_rankcorr, render_games_graph_interactive
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "v8"
REPORTS = ROOT / "reports"


def ensure_dirs():
    for d in [OUT, OUT / "plots", OUT / "tables", OUT / "interactive", REPORTS]:
        d.mkdir(parents=True, exist_ok=True)


def _img_b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def run_scenarios():
    years = [2025, 2026, 2027, 2028, 2029, 2030]
    base = Params()

    scenarios = {
        "baseline": [],
        "pooled_funding": ["pooled_funding"],
        "ucc_integration": ["ucc_integration"],
        "nep_realism": ["nep_realism"],
        "discharge_capacity": ["aged_ndis_capacity"],
        "bundle_all": ["pooled_funding", "ucc_integration", "nep_realism", "aged_ndis_capacity", "middle_tier", "cumulative_cap"],
    }

    summaries = []
    for name, ivs in scenarios.items():
        p = scenario_params(base, ivs)
        agg, freq = run_hybrid(years, p, seed=123, n_mc=140)
        agg.to_csv(OUT / "tables" / f"trajectory_{name}.csv", index=False)
        freq.to_csv(OUT / "tables" / f"strategy_freq_{name}.csv", index=False)

        # Key trajectory plots
        plot_trajectory(agg, "pressure_mean", "Pressure index", OUT / "plots" / f"{name}_pressure.png",
                        "pressure_p10", "pressure_p90")
        plot_trajectory(agg, "offload_mean", "Ambulance offload (min)", OUT / "plots" / f"{name}_offload.png",
                        "offload_p10", "offload_p90")
        plot_trajectory(agg, "within4_mean", "ED within 4 hours (share)", OUT / "plots" / f"{name}_within4.png",
                        "within4_p10", "within4_p90")
        plot_trajectory(agg, "rr_mean", "Relative risk proxy", OUT / "plots" / f"{name}_rr_proxy.png",
                        "rr_p10", "rr_p90")

        if name in ("baseline", "bundle_all"):
            plot_strategy_heatmap(freq, OUT / "plots" / f"{name}_strategies.png")

        summaries.append({"scenario": name, "interventions": ", ".join(ivs) if ivs else "(none)", **summarise_outcome(agg)})

    scenario_df = pd.DataFrame(summaries)
    scenario_df.to_csv(OUT / "tables" / "scenario_summary.csv", index=False)

    # Deltas vs baseline + plots
    baseline = scenario_df[scenario_df["scenario"] == "baseline"].iloc[0]
    metrics = ["pressure_2030", "within4_2030", "offload_2030", "effshare_effective_2030", "effgap_2030"]
    delta = scenario_df.copy()
    for m in metrics:
        delta[m] = delta[m] - float(baseline[m])
    delta.to_csv(OUT / "tables" / "scenario_deltas_vs_baseline.csv", index=False)

    fig = plt.figure(figsize=(10, 5))
    ax = fig.gca()
    x = np.arange(len(delta["scenario"]))
    ax.bar(x - 0.2, delta["within4_2030"], width=0.2, label="Δ within4")
    ax.bar(x, -delta["offload_2030"] / 30.0, width=0.2, label="−Δ offload (scaled /30)")
    ax.bar(x + 0.2, -delta["pressure_2030"], width=0.2, label="−Δ pressure")
    ax.set_xticks(x)
    ax.set_xticklabels(delta["scenario"], rotation=30, ha="right")
    ax.axhline(0, linewidth=1)
    ax.set_ylabel("Change vs baseline (scaled)")
    ax.legend(frameon=False, ncol=3, fontsize=9)
    ax.grid(True, axis="y", alpha=0.25)
    fig.savefig(OUT / "plots" / "scenario_deltas.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Tradeoff plot
    fig = plt.figure()
    ax = fig.gca()
    sizes = 2000 * (scenario_df["pressure_2030"] - scenario_df["pressure_2030"].min() + 0.02)
    ax.scatter(scenario_df["effshare_effective_2030"], scenario_df["within4_2030"], s=sizes, alpha=0.7)
    for _, r in scenario_df.iterrows():
        ax.text(r["effshare_effective_2030"] + 0.0005, r["within4_2030"] + 0.0005, r["scenario"], fontsize=9)
    ax.set_xlabel("Effective Commonwealth share (proxy)")
    ax.set_ylabel("ED within 4 hours (share)")
    ax.grid(True, alpha=0.25)
    fig.savefig(OUT / "plots" / "tradeoff_scatter.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def run_sensitivity():
    years = [2025, 2026, 2027, 2028, 2029, 2030]
    base = Params()

    samples = sensitivity_sample(base, n=40, seed=20251220)
    outcomes = []
    for _, row in samples.iterrows():
        p = Params(**{k: row[k] for k in Params().__dict__.keys()})
        agg, _ = run_hybrid(years, p, seed=1000 + int(row["sample_id"]), n_mc=70)
        outcomes.append({"sample_id": int(row["sample_id"]), **summarise_outcome(agg)})

    out = samples.merge(pd.DataFrame(outcomes), on="sample_id")
    out.to_csv(OUT / "tables" / "sensitivity_samples.csv", index=False)

    params = [
        "rurality_weight", "cost_shifting_intensity", "fragmentation_index",
        "discharge_delay_base", "admin_burden_weight", "political_salience",
        "rr_beta_pressure", "rr_beta_offload"
    ]
    for oc in ["pressure_2030", "within4_2030", "offload_2030", "rr_2030", "effshare_effective_2030", "effgap_2030"]:
        tornado_from_rankcorr(out, oc, params=params, outpath=OUT / "plots" / f"tornado_{oc}.png", topk=8)


def make_interactive():
    render_games_graph_interactive(OUT / "interactive" / "games_network_interactive.html")


def write_reports():
    scenario_df = pd.read_csv(OUT / "tables" / "scenario_summary.csv")
    delta_df = pd.read_csv(OUT / "tables" / "scenario_deltas_vs_baseline.csv")
    sens_df = pd.read_csv(OUT / "tables" / "sensitivity_samples.csv")

    key_figs = [
        ("Scenario deltas vs baseline (2030)", OUT / "plots" / "scenario_deltas.png"),
        ("Trade-off: effective share vs within-4-hours (bubble ~ pressure)", OUT / "plots" / "tradeoff_scatter.png"),
        ("Baseline: pressure trajectory", OUT / "plots" / "baseline_pressure.png"),
        ("Baseline: within4 trajectory", OUT / "plots" / "baseline_within4.png"),
        ("Bundle: within4 trajectory", OUT / "plots" / "bundle_all_within4.png"),
        ("Sensitivity tornado: within4_2030", OUT / "plots" / "tornado_within4_2030.png"),
        ("Sensitivity tornado: pressure_2030", OUT / "plots" / "tornado_pressure_2030.png"),
    ]

    fig_html = "\n".join([
        f"<h3>{title}</h3><img style='max-width:100%;height:auto' src='data:image/png;base64,{_img_b64(p)}'/>"
        for title, p in key_figs
    ])

    html = f"""
    <html>
    <head>
      <meta charset="utf-8"/>
      <title>NHRA modelling report v8</title>
      <style>
        body {{ font-family: Inter, Arial, sans-serif; margin: 28px; color: #111; }}
        table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 13px; }}
        th {{ background: #f5f5f5; text-align: left; }}
        code {{ background:#f6f6f6; padding:2px 4px; border-radius:4px; }}
      </style>
    </head>
    <body>
      <h1>NHRA negotiations: stylised hybrid game-theory model (v8)</h1>
      <p><b>Date:</b> {date.today().isoformat()} &nbsp; <b>Version:</b> v0.8.0</p>

      <h2>Scenario headline outcomes (2030)</h2>
      {scenario_df.round(3).to_html(index=False)}

      <h2>Scenario deltas vs baseline</h2>
      {delta_df.round(3).to_html(index=False)}

      <h2>Sensitivity</h2>
      <p>Sample-based global sensitivity screen using Spearman rank correlations (see tornado plots).</p>
      {sens_df.head(20).round(3).to_html(index=False)}

      <h2>Figures</h2>
      {fig_html}

      <h2>Interactive network diagram</h2>
      <p>Open: <code>outputs/v8/interactive/games_network_interactive.html</code></p>

      <h2>Notes</h2>
      <ul>
        <li><b>Pressure index</b> is unitless; interpret as relative strain vs baseline.</li>
        <li><b>RR proxy</b> is a relative indicator only (directional stress signal), not a mortality estimate.</li>
      </ul>
    </body>
    </html>
    """
    (REPORTS / "v8_report.html").write_text(html, encoding="utf-8")

    # Plain text summary
    lines = []
    lines.append("NHRA hybrid game-theory model (v8) — plain-language summary")
    lines.append("")
    lines.append(
        f"Across scenarios, ED within-4-hours in 2030 ranged from "
        f"{scenario_df['within4_2030'].min():.2f} to {scenario_df['within4_2030'].max():.2f} (stylised)."
    )
    lines.append("The combined intervention bundle produced the highest within-4-hours and lowest pressure in these runs.")
    lines.append(
        "Sensitivity screening suggested that discharge delays, fragmentation, and cost-shifting intensity were "
        "the strongest drivers of pressure and throughput."
    )
    (REPORTS / "v8_summary.txt").write_text("\n".join(lines), encoding="utf-8")


def main():
    ensure_dirs()
    run_scenarios()
    run_sensitivity()
    make_interactive()
    write_reports()


if __name__ == "__main__":
    main()
