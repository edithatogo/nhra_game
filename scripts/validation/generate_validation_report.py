"""Generates a summary validation report from backtest results."""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from nhra_gt.domain.validation import RecursiveResult, aggregate_metrics

MEAN_RMSE_LIMIT = 0.15


def main() -> int:
    """Compile and save the final validation Markdown report."""
    results_path = Path("data/calibration/recursive_results.json")
    gsa_path = Path("data/gsa/morris_results.csv")
    out_path = Path("reports/validation_report.md")

    if not results_path.exists():
        print(
            "Run the recursive backtest before generating the validation report.", file=sys.stderr
        )
        return 2

    results_data = json.loads(results_path.read_text(encoding="utf-8"))
    if not results_data:
        print("The backtest contains no holdout results.", file=sys.stderr)
        return 2

    res_objs = [RecursiveResult(**r) for r in results_data]
    metrics = aggregate_metrics(res_objs)

    report = []
    report.append("# NHRA Model Technical Validation Report")
    report.append(f"Generated {datetime.now(UTC).isoformat(timespec='seconds')}")
    report.append("\n## 1. Executive Summary")

    # Status Logic
    rmse_avg = sum(m["rmse"] for m in metrics.values()) / len(metrics)
    status = "MET" if rmse_avg < MEAN_RMSE_LIMIT else "CALIBRATION REQUIRED"
    report.append(f"Mean RMSE criterion **{status}**")
    report.append("The rolling holdouts use the default model parameters.")

    report.append("\n## 2. Recursive Backtesting Metrics")
    report.append("| Metric | RMSE | MAPE | Theil U | Hit Rate |")
    report.append("| :--- | :--- | :--- | :--- | :--- |")

    for m, vals in metrics.items():
        report.append(
            f"| {m} | {vals['rmse']:.3f} | {vals['mape'] * 100:.1f}% | {vals['theil_u']:.3f} | {vals['hit_rate']:.3f} |"
        )

    # GSA Section
    if gsa_path.exists():
        gsa_df = pd.read_csv(gsa_path)
        report.append("\n## 3. Mechanism Integrity (Morris GSA)")
        report.append("Top 5 Drivers (mu_star):")
        top5 = gsa_df.sort_values("mu_star", ascending=False).head(5)
        for _, row in top5.iterrows():
            report.append(f"- **{row['index']}**: {row['mu_star']:.3f} (sigma: {row['sigma']:.3f})")

    report.append("\n## 4. Review")
    report.append(
        "Parameter grounding, long-horizon stability and peer review require their own evidence."
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"Generated validation report at {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
