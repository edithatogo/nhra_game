"""Extracts influence edges from Mermaid diagrams for trace analysis."""

import json
from pathlib import Path

from nhra_gt.audit.visual_trace import extract_visual_trace


def main() -> None:
    """Trace all visual edges in the diagrams directory."""
    sources = {"diagrams": list(Path("diagrams").rglob("*.mmd"))}
    all_edges = {}

    print(f"Processing {len(sources['diagrams'])} diagram files...")
    for diag_path in sources["diagrams"]:
        print(f"  Tracing {diag_path}...")
        try:
            content = diag_path.read_text(encoding="utf-8")
            edges = extract_visual_trace(content)
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
    main()
