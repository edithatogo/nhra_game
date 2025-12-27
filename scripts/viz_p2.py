import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def main():
    out_dir = Path("publications/P2_Modelling_MJA/03_Manuscript/figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    data_dir = Path("publications/P2_Modelling_MJA/02_Analysis")
    
    # 1. Trajectory Comparison
    scenarios = ["baseline", "transparency_surge", "audit_blitz", "cooperative_governance"]
    plt.figure(figsize=(10, 6))
    
    for scen in scenarios:
        df = pd.read_csv(data_dir / f"traj_{scen}.csv")
        plt.plot(df["year"], df["pressure_mean"], label=scen.replace("_", " ").title(), marker='o')
        
    plt.axhline(1.0, color='red', linestyle='--', alpha=0.5, label="System Limit")
    plt.xlabel("Year")
    plt.ylabel("System Pressure Index")
    plt.title("Figure 1: Projected System Pressure under Alternative NHRA Policies")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(out_dir / "figure1_trajectories.png", dpi=300)
    plt.close()
    
    # 2. Strategic Gaming Breakdown (Baseline)
    # We don't have strategy freq per year in my P2 run yet, I'll use the summary
    summary = pd.read_csv(data_dir / "experiment_summary.csv")
    plt.figure(figsize=(8, 6))
    sns.barplot(data=summary, x="scenario", y="within4")
    plt.xticks(rotation=45)
    plt.ylabel("Proportion within 4h")
    plt.title("Figure 2: Performance Outcome (within 4h) by Policy Scenario")
    plt.tight_layout()
    plt.savefig(out_dir / "figure2_performance.png", dpi=300)
    plt.close()
    
    print(f"Figures generated in {out_dir}")

if __name__ == "__main__":
    main()
