import pandas as pd
from pathlib import Path
from nhra_gt.visualization.base import PlotConfig, save_figure
from nhra_gt.visualization.trajectories import plot_comparison_trajectory
from nhra_gt.visualization.distributional import plot_comparison_bar

def main():
    out_dir = Path("publications/P2_Modelling_MJA/03_Manuscript/figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    data_dir = Path("publications/P2_Modelling_MJA/02_Analysis")
    config = PlotConfig()
    
    # 1. Trajectory Comparison
    scenarios = ["baseline", "transparency_surge", "audit_blitz", "cooperative_governance"]
    all_traj = []
    for scen in scenarios:
        df = pd.read_csv(data_dir / f"traj_{scen}.csv")
        df["Scenario"] = scen.replace("_", " ").title()
        all_traj.append(df)
    
    combined_traj = pd.concat(all_traj)
    fig1 = plot_comparison_trajectory(
        combined_traj, 
        "pressure_mean", 
        "System Pressure Index", 
        config=config
    )
    # Add system limit line
    fig1.gca().axhline(1.0, color='red', linestyle='--', alpha=0.5, label="System Limit")
    fig1.gca().legend()
    fig1.gca().set_title("Figure 1: Projected System Pressure under Alternative NHRA Policies")
    
    save_figure(fig1, out_dir / "figure1_trajectories.png", config)
    
    # 2. Strategic Gaming Breakdown
    summary = pd.read_csv(data_dir / "experiment_summary.csv")
    fig2 = plot_comparison_bar(
        summary,
        "scenario",
        "within4",
        "Figure 2: Performance Outcome (within 4h) by Policy Scenario",
        "Proportion within 4h",
        config=config
    )
    
    save_figure(fig2, out_dir / "figure2_performance.png", config)
    
    print(f"Figures generated in {out_dir}")

if __name__ == "__main__":
    main()
