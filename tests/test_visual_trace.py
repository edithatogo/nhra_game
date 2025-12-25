from __future__ import annotations

from pathlib import Path
from src.nhra_game_theory.audit.visual_trace import extract_edges


def test_extract_edges_mermaid() -> None:
    mmd_content = """
graph TD
    A[Node A] -->|Influence| B[Node B]
    B --> C
"""
    edges = extract_edges(mmd_content, "mermaid")
    assert {"source": "A", "target": "B", "label": "Influence"} in edges
    assert {"source": "B", "target": "C", "label": ""} in edges


def test_extract_edges_graphviz() -> None:
    dot_content = """
digraph G {
    "Node A" -> "Node B" [label="Influence"];
    "Node B" -> "Node C";
}
"""
    edges = extract_edges(dot_content, "graphviz")
    assert {"source": "Node A", "target": "Node B", "label": "Influence"} in edges
    assert {"source": "Node B", "target": "Node C", "label": ""} in edges
