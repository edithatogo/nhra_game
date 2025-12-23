from __future__ import annotations

import pandas as pd
import numpy as np
from nhra_game_theory.subgames.games import GameParams, cost_shifting_game
from nhra_game_theory.subgames.nash import all_nash, select_equilibrium

def main():
    # Grid search
    intensities = np.linspace(0.0, 1.0, 21)
    pressures = np.linspace(0.8, 1.5, 21)
    
    results = []
    
    for csi in intensities:
        for pr in pressures:
            # Note: The current implementation of cost_shifting_game doesn't use csi, 
            # but we pass it to GameParams anyway to check stability if it WERE used later.
            # We also vary efficiency_gap as that IS used.
            
            # Let's test with a fixed efficiency gap first
            gp = GameParams(
                pressure=float(pr),
                efficiency_gap=0.20,
                discharge_delay=1.0,
                political_salience=0.3,
                audit_pressure=0.5
            )
            
            # We need to manually inject csi if we want to test "what-if" scenarios before modifying the code,
            # but for this audit we just want to show the current behavior.
            
            game = cost_shifting_game(gp)
            eqs = all_nash(game)
            # Use payoff dominant selection
            sel = select_equilibrium(eqs, rule="payoff_dominant", u_row=game.u_row, u_col=game.u_col)
            
            # Get strategy index (0=I, 1=S)
            strategy_idx = int(np.argmax(sel.row))
            strategy = game.row_actions[strategy_idx]
            
            results.append({
                "cost_shifting_intensity": csi,
                "pressure": pr,
                "efficiency_gap": 0.20,
                "strategy": strategy,
                "strategy_int": strategy_idx # 0 for Invest, 1 for Shift
            })
            
    df = pd.DataFrame(results)
    out_path = "data/gsa_v21/stability_audit_cost_shifting.csv"
    df.to_csv(out_path, index=False)
    print(f"Stability audit saved to {out_path}")
    
    # Quick summary
    print("\nStrategy distribution:")
    print(df["strategy"].value_counts())
    
    # Check if intensity affects outcome (it shouldn't in current code)
    correlation = df["cost_shifting_intensity"].corr(df["strategy_int"])
    print(f"\nCorrelation between Intensity and Strategy: {correlation:.4f}")

if __name__ == "__main__":
    main()
