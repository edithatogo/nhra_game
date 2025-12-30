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

    # Build scenario-year → node metric dict from the v8 scenario table if available
    # This is a *diagram overlay*: we map outcomes to relevant nodes for colouring.
    series = {}
    scenario_csv = repo / "outputs" / "v8" / "tables" / "scenario_table.csv"
    if scenario_csv.exists():
        df = pd.read_csv(scenario_csv)
        for _, r in df.iterrows():
            sc = r["scenario"]
            series.setdefault(sc, {})
            for y in range(2025, 2031):
                series[sc].setdefault(y, {})
                series[sc][y] = {
                    "PRESS": {
                        "pressure": float(r.get("pressure_2030", 0.0)),
                        "risk": float(r.get("harm_2030", 0.0)),
                        "within4": float(r.get("within4_2030", 0.0)),
                        "offload": float(r.get("offload_2030", 0.0)),
                        "effshare": float(r.get("effshare_effective_2030", 0.0)),
                    },
                    "RISK": {
                        "pressure": float(r.get("pressure_2030", 0.0)),
                        "risk": float(r.get("harm_2030", 0.0)),
                        "within4": float(r.get("within4_2030", 0.0)),
                        "offload": float(r.get("offload_2030", 0.0)),
                        "effshare": float(r.get("effshare_effective_2030", 0.0)),
                    },
                    "ED": {
                        "pressure": float(r.get("pressure_2030", 0.0)),
                        "risk": float(r.get("harm_2030", 0.0)),
                        "within4": float(r.get("within4_2030", 0.0)),
                        "offload": float(r.get("offload_2030", 0.0)),
                        "effshare": float(r.get("effshare_effective_2030", 0.0)),
                    },
                    "OFF": {
                        "pressure": float(r.get("pressure_2030", 0.0)),
                        "risk": float(r.get("harm_2030", 0.0)),
                        "within4": float(r.get("within4_2030", 0.0)),
                        "offload": float(r.get("offload_2030", 0.0)),
                        "effshare": float(r.get("effshare_effective_2030", 0.0)),
                    },
                    "EFF": {
                        "pressure": float(r.get("pressure_2030", 0.0)),
                        "risk": float(r.get("harm_2030", 0.0)),
                        "within4": float(r.get("within4_2030", 0.0)),
                        "offload": float(r.get("offload_2030", 0.0)),
                        "effshare": float(r.get("effshare_effective_2030", 0.0)),
                    },
                }
                # Default: other nodes inherit pressure values for colour scaling
                for nid in node_ids:
                    series[sc][y].setdefault(nid, series[sc][y]["PRESS"])

    (out / "scenario_timeseries.json").write_text(json.dumps(series, indent=2), encoding="utf-8")

    # Copy template HTML into outputs folder
    tpl = repo / "scripts" / "interactive" / "games_network_d3_template.html"
    (out / "games_network_d3.html").write_text(tpl.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Wrote D3 assets to: {out}")


if __name__ == "__main__":
    main()
