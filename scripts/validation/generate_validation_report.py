from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from nhra_gt.domain.validation import RecursiveResult, aggregate_metrics


def main():
    results_path = Path("data/calibration/recursive_results.json")
    gsa_path = Path("data/gsa/morris_results.csv")
    out_path = Path("reports/validation_report.md")

    if not results_path.exists():
        print("Error: Backtest results not found.")
        return

    with open(results_path) as f:
        results_data = json.load(f)

    res_objs = [RecursiveResult(**r) for r in results_data]
    metrics = aggregate_metrics(res_objs)

    report = []
    report.append("# NHRA Model Technical Validation Report")
    report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n## 1. Executive Summary")

    # Simple pass/fail logic for summary
    avg_rmse = sum(m["rmse"] for m in metrics.values()) / len(metrics)
    status = "STABLE" if avg_rmse < 0.15 else "CAUTION"
    report.append(f"Model Status: **{status}**")

    report.append("\n## 2. Recursive Backtesting Metrics (2011–2024)")
    report.append("| Metric | RMSE | MAPE | Theil U | Hit Rate |")
    report.append("| :--- | :--- | :--- | :--- | :--- |")
    for m, vals in metrics.items():
        report.append(
            f"| {m} | {vals['rmse']:.3f} | {vals['mape'] * 100:.1f}% | {vals['theil_u']:.3f} | {vals['hit_rate']:.3f} |"
        )

    report.append("\n## 3. Error Decomposition (Theil)")
    report.append("![Theil Decomposition](../outputs/validation/theil_decomposition.png)")

    report.append("\n## 4. Mechanism Integrity (GSA)")
    if gsa_path.exists():
        df_gsa = pd.read_csv(gsa_path)
        if "Unnamed: 0" in df_gsa.columns:
            df_gsa = df_gsa.rename(columns={"Unnamed: 0": "parameter"})

        # Determine rank
        df_gsa["rank"] = df_gsa["mu_star"].rank(ascending=False)
        top_driver = df_gsa.loc[df_gsa["rank"] == 1, "parameter"].values[0]

        report.append(f"Top mechanistic driver (mu_star): **{top_driver}**")

        report.append("\n| Parameter | mu_star | Rank |")
        report.append("| :--- | :--- | :--- |")
        for _, row in df_gsa.sort_values("rank").iterrows():
            report.append(f"| {row['parameter']} | {row['mu_star']:.4f} | {int(row['rank'])} |")
    else:
        report.append("GSA results not found.")

    report.append("\n## 5. Compliance Notes")
    report.append("- [x] STRESS Guidelines: Model structure and equations documented.")
    report.append("- [x] CHEERS Checklist: Economic parameters sourced from AIHW/ABS.")
    report.append("- [ ] Peer Review: Pending.")

    with open(out_path, "w") as f:
        f.write("\n".join(report))

    print(f"Generated validation report at {out_path}")


if __name__ == "__main__":
    main()
