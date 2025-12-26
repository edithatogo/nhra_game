from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))


from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    out = Path("outputs/v15")
    plots = out / "plots"
    plots.mkdir(parents=True, exist_ok=True)

    traj = pd.read_csv(out / "tables" / "trajectory.csv")

    for col, fn, title, ylab in [
        ("pressure_mean", "baseline_pressure.png", "Pressure over time (mean)", "Pressure index"),
        ("rr_mean", "baseline_rr_proxy.png", "Risk proxy over time (mean)", "Risk proxy"),
        ("offload_mean", "baseline_offload.png", "Ambulance offload delay (mean)", "Minutes"),
        ("within4_mean", "baseline_within4.png", "ED within-4-hours (mean)", "Proportion"),
        ("effgap_mean", "baseline_effgap.png", "Efficiency gap over time (mean)", "Gap (index)"),
    ]:
        plt.figure()
        plt.plot(traj["year"], traj[col])
        plt.title(title)
        plt.xlabel("Year")
        plt.ylabel(ylab)
        plt.tight_layout()
        plt.savefig(plots / fn, dpi=200)
        plt.close()

    eq = pd.read_csv(out / "tables" / "equilibria_grid.csv")
    # Heatmap-like plot: number of equilibria by pressure/effgap per game
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

    eqy = pd.read_csv(out / "tables" / "equilibria_by_year.csv")
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

    scen = pd.read_csv(out / "tables" / "scenario_summary.csv")
    plt.figure()
    plt.bar(scen["scenario"], scen["rr_mean"])
    plt.xticks(rotation=20, ha="right")
    plt.title("Scenario end-year risk proxy (mean)")
    plt.ylabel("Risk proxy")
    plt.tight_layout()
    plt.savefig(plots / "scenario_rr_bar.png", dpi=220)
    plt.close()


if __name__ == "__main__":
    main()
