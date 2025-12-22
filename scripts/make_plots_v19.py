from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    out = Path("outputs/v19")
    tables = out / "tables"
    plots = out / "plots"
    plots.mkdir(parents=True, exist_ok=True)

    traj = pd.read_csv(tables / "trajectory.csv")

    # NEP vs input cost index (if present)
    nep_cost_path = tables / "nep_cost_series.csv"
    if nep_cost_path.exists():
        nep_cost = pd.read_csv(nep_cost_path)
        plt.figure()
        plt.plot(nep_cost["year"], nep_cost["nep_per_nwau"], label="NEP ($/NWAU, index)")
        plt.plot(nep_cost["year"], nep_cost["input_cost_per_nwau"], label="Input cost per NWAU (index)")
        plt.title("NEP vs input cost per NWAU (index)")
        plt.xlabel("Year")
        plt.ylabel("Index")
        plt.legend()
        plt.tight_layout()
        plt.savefig(plots / "nep_vs_input_cost_index.png", dpi=220)
        plt.close()


    # Baseline trajectories
    for col, fn, title, ylab in [
        ("pressure_mean", "baseline_pressure.png", "Pressure over time (mean)", "Pressure index"),
        ("rr_mean", "baseline_rr_proxy.png", "Risk proxy over time (mean)", "Risk proxy"),
        ("offload_mean", "baseline_offload.png", "Ambulance offload delay (mean)", "Minutes"),
        ("within4_mean", "baseline_within4.png", "ED within-4-hours (mean)", "Proportion"),
        ("effgap_mean", "baseline_effgap.png", "Efficiency gap over time (mean)", "Gap (index)"),
        ("occupancy_mean", "baseline_occupancy.png", "Inpatient occupancy proxy (mean)", "Index"),
            ]:
        plt.figure()
        plt.plot(traj["year"], traj[col])
        plt.title(title)
        plt.xlabel("Year")
        plt.ylabel(ylab)
        plt.tight_layout()
        plt.savefig(plots / fn, dpi=220)
        plt.close()


    # NEP scaffolding plots (NEP is annual $/NWAU index; efficient payment = NEP×representative NWAU)
    nep = pd.read_csv(tables / "nep_series.csv")
    for col, fn, title, ylab in [
        ("nep_per_nwau", "baseline_nep_index.png", "NEP per NWAU (index)", "Index"),
        ("efficient_payment", "baseline_efficient_payment.png", "Efficient payment (NEP×NWAU; index)", "Index"),
    ]:
        plt.figure()
        plt.plot(nep["year"], nep[col])
        plt.title(title)
        plt.xlabel("Year")
        plt.ylabel(ylab)
        plt.tight_layout()
        plt.savefig(plots / fn, dpi=220)
        plt.close()
    
    # Equilibria grid heatmaps
    eq = pd.read_csv(tables / "equilibria_grid.csv")
    for game in eq["game"].unique():
        sub = eq[eq["game"] == game]
        piv = sub.pivot(index="pressure", columns="effgap", values="n_equilibria").sort_index()
        plt.figure()
        plt.imshow(piv.values, aspect="auto", origin="lower")
        plt.title(f"Equilibria count grid — {game}")
        plt.xlabel("Efficiency gap")
        plt.ylabel("Pressure")
        plt.xticks(range(len(piv.columns)), [str(x) for x in piv.columns])
        plt.yticks(range(len(piv.index)), [str(x) for x in piv.index])
        plt.tight_layout()
        plt.savefig(plots / f"equilibria_grid_{game}.png", dpi=220)
        plt.close()

    # Equilibrium multiplicity over time
    eqy = pd.read_csv(tables / "equilibria_by_year.csv")
    eqcount = eqy.groupby(["year", "game"])["n_equilibria_in_game"].max().reset_index()
    for gname in eqcount["game"].unique():
        sub = eqcount[eqcount["game"] == gname]
        plt.figure()
        plt.plot(sub["year"], sub["n_equilibria_in_game"])
        plt.title(f"Equilibrium multiplicity over time — {gname}")
        plt.xlabel("Year")
        plt.ylabel("Number of Nash equilibria")
        plt.tight_layout()
        plt.savefig(plots / f"equilibria_count_over_time_{gname}.png", dpi=220)
        plt.close()

    # Scenario and intervention comparisons
    scen = pd.read_csv(tables / "scenario_summary.csv")
    plt.figure()
    plt.bar(scen["scenario"], scen["rr_mean_2030"])
    plt.xticks(rotation=20, ha="right")
    plt.title("Scenario end-year risk proxy (mean)")
    plt.ylabel("Risk proxy (2030)")
    plt.tight_layout()
    plt.savefig(plots / "scenario_rr_bar.png", dpi=240)
    plt.close()

    deltas = pd.read_csv(tables / "intervention_deltas.csv")
    # Delta plots (directional)
    for col, fn, title, ylab in [
        ("delta_rr_2030", "intervention_delta_rr.png", "Intervention impact on risk proxy (2030 delta vs baseline)", "Δ Risk proxy"),
        ("delta_offload_2030", "intervention_delta_offload.png", "Intervention impact on offload delay (2030 delta vs baseline)", "Δ Offload (min)"),
        ("delta_within4_2030", "intervention_delta_within4.png", "Intervention impact on within-4-hours (2030 delta vs baseline)", "Δ Proportion within-4h"),
        ("delta_effgap_2030", "intervention_delta_effgap.png", "Intervention impact on efficiency gap (2030 delta vs baseline)", "Δ Efficiency gap (index)"),
    ]:
        plt.figure()
        plt.bar(deltas["scenario"], deltas[col])
        plt.xticks(rotation=20, ha="right")
        plt.title(title)
        plt.ylabel(ylab)
        plt.tight_layout()
        plt.savefig(plots / fn, dpi=240)
        plt.close()


if __name__ == "__main__":
    main()