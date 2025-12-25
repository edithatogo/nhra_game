from __future__ import annotations

import json
from pathlib import Path

from scripts.audit.inventory_sources import discover_sources
from src.nhra_game_theory.audit.visual_trace import extract_edges


def trace_all_visuals() -> None:
    """Discover all diagrams and extract strategic edges."""
    sources = discover_sources()
    all_edges = {}

    print(f"Processing {len(sources['diagrams'])} diagram files...")
    for diag_path in sources["diagrams"]:
        print(f"  Tracing {diag_path}...")
        try:
            content = diag_path.read_text(encoding="utf-8")
            fmt = "mermaid" if diag_path.suffix == ".mmd" else "graphviz"
            edges = extract_edges(content, fmt)
            all_edges[str(diag_path)] = edges
        except Exception as e:
            print(f"    Error tracing {diag_path}: {e}")

    output_dir = Path("data/audit")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "visual_edges.json"
    with open(output_file, "w") as f:
        json.dump(all_edges, f, indent=2)
    
    print(f"\nSaved visual edges for {len(all_edges)} diagrams to {output_file}")


if __name__ == "__main__":
    trace_all_visuals()
