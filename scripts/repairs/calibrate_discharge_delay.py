from pathlib import Path

import numpy as np
import pandas as pd

from nhra_gt.domain.validation import calculate_rmse
from nhra_gt.engine import Params, run_hybrid


def main():
    # Load base params
    p = Params()
    calib_path = Path("data/calibration/calibration_optuna_best.csv")
    if calib_path.exists():
        df_calib = pd.read_csv(calib_path)
        if not df_calib.empty:
            vals = df_calib.iloc[0].to_dict()
            valid_keys = {k: v for k, v in vals.items() if hasattr(p, k)}
            p = p.replace(**valid_keys)

    # Load historical for truth
    hist_path = Path("data/calibration/historical_normalized.csv")
    df_hist = pd.read_csv(hist_path)
    target_years = df_hist["year"].tolist()
    _actual_w4 = df_hist["within4"].values

    print(f"{'Delay':<6} | {'RMSE':<6} | {'MeanPred':<8}")
    print("-" * 30)

    best_rmse = 999.0
    best_val = -1.0

    for val in [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.0, 1.05]:
        p_test = p.replace(discharge_delay_base=val)
        # Use default seed for stability
        traj, _ = run_hybrid(years=target_years, p=p_test, n_mc=50, seed=42)

        # Extract predictions corresponding to historical rows
        # Assuming traj generates one row per month, we need to aggregate or match
        # But aggregate_metrics usually takes yearly means?
        # run_hybrid returns monthly trajectory.
        # Let's group by year and take mean
        traj_yearly = traj.groupby("year")[["within4_mean"]].mean().reset_index()

        # Merge with actual to align
        merged = pd.merge(df_hist, traj_yearly, on="year", suffixes=("_actual", "_pred"))

        pred = merged["within4_mean"].values
        act = merged["within4"].values

        rmse = calculate_rmse(act, pred)
        print(f"{val:<6.2f} | {rmse:<6.3f} | {np.mean(pred):<8.3f}")

        if rmse < best_rmse:
            best_rmse = rmse
            best_val = val

    print("-" * 30)
    print(f"Best discharge_delay_base: {best_val} (RMSE: {best_rmse:.3f})")

    # Update CSV if improved
    if best_rmse < 0.15:
        print(f"Updating {calib_path}...")
        df_calib["discharge_delay_base"] = best_val
        df_calib.to_csv(calib_path, index=False)
        print("Updated.")
    else:
        print("Best value still > 0.15, not updating automatically.")


if __name__ == "__main__":
    main()
