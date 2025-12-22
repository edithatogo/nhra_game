from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx


def main() -> None:
    out = Path("outputs/v18")
    tables = out / "tables"
    plots = out / "plots"
    plots.mkdir(parents=True, exist_ok=True)

    traj = pd.read_csv(tables / "trajectory_baseline.csv")
    sens = pd.read_csv(tables / "sensitivity_oneway.csv")
    scen = pd.read_csv(tables / "intervention_scenarios.csv")
    infl = pd.read_csv(tables / "influence_edges.csv")

    # --- Baseline trajectories ---
    def lineplot(ycol: str, title: str, fname: str) -> None:
        fig = plt.figure()
        plt.plot(traj["year"], traj[ycol])
        plt.title(title)
        plt.xlabel("Year")
        plt.ylabel(ycol)
        plt.tight_layout()
        plt.savefig(plots / fname, dpi=220)
        plt.close(fig)

    for ycol, title, fname in [
        ("pressure_mean", "Baseline: system pressure", "baseline_pressure.png"),
        ("offload_mean", "Baseline: ambulance offload time (mean, min)", "baseline_offload.png"),
        ("within4_mean", "Baseline: % ED within 4 hours (mean)", "baseline_within4.png"),
        ("rr_mean", "Baseline: rural risk proxy (mean)", "baseline_rr.png"),
        ("effgap_mean", "Baseline: total efficiency gap (mean)", "baseline_effgap.png"),
    ]:
        if ycol in traj.columns:
            lineplot(ycol, title, fname)

    # Macro series (if present)
    if "nep_mean" in traj.columns and "cost_mean" in traj.columns:
        lineplot("nep_mean", "Baseline: NEP index (mean)", "baseline_nep_index.png")
        lineplot("cost_mean", "Baseline: input-cost index (mean)", "baseline_cost_index.png")

        fig = plt.figure()
        plt.plot(traj["year"], traj["nep_mean"] / traj["cost_mean"])
        plt.title("Baseline: NEP-to-cost index (higher = better alignment)")
        plt.xlabel("Year")
        plt.ylabel("NEP / Cost index")
        plt.tight_layout()
        plt.savefig(plots / "baseline_nep_to_cost.png", dpi=220)
        plt.close(fig)

    if "effgap_micro_mean" in traj.columns and "effgap_macro_mean" in traj.columns:
        fig = plt.figure()
        plt.plot(traj["year"], traj["effgap_macro_mean"], label="Macro gap")
        plt.plot(traj["year"], traj["effgap_micro_mean"], label="Micro gap")
        plt.plot(traj["year"], traj["effgap_mean"], label="Total gap")
        plt.title("Baseline: efficiency gap decomposition (macro vs micro)")
        plt.xlabel("Year")
        plt.ylabel("Gap")
        plt.legend()
        plt.tight_layout()
        plt.savefig(plots / "baseline_effgap_decomposition.png", dpi=220)
        plt.close(fig)

    # --- Sensitivity (one-way) summary bar: effect on end-year offload ---
    piv = sens.pivot_table(index="parameter", columns="level", values="offload_mean_2030")
    if "high" in piv.columns and "low" in piv.columns:
        effect = (piv["high"] - piv["low"]).sort_values()
        fig = plt.figure(figsize=(7.2, 4.2))
        plt.barh(effect.index, effect.values)
        plt.title("One-way sensitivity: effect on offload_mean_2030 (high - low)")
        plt.xlabel("Δ offload minutes (2030)")
        plt.tight_layout()
        plt.savefig(plots / "sensitivity_offload_bar.png", dpi=220)
        plt.close(fig)

    piv = sens.pivot_table(index="parameter", columns="level", values="rr_mean_2030")
    if "high" in piv.columns and "low" in piv.columns:
        effect = (piv["high"] - piv["low"]).sort_values()
        fig = plt.figure(figsize=(7.2, 4.2))
        plt.barh(effect.index, effect.values)
        plt.title("One-way sensitivity: effect on rr_mean_2030 (high - low)")
        plt.xlabel("Δ RR (2030)")
        plt.tight_layout()
        plt.savefig(plots / "sensitivity_rr_bar.png", dpi=220)
        plt.close(fig)

    # --- Intervention deltas ---
    fig = plt.figure(figsize=(8.0, 4.2))
    df = scen.sort_values("delta_offload_2030")
    plt.barh(df["scenario"], df["delta_offload_2030"])
    plt.title("Intervention scenarios: Δ offload_mean_2030 vs baseline")
    plt.xlabel("Δ offload minutes (2030)")
    plt.tight_layout()
    plt.savefig(plots / "scenario_delta_offload.png", dpi=220)
    plt.close(fig)

    fig = plt.figure(figsize=(8.0, 4.2))
    df = scen.sort_values("delta_rr_2030")
    plt.barh(df["scenario"], df["delta_rr_2030"])
    plt.title("Intervention scenarios: Δ rr_mean_2030 vs baseline")
    plt.xlabel("Δ rural risk proxy (2030)")
    plt.tight_layout()
    plt.savefig(plots / "scenario_delta_rr.png", dpi=220)
    plt.close(fig)

    # --- Influence network (parameters -> outcomes) ---
    try:
        G = nx.DiGraph()
        for _, r in infl.iterrows():
            G.add_edge(r["source"], r["target"], weight=float(r["weight"]))
        pos = nx.spring_layout(G, seed=42)
        fig = plt.figure(figsize=(8.0, 5.0))
        nx.draw_networkx_nodes(G, pos, node_size=900)
        nx.draw_networkx_labels(G, pos, font_size=8)
        widths = [max(0.5, abs(G[u][v]["weight"]) / 10.0) for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, width=widths, arrows=True, arrowsize=12)
        plt.title("Influence network: one-way sensitivity edges")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(plots / "influence_network.png", dpi=220)
        plt.close(fig)
    except Exception:
        pass


if __name__ == "__main__":
    main()
