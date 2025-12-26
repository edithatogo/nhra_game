from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))


from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

OUTCOMES = [
    "pressure_mean",
    "offload_mean",
    "within4_mean",
    "effgap_mean",
    "discharge_mean",
    "rr_mean",
]


def main() -> None:
    out = Path("outputs/v19")
    tables = out / "tables"
    plots = out / "plots"
    plots.mkdir(parents=True, exist_ok=True)

    traj = pd.read_csv(tables / "trajectory.csv")
    freq = pd.read_csv(tables / "strategy_frequency.csv")

    # Pivot strategies to columns like DEF_R, SHIFT_I etc using yearly shares
    piv = (
        freq.assign(col=freq["game"] + "_" + freq["strategy"])
        .pivot_table(index="year", columns="col", values="share", aggfunc="mean")
        .reset_index()
    )
    df = traj.merge(piv, on="year", how="left").fillna(0.0)

    cols = [c for c in df.columns if c in OUTCOMES or "_" in c and c not in ("rollout",)]
    # Focus: outcomes + strategies
    corr = df[cols].corr(numeric_only=True)

    # Save correlations
    corr.to_csv(tables / "network_correlation_matrix.csv")

    # Plot heatmap
    plt.figure(figsize=(12, 10))
    plt.imshow(corr.values, aspect="auto")
    plt.title("Network effect proxy: correlation among strategies and system outcomes")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90, fontsize=7)
    plt.yticks(range(len(corr.index)), corr.index, fontsize=7)
    plt.colorbar(label="Pearson r")
    plt.tight_layout()
    plt.savefig(plots / "network_effect_correlation_heatmap.png", dpi=240)
    plt.close()

    # Edge list for strong associations
    edges = []
    for i, a in enumerate(corr.columns):
        for j, b in enumerate(corr.columns):
            if j <= i:
                continue
            r = float(corr.iloc[i, j])
            if abs(r) >= 0.35:
                edges.append({"a": a, "b": b, "r": r})
    pd.DataFrame(edges).sort_values("r", key=lambda s: s.abs(), ascending=False).to_csv(
        tables / "network_edges_strong_corr.csv", index=False
    )


if __name__ == "__main__":
    main()
