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

    # Build scenario-year → node metric dict
    # This is a *diagram overlay*: we map outcomes to relevant nodes for colouring.
    series = {}

    # 1. Load Summary & Intervention Endpoints (for scenarios without full trajectories)
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

            # Endpoints are 2030 values. We project these flatly across 2025-2031
            # for scenarios where we lack full trajectory data.
            p_val = float(r.get("pressure_mean_2030", 0.0))
            r_val = float(r.get("rr_mean_2030", 0.0))
            w_val = float(r.get("within4_mean_2030", 0.0))
            o_val = float(r.get("offload_mean_2030", 0.0))
            e_val = 1.0 - float(r.get("effgap_mean_2030", 0.0))

            metrics = {
                "pressure": p_val,
                "risk": r_val,
                "within4": w_val,
                "offload": o_val,
                "effshare": e_val,
            }

            for y in range(2025, 2031):
                series[sc].setdefault(y, {})
                for state_node in ["PRESS", "RISK", "ED", "OFF", "EFF"]:
                    series[sc][y][state_node] = metrics
                # Default others
                for nid in node_ids:
                    if nid not in ["PRESS", "RISK", "ED", "OFF", "EFF"]:
                        series[sc][y].setdefault(nid, metrics)

    # 2. Load Full Trajectory for Baseline (to enable dynamic year slider)
    traj_csv = base_dir / "trajectory.csv"
    if traj_csv.exists():
        df_traj = pd.read_csv(traj_csv)
        # The CSV likely has columns: year, pressure_mean, rr_mean, etc.
        # "baseline_equilibria" is the key used in summary, let's overlap/update it.
        sc_base = "baseline_equilibria"
        series.setdefault(sc_base, {})

        for _, r in df_traj.iterrows():
            y = int(r["year"])
            if 2025 <= y <= 2030:
                series[sc_base].setdefault(y, {})

                # Extract dynamic metrics
                p_val = float(r.get("pressure_mean", 0.0))
                r_val = float(r.get("rr_mean", 0.0))
                w_val = float(r.get("within4_mean", 0.0))
                o_val = float(r.get("offload_mean", 0.0))
                # effgap_mean might not be in trajectory? Check output.
                # Output showed: effgap_mean IS in trajectory.csv
                e_val = 1.0 - float(r.get("effgap_mean", 0.0))

                metrics = {
                    "pressure": p_val,
                    "risk": r_val,
                    "within4": w_val,
                    "offload": o_val,
                    "effshare": e_val,
                }

                for state_node in ["PRESS", "RISK", "ED", "OFF", "EFF"]:
                    series[sc_base][y][state_node] = metrics

                for nid in node_ids:
                    if nid not in ["PRESS", "RISK", "ED", "OFF", "EFF"]:
                        series[sc_base][y].setdefault(nid, metrics)

    (out / "scenario_timeseries.json").write_text(json.dumps(series, indent=2), encoding="utf-8")

    # Copy template HTML into outputs folder
    tpl = repo / "scripts" / "interactive" / "games_network_d3_template.html"
    (out / "games_network_d3.html").write_text(tpl.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Wrote D3 assets to: {out}")


if __name__ == "__main__":
    main()
