from __future__ import annotations

from pathlib import Path

import pandas as pd

from nhra_gt.engine import Params, run_hybrid


def main() -> None:
    # Setup output paths
    out_dir = Path("publications/P2_Modelling_MJA/02_Analysis")
    out_dir.mkdir(parents=True, exist_ok=True)

    years = list(range(2025, 2031))

    # Define "Golden Scenarios"
    scenarios = {
        "baseline": Params(),
        "transparency_surge": Params(audit_pressure=0.8, noise_sd=0.01),
        "audit_blitz": Params(audit_pressure=1.5, admin_burden_weight=1.2),
        "cooperative_governance": Params(cost_shifting_intensity=0.2, fragmentation_index=0.8),
    }

    results = []
    for name, p in scenarios.items():
        print(f"Running scenario: {name}")
        traj, strat = run_hybrid(years=years, p=p, seed=42, n_mc=300)

        # Save raw trajectory
        traj.to_csv(out_dir / f"traj_{name}.csv", index=False)

        # Aggregate endpoint
        end = traj.iloc[-1]
        results.append(
            {
                "scenario": name,
                "pressure": end["pressure_mean"],
                "within4": end["within4_mean"],
                "effective_share": end["cth_effective_mean"],
                "efficiency_gap": end["effgap_mean"],
            }
        )

    summary_df = pd.DataFrame(results)
    summary_df.to_csv(out_dir / "experiment_summary.csv", index=False)
    print(f"Experiments complete. Results saved to {out_dir}")


if __name__ == "__main__":
    main()
