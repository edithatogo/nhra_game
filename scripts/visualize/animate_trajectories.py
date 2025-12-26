from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from nhra_gt.engine import Params, baseline_state, step, decide_strategies

def animate_pressure(n_mc: int = 50, n_years: int = 10, output_path: str = "outputs/animations/pressure_swarm.gif"):
    """Generates an animated GIF of Monte Carlo pressure trajectories."""
    p = Params()
    years = list(range(2025, 2025 + n_years))
    
    # Pre-simulate all data
    # raw_data[rollout, year_idx]
    raw_data = np.zeros((n_mc, n_years))
    
    rng = np.random.default_rng(42)
    
    for r in range(n_mc):
        s = baseline_state(start_year=years[0], p=p)
        raw_data[r, 0] = s.pressure
        for i in range(1, n_years):
            strategies = decide_strategies(s, p, rng)
            s = step(s, p, strategies, rng)
            raw_data[r, i] = s.pressure
            
    # Setup Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(years[0], years[-1])
    ax.set_ylim(0.7, 1.6)
    ax.set_title("NHRA System Pressure: Monte Carlo Swarm")
    ax.set_xlabel("Year")
    ax.set_ylabel("Pressure Index")
    ax.grid(True, linestyle="--", alpha=0.6)
    
    lines = [ax.plot([], [], color="teal", alpha=0.3, linewidth=1)[0] for _ in range(n_mc)]
    mean_line, = ax.plot([], [], color="red", linewidth=2, label="Mean Pressure")
    ax.legend(loc="upper left")

    def init():
        for line in lines:
            line.set_data([], [])
        mean_line.set_data([], [])
        return lines + [mean_line]

    def update(frame):
        # frame is the year index (0 to n_years-1)
        x = years[:frame+1]
        for r in range(n_mc):
            y = raw_data[r, :frame+1]
            lines[r].set_data(x, y)
            
        mean_y = np.mean(raw_data[:, :frame+1], axis=0)
        mean_line.set_data(x, mean_y)
        
        return lines + [mean_line]

    ani = animation.FuncAnimation(
        fig, update, frames=len(years), init_func=init, blit=True, interval=500
    )
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    try:
        # Requires pillow for gif
        ani.save(output_path, writer='pillow')
        print(f"Animation saved to {output_path}")
    except Exception as e:
        print(f"Failed to save animation: {e}")
        print("Falling back to static plot.")
        plt.savefig(output_path.replace(".gif", ".png"))

if __name__ == "__main__":
    animate_pressure()
