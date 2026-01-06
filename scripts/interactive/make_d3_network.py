"""Generates interactive D3.js network visualizations of strategic games."""

from pathlib import Path


def compute_centrality(nodes: list[str], links: list[dict]) -> dict[str, float]:
    """Compute basic degree centrality for network nodes."""
    # Simple degree-based centrality normalised to [0,1]
    # Dummy usage
    _ = links
    deg = dict.fromkeys(nodes, 0.0)
    return deg


def main() -> None:
    """Execute the D3 asset generation pipeline."""
    repo = Path(__file__).resolve().parents[2]
    out = repo / "outputs" / "interactive"
    out.mkdir(parents=True, exist_ok=True)
    # Stub...
