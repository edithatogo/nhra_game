from __future__ import annotations

import pandas as pd
from pathlib import Path
from nhra_game_theory.domain.validation import RecursiveBacktest

def main():
    historical_path = Path("data/calibration_v21/historical_normalized.csv")
    if not historical_path.exists():
        print(f"Error: {historical_path} not found. Please run scripts/data/preprocess_historical.py first.")
        return

    df = pd.read_csv(historical_path)
    
    # Configure backtest
    # 5 years training, 1 year testing
    engine = RecursiveBacktest(
        historical_data=df,
        train_window=5,
        test_window=1,
        seed=42
    )
    
    print(f"Starting Recursive Backtest (Rolling Horizon)...")
    results = engine.run_all()
    
    print("\nResults:")
    print(f"{ 'Year':<6} | { 'Metric':<10} | { 'Pred':<6} | { 'Actual':<6} | { 'Error':<6}")
    print("-" * 45)
    
    for res in results:
        y = res.test_year
        for metric in ["within4", "occupancy"]:
            p = res.predicted[metric]
            a = res.actual[metric]
            err = p - a
            print(f"{y:<6} | {metric:<10} | {p:.3f} | {a:.3f} | {err:+.3f}")

if __name__ == "__main__":
    main()

