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
                audit_pressure=0.5,
                cost_shifting_intensity=float(csi)
            )
            
            # We need to manually inject csi if we want to test "what-if" scenarios before modifying the code,
            # but for this audit we just want to show the current behavior.
            
            game = cost_shifting_game(gp)
            
            if np.isclose(csi, 1.0) and np.isclose(pr, 1.15): # Mid-range pressure
                print(f"\n--- DEBUG: csi={csi:.2f}, pr={pr:.2f} ---")
                print("Row Payoffs:\n", game.u_row)
                print("Col Payoffs:\n", game.u_col)
                eqs = all_nash(game)
                print(f"Found {len(eqs)} Nash Equilibria.")
                sel = select_equilibrium(eqs, rule="payoff_dominant", u_row=game.u_row, u_col=game.u_col)
                print(f"Selected Row Strategy: {sel.row}")
            
            eqs = all_nash(game)
            # Use payoff dominant selection
            sel = select_equilibrium(eqs, rule="payoff_dominant", u_row=game.u_row, u_col=game.u_col)
            
            # Get strategy index (0=I, 1=S)
            row_idx = int(np.argmax(sel.row))
            col_idx = int(np.argmax(sel.col))
            
            row_strat = game.row_actions[row_idx]
            col_strat = game.col_actions[col_idx]
            
            # Effective strategy: S if anyone shifts
            effective_strat = "S" if (row_strat == "S" or col_strat == "S") else "I"
            
            results.append({
                "cost_shifting_intensity": csi,
                "pressure": pr,
                "efficiency_gap": 0.20,
                "row_strategy": row_strat,
                "col_strategy": col_strat,
                "effective_strategy": effective_strat,
                "effective_int": 1 if effective_strat == "S" else 0
            })
            
    df = pd.DataFrame(results)
    out_path = "data/gsa_v21/stability_audit_cost_shifting.csv"
    df.to_csv(out_path, index=False)
    print(f"Stability audit saved to {out_path}")
    
    # Quick summary
    print("\nEffective Strategy distribution:")
    print(df["effective_strategy"].value_counts())
    
    # Check correlation
    correlation = df["cost_shifting_intensity"].corr(df["effective_int"])
    print(f"\nCorrelation between Intensity and Effective Strategy: {correlation:.4f}")

if __name__ == "__main__":
    main()
