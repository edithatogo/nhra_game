"""Build a single-file HTML report for v13 outputs.

Usage:
  PYTHONPATH=src python scripts/build_report_v13.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))


from datetime import date
from pathlib import Path

import pandas as pd


def _img(path: str, width: str = "900px") -> str:
    return f'<div style="margin:14px 0"><img src="{path}" style="max-width:{width}; width:100%; border:1px solid #eee; border-radius:10px"/></div>'


def main() -> None:
    root = Path(".")
    out = root / "reports"
    out.mkdir(exist_ok=True, parents=True)

    tables = root / "outputs" / "v12" / "tables"
    plots = root / "outputs" / "v12" / "plots"

    scen = pd.read_csv(tables / "scenario_summary.csv")
    pd.read_csv(tables / "trajectory_derived.csv")

    html = []
    html.append("<!doctype html><html><head><meta charset='utf-8'/>")
    html.append("<meta name='viewport' content='width=device-width, initial-scale=1'/>")
    html.append("<title>NHRA game-theory simulation — v13 report</title>")
    html.append("<style>body{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:980px;margin:24px auto;padding:0 16px;line-height:1.45;color:#111;} h1,h2{line-height:1.15} table{border-collapse:collapse;width:100%;} th,td{border:1px solid #ddd;padding:8px;font-size:14px;} th{background:#fafafa;text-align:left;} .note{background:#f7f7fb;padding:12px 14px;border-radius:12px;border:1px solid #eee;} code{background:#f6f6f6;padding:2px 6px;border-radius:6px;}</style>")
    html.append("</head><body>")
    html.append(f"<h1>NHRA game-theory simulation — v13</h1><p><b>Build date:</b> {date.today().isoformat()}</p>")

    html.append("<div class='note'><b>Interpretation</b>: This is a stylised mechanism model. NEP is treated as an <i>index</i> by default (see <code>Params.nep_per_nwau_start</code>), and is multiplied by a single representative NWAU weight for illustrative cost-stack plots. The model is designed to explore strategic incentives (cost-shifting, definition/coding pressure, discharge delay) rather than replicate ABF accounting.</div>")

    html.append("<h2>Baseline dynamics</h2>")
    for f, title in [
        ("network_externality.png", "Network externality proxy (pressure × exit-block share)"),
        ("actual_cost_index.png", "Actual cost index (representative NWAU)"),
        ("cth_payment_index.png", "Commonwealth payment index (representative NWAU)"),
        ("state_payment_index.png", "State residual payment index (representative NWAU)"),
    ]:
        html.append(f"<h3>{title}</h3>")
        html.append(_img(str((plots / f).as_posix())))

    html.append("<h2>Scenario comparison (end-year)</h2>")
    html.append(scen.to_html(index=False))

    html.append("<h2>What’s in the ZIP</h2>")
    html.append("<ul>")
    html.append("<li><code>outputs/v12</code>: derived tables + plots</li>")
    html.append("<li><code>diagrams/mermaid</code>, <code>diagrams/mermaid_user</code>, <code>diagrams/graphviz</code>: diagram sources + best-effort cross-format mirrors</li>")
    html.append("</ul>")

    html.append("</body></html>")
    out_html = out / "v13_report_20251220.html"
    out_html.write_text("\n".join(html), encoding="utf-8")

    # Also write a markdown version (lightweight, references images by relative path)
    md = []
    md.append("# NHRA game-theory simulation — v13")
    md.append("")
    md.append(f"**Build date:** {date.today().isoformat()}")
    md.append("")
    md.append("> Interpretation: stylised mechanism model. NEP is treated as an index by default and used for illustrative cost-stack plots.")
    md.append("")
    md.append("## Baseline dynamics")
    for f, title in [
        ("network_externality.png", "Network externality proxy (pressure × exit-block share)"),
        ("actual_cost_index.png", "Actual cost index (representative NWAU)"),
        ("cth_payment_index.png", "Commonwealth payment index (representative NWAU)"),
        ("state_payment_index.png", "State residual payment index (representative NWAU)"),
    ]:
        md.append(f"### {title}")
        md.append(f"![{title}](../outputs/v12/plots/{f})")
        md.append("")
    md.append("## Scenario comparison (end-year)")
    md.append(scen.to_markdown(index=False))
    out_md = out / "v13_report_20251220.md"
    out_md.write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    main()
