from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))


from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    post_path = Path("data/calibration_v21/calibration_trials_posterior.csv")
    out_dir = Path("data/calibration_v21/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if not post_path.exists():
        print(f"Error: {post_path} not found.")
        return
        
    df = pd.read_csv(post_path)
    
    # Filter for completed trials
    df = df[df["state"] == "COMPLETE"]
    
    # Identify parameter columns
    param_cols = [c for c in df.columns if c.startswith("params_")]
    
    # Calculate importance (correlation with 'value')
    # Higher absolute correlation implies higher sensitivity
    importances = []
    for col in param_cols:
        corr = df[col].corr(df["value"])
        importances.append({
            "parameter": col.replace("params_", ""),
            "correlation_with_error": corr,
            "abs_importance": abs(corr) if not np.isnan(corr) else 0.0
        })
        
    imp_df = pd.DataFrame(importances).sort_values("abs_importance", ascending=False)
    
    # Save report
    imp_df.to_csv(out_dir / "parameter_importance.csv", index=False)
    
    # Generate Markdown Summary
    report_md = "# Parameter Sensitivity Report (Calibration v21)\n\n"
    report_md += "This report ranks parameters by their absolute correlation with the calibration error.\n\n"
    report_md += imp_df.to_markdown(index=False)
    
    (out_dir / "sensitivity_summary.md").write_text(report_md)
    print(f"Report generated: {out_dir / 'sensitivity_summary.md'}")

if __name__ == "__main__":
    main()
