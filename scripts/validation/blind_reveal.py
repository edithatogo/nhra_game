from __future__ import annotations

from pathlib import Path

import pandas as pd

from nhra_gt.domain.validation import BlindReveal, aggregate_metrics


def main():
    historical_path = Path("data/calibration/historical_normalized.csv")
    if not historical_path.exists():
        print(f"Error: {historical_path} not found.")
        return

    df = pd.read_csv(historical_path)

    # 2024 is the only future year we have data for in this file
    holdout_years = [2024]

    revealer = BlindReveal(historical_data=df, holdout_years=holdout_years, seed=42)

    print(f"Starting Blind Reveal Test (Holdout: {holdout_years})...")
    print(
        f"Training Data: {len(revealer.train_df)} years ({revealer.train_df['year'].min()}-{revealer.train_df['year'].max()})"
    )

    results = revealer.run_prediction()

    print("\nBlind Reveal Results:")
    print(f"{'Year':<6} | {'Metric':<10} | {'Pred':<6} | {'Actual':<6} | {'Error':<6}")
    print("-" * 45)

    for res in results:
        y = res.test_year
        for metric in ["within4", "occupancy"]:
            p = res.predicted[metric]
            a = res.actual[metric]
            err = p - a
            print(f"{y:<6} | {metric:<10} | {p:.3f} | {a:.3f} | {err:+.3f}")

    # Summary
    summary = aggregate_metrics(results)
    print("\nPerformance Summary:")
    print(f"{'Metric':<10} | {'RMSE':<6} | {'MAPE':<6} | {'Theil U':<8} | {'HitRate':<8}")
    print("-" * 55)
    for m, vals in summary.items():
        print(
            f"{m:<10} | {vals['rmse']:.3f} | {vals['mape']:.3f} | {vals['theil_u']:.3f} | {vals['hit_rate']:.3f}"
        )


if __name__ == "__main__":
    main()
