from __future__ import annotations

"""
Generate the JSON inputs for the D3 network and copy the HTML template into outputs/v9/interactive.

This makes the diagram "dynamic" in the sense that:
- the topology is fixed (games + operational states)
- node colouring is driven by scenario-year values exported from the simulation
"""

import json
from pathlib import Path

import pandas as pd


def compute_centrality(nodes: list[str], links: list[dict]) -> dict[str, float]:
    # Simple degree-based centrality normalised to [0,1]
    deg = dict.fromkeys(nodes, 0.0)
    for e in links:
        deg[e["source"]] += e["weight"]
        deg[e["target"]] += e["weight"]
    mx = max(deg.values()) if deg else 1.0
    return {k: (v / mx if mx > 0 else 0.0) for k, v in deg.items()}


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    out = repo / "outputs" / "interactive"
    out.mkdir(parents=True, exist_ok=True)

    # Define a canonical games network (minimal labels)
    nodes = [
        ("BARG", "Bargain", "game"),
        ("DEF", "Define", "game"),
        ("CAP", "Cap", "game"),
        ("SHIFT", "Shift", "game"),
        ("DISC", "Discharge", "game"),
        ("GOV", "Govern", "game"),
        ("SIGNAL", "Signal", "game"),
        ("PRESS", "Pressure", "state"),
        ("OCC", "Occupancy", "state"),
        ("OFF", "Offload", "state"),
        ("ED", "ED≤4h", "state"),
        ("RISK", "Risk", "state"),
        ("EFF", "EffShare", "state"),
    ]
    links = [
        ("SIGNAL", "BARG", 0.55),
        ("BARG", "DEF", 0.55),
        ("BARG", "CAP", 0.50),
        ("BARG", "GOV", 0.50),
        ("DEF", "CAP", 0.45),
        ("CAP", "SHIFT", 0.55),
        ("SHIFT", "PRESS", 0.70),
        ("DISC", "OCC", 0.75),
        ("PRESS", "ED", 0.60),
        ("OCC", "OFF", 0.65),
        ("OFF", "RISK", 0.75),
        ("ED", "RISK", 0.60),
        ("GOV", "ED", 0.45),
        ("SHIFT", "EFF", 0.55),
        ("EFF", "PRESS", 0.40),
    ]

    node_ids = [n[0] for n in nodes]
    link_dicts = [{"source": s, "target": t, "weight": float(w)} for s, t, w in links]
    cent = compute_centrality(node_ids, link_dicts)

    graph = {
        "nodes": [
            {"id": nid, "label": lab, "type": typ, "centrality": cent.get(nid, 0.0)}
            for nid, lab, typ in nodes
        ],
        "links": link_dicts,
    }
    (out / "games_network.json").write_text(json.dumps(graph, indent=2), encoding="utf-8")

    # Build scenario-year → node metric dict from the baseline tables
    # This is a *diagram overlay*: we map outcomes to relevant nodes for colouring.
    series = {}

    # Read both summary and intervention tables
    base_dir = repo / "data" / "baseline" / "tables"
    dfs = []

    summary_csv = base_dir / "scenario_summary.csv"
    if summary_csv.exists():
        dfs.append(pd.read_csv(summary_csv))

    intervention_csv = base_dir / "intervention_scenarios.csv"
    if intervention_csv.exists():
        dfs.append(pd.read_csv(intervention_csv))

    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        for _, r in df.iterrows():
            sc = r["scenario"]
            series.setdefault(sc, {})
            # Data is currently only for 2030 in these summaries, but D3 expects a time series.
            # We will project the 2030 value across the range for now, or just set it for 2030.
            # The original script looped 2025-2031. Let's populate 2030 specifically,
            # and maybe copy it to other years if needed, but the original code read specific year columns.
            # The new data only has _2030 columns. We'll populate 2025-2031 with the 2030 static value
            # to ensure the map shows *something* for any year selected, acting as a "steady state" view.

            # Map columns:
            # pressure_mean_2030 -> pressure
            # rr_mean_2030 -> risk (harm)
            # within4_mean_2030 -> within4
            # offload_mean_2030 -> offload
            # effgap_mean_2030 -> effshare (approximate 1-gap or just gap? Old code used effshare_effective_2030)
            # Let's use 1.0 - effgap as "efficiency share" proxy if gap < 1.

            p_val = float(r.get("pressure_mean_2030", 0.0))
            r_val = float(r.get("rr_mean_2030", 0.0))
            w_val = float(r.get("within4_mean_2030", 0.0))
            o_val = float(r.get("offload_mean_2030", 0.0))
            e_val = 1.0 - float(r.get("effgap_mean_2030", 0.0))  # gap to share proxy

            metrics = {
                "pressure": p_val,
                "risk": r_val,
                "within4": w_val,
                "offload": o_val,
                "effshare": e_val,
            }

            for y in range(2025, 2031):
                series[sc].setdefault(y, {})
                # Apply these metrics to all relevant state nodes
                for state_node in ["PRESS", "RISK", "ED", "OFF", "EFF"]:
                    series[sc][y][state_node] = metrics

                # Default: other nodes inherit pressure values for colour scaling
                for nid in node_ids:
                    if nid not in ["PRESS", "RISK", "ED", "OFF", "EFF"]:
                        series[sc][y].setdefault(nid, series[sc][y]["PRESS"])

    (out / "scenario_timeseries.json").write_text(json.dumps(series, indent=2), encoding="utf-8")

    # Copy template HTML into outputs folder
    tpl = repo / "scripts" / "interactive" / "games_network_d3_template.html"
    (out / "games_network_d3.html").write_text(tpl.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Wrote D3 assets to: {out}")


if __name__ == "__main__":
    main()
