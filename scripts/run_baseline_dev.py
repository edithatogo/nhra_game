from __future__ import annotations

from pathlib import Path

import polars as pl

from nhra_gt.engine import Params, run_hybrid


# Mocking missing functions if needed (based on previous errors)
def nep_series(years, p):
    return pd.DataFrame({"year": years, "nep": [p.nep_per_nwau_start] * len(years)})


def nep_vs_cost_series(years, p):
    return pd.DataFrame({"year": years, "nep": [1.0] * len(years), "cost": [1.0] * len(years)})


import pandas as pd


def scenario_endpoints(
    years: list[int], scenarios: dict[str, Params], seed: int = 123
) -> pl.DataFrame:
    """Run a set of scenarios and return end-year summary metrics."""
    rows: list[dict[str, object]] = []
    for name, pp in scenarios.items():
        # Using very small n_mc for dev
        d_pd, _ = run_hybrid(years=years, p=pp, seed=seed, n_mc=2)
        d = pl.from_pandas(d_pd)
        end = d.tail(1).to_dicts()[0]
        rows.append(
            {
                "scenario": name,
                "rr_mean_2030": float(end["rr_mean"]),
                "pressure_mean_2030": float(end["pressure_mean"]),
                "within4_mean_2030": float(end["within4_mean"]),
                "effgap_mean_2030": float(end["effgap_mean"]),
                "occ_mean_2030": float(end["occupancy_mean"]),
            }
        )
    df = pl.DataFrame(rows).sort("scenario")
    return df


def main() -> None:
    out = Path("data/baseline")
    tables = out / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    years = list(range(2025, 2031))
    base = Params()

    # Baseline (n_mc=5 for dev)
    print("Running baseline...")
    traj_pd, strat_pd = run_hybrid(years=years, p=base, seed=123, n_mc=5)
    traj = pl.from_pandas(traj_pd)

    if not strat_pd.empty:
        strat_pd["year"] = strat_pd["year"].astype(int)
        strat_pd["game"] = strat_pd["game"].astype(str)
        strat_pd["strategy"] = strat_pd["strategy"].astype(str)
        strat_pd["n"] = strat_pd["n"].astype(int)
        strat_pd["share"] = strat_pd["share"].astype(float)

    strat = pl.from_pandas(strat_pd)

    traj.write_csv(tables / "trajectory.csv")
    strat.write_csv(tables / "strategy_frequency.csv")
    print("Baseline complete.")

    # Core scenario set
    scenarios_core = {
        "baseline_equilibria": Params(),
        "adversarial": Params(
            cost_shifting_intensity=1.2,
            fragmentation_index=1.1,
            political_salience=0.7,
        ),
    }
    print("Running scenarios...")
    core = scenario_endpoints(years, scenarios_core, seed=123)
    core.write_csv(tables / "scenario_summary.csv")
    print("Scenarios complete.")


if __name__ == "__main__":
    main()
