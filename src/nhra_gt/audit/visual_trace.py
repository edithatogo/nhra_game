"""
Visual Trace and Dependency Mapping.

Extracts edges and nodes for visualizing data flow and agent interactions.
"""

from __future__ import annotations

import re
from typing import TypedDict


class Edge(TypedDict):
    source: str
    target: str
    label: str


def extract_edges(content: str, format_type: str) -> list[Edge]:
    """Extract strategic edges from Mermaid or Graphviz content."""
    edges: list[Edge] = []

    if format_type == "mermaid":
        # Match: A[Node A] -->|Influence| B[Node B]
        # or A --> B
        pattern = r"(\w+)(?:\[[^\]]*\])?\s*--+>\s*(?:\|([^\|]*)\|)?\s*(\w+)(?:\[[^\]]*\])?"
        matches = re.finditer(pattern, content)
        for m in matches:
            edges.append(
                {
                    "source": m.group(1),
                    "target": m.group(3),
                    "label": m.group(2) if m.group(2) else "",
                }
            )

    elif format_type == "graphviz":
        # Match: "Node A" -> "Node B" [label="Influence"];
        # or NodeA -> NodeB;
        pattern = r'(?:"([^"]+)"|(\w+))\s*-+>\s*(?:"([^"]+)"|(\w+))(?:\s*\[[^\]]*label=["\']?([^"\'\]]+)["\']?[^\]]*\])?'
        matches = re.finditer(pattern, content)
        for m in matches:
            source = m.group(1) or m.group(2)
            target = m.group(3) or m.group(4)
            label = m.group(5) if m.group(5) else ""
            edges.append({"source": source, "target": target, "label": label})

    return edges
