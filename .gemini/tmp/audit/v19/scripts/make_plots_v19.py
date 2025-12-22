from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _ensure(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    tables = repo / "outputs" / "v19" / "tables"
    plots = repo / "outputs" / "v19" / "plots"
    _ensure(plots)

    traj = pd.read_csv(tables / "trajectory_baseline.csv")
    scen = pd.read_csv(tables / "scenario_endpoints.csv")
    nep = pd.read_csv(tables / "nep_cost_series.csv")
    eq_grid = pd.read_csv(tables / "equilibria_grid.csv")
    scen_ts = pd.read_csv(tables / "scenario_timeseries.csv")

    # --- Baseline time series (pressure / risk proxy / ED performance) ---
    plt.figure()
    plt.plot(traj["year"], traj["pressure_mean"])
    plt.xlabel("Year")
    plt.ylabel("Pressure (index)")
    plt.title("Baseline: system pressure over time (mean)")
    plt.tight_layout()
    plt.savefig(plots / "baseline_pressure.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(traj["year"], traj["rr_mean"])
    plt.xlabel("Year")
    plt.ylabel("Relative risk (index)")
    plt.title("Baseline: clinical risk proxy over time (mean)")
    plt.tight_layout()
    plt.savefig(plots / "baseline_rr.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(traj["year"], traj["within4_mean"])
    plt.xlabel("Year")
    plt.ylabel("ED within 4h (proportion)")
    plt.title("Baseline: ED throughput (within 4h, mean)")
    plt.tight_layout()
    plt.savefig(plots / "baseline_within4.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(traj["year"], traj["offload_mean"])
    plt.xlabel("Year")
    plt.ylabel("Ambulance offload delay (minutes)")
    plt.title("Baseline: ambulance offload delay (mean)")
    plt.tight_layout()
    plt.savefig(plots / "baseline_offload.png", dpi=300)
    plt.close()

    # --- Macro drift: NEP vs input costs ---
    plt.figure()
    plt.plot(nep["year"], nep["nep_per_nwau"], label="NEP (index)")
    plt.plot(nep["year"], nep["input_cost_index"], label="Input costs (index)")
    plt.xlabel("Year")
    plt.ylabel("Index (2025=1.0)")
    plt.title("Macro drift: NEP vs input costs over time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots / "macro_nep_vs_cost.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(nep["year"], nep["nep_to_cost_index"])
    plt.xlabel("Year")
    plt.ylabel("NEP / cost index")
    plt.title("Macro drift: NEP-to-cost ratio over time")
    plt.tight_layout()
    plt.savefig(plots / "macro_nep_to_cost_ratio.png", dpi=300)
    plt.close()

    # --- Scenario endpoints bar (risk proxy) ---
    plt.figure()
    plt.bar(scen["scenario"], scen["rr_mean_2030"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Relative risk (2030)")
    plt.title("Scenario comparison: 2030 risk proxy")
    plt.tight_layout()
    plt.savefig(plots / "scenario_rr_2030.png", dpi=300)
    plt.close()

    # --- Equilibria grid heatmap (count) per game ---
    # For compactness: output one plot per game
    for g in sorted(eq_grid["game"].unique()):
        d = eq_grid[eq_grid["game"] == g].pivot(index="pressure", columns="effgap", values="n_equilibria")
        plt.figure()
        plt.imshow(d.values, aspect="auto")
        plt.xticks(range(len(d.columns)), [str(c) for c in d.columns])
        plt.yticks(range(len(d.index)), [str(i) for i in d.index])
        plt.xlabel("Efficiency gap (index)")
        plt.ylabel("Pressure (index)")
        plt.title(f"Equilibria count grid: {g}")
        plt.colorbar(label="Number of Nash equilibria")
        plt.tight_layout()
        plt.savefig(plots / f"equilibria_grid_{g}.png", dpi=300)
        plt.close()

    # --- Scenario time series overlay (pressure) for key packages ---
    key = scen_ts[scen_ts["scenario"].isin(["baseline", "integration_package", "macro_alignment_package", "full_package"])].copy()
    plt.figure()
    for name, gdf in key.groupby("scenario"):
        plt.plot(gdf["year"], gdf["pressure_mean"], label=name)
    plt.xlabel("Year")
    plt.ylabel("Pressure (index)")
    plt.title("Scenario trajectories: pressure over time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots / "scenario_pressure_timeseries.png", dpi=300)
    plt.close()

    plt.figure()
    for name, gdf in key.groupby("scenario"):
        plt.plot(gdf["year"], gdf["rr_mean"], label=name)
    plt.xlabel("Year")
    plt.ylabel("Relative risk (index)")
    plt.title("Scenario trajectories: risk proxy over time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots / "scenario_rr_timeseries.png", dpi=300)
    plt.close()

    print(f"Wrote plots to: {plots}")


if __name__ == "__main__":
    main()
