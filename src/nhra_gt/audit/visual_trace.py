"""Trace visualization for audit scripts."""

import re
from typing import TypedDict


class Edge(TypedDict):
    """Represents a directed influence edge between two nodes in a diagram."""

    source: str
    target: str


def extract_visual_trace(content: str) -> list[Edge]:
    """Extract influence edges from Mermaid graph definitions."""
    edges = []
    # Match: A --> B or A -- "label" --> B
    # Simplified regex for Mermaid flowchart syntax
    pattern = r"([A-Za-z0-9_]+)\s*-+>\s*([A-Za-z0-9_]+)"
    matches = re.finditer(pattern, content)
    for m in matches:
        edges.append({"source": m.group(1), "target": m.group(2)})

    # Also check for Graphviz style: "Node A" -> "Node B"
    if not edges:
        # Match: "Node A" -> "Node B" [label="Influence"];
        # or NodeA -> NodeB;
        pattern = r'(?"([^"]+)"|(\w+))\s*-+>\s*(?"([^"]+)"|(\w+))(?:\s*\[[^\]]*label=["\]?(["\']?([^"]+|[^\]]+))["\]?[^\]]*\])?'
        matches = re.finditer(pattern, content)
        for m in matches:
            src = m.group(1) or m.group(2)
            tgt = m.group(3) or m.group(4)
            if src and tgt:
                edges.append({"source": src, "target": tgt})

    return edges
