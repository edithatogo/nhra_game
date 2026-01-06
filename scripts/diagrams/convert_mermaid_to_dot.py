"""Converts Mermaid diagrams to Graphviz DOT format."""

import re
from pathlib import Path


def mermaid_to_dot(mmd_text: str, title: str = "Mermaid converted") -> str:
    """Convert Mermaid graph syntax to DOT syntax."""
    labels: dict[str, str] = {}
    edges: list[tuple[str, str, str | None, str]] = []

    INLINE_NODE = re.compile(r'(?P<id>[A-Za-z0-9_]+)\s*\[\s*"(?P<label>[^"]+)"\s*\]')
    EDGE = re.compile(r'(?P<u>\w+)\s*(?:--\s*"(?P<label>[^"]+)"\s*)?-->\s*(?P<v>\w+)')

    for line in mmd_text.splitlines():
        # Match nodes
        m_node = INLINE_NODE.search(line)
        if m_node:
            labels[m_node.group("id")] = m_node.group("label")

        # Match edges
        m_edge = EDGE.search(line)
        if m_edge:
            u, lab, v = m_edge.groups()
            edges.append((u, v, lab, "solid"))

    dot = [f'digraph "{title}" {{']
    dot.append(f'  graph [labelloc="t", label="{title}", fontsize=12];')
    dot.append(
        '  node [shape=box, style="rounded,filled", fillcolor="#F7F7F7", color="#555555", fontname="Inter", fontsize=11];'
    )
    dot.append('  edge [color="#444444", fontname="Inter", fontsize=10];')

    for nid, lab in labels.items():
        dot.append(f'  {nid} [label="{lab}"];')

    for u, v, l, _ in edges:
        if l:
            dot.append(f'  {u} -> {v} [label="{l}"];')
        else:
            dot.append(f"  {u} -> {v};")

    dot.append("}")
    return "\n".join(dot)


def main() -> None:
    """Run CLI for Mermaid to DOT conversion."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    txt = args.input.read_text(encoding="utf-8")
    out = mermaid_to_dot(txt)
    if args.output:
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)


if __name__ == "__main__":
    main()
