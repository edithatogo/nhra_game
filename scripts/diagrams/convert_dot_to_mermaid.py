"""Converts Graphviz DOT files to Mermaid format."""

import re
from pathlib import Path


def dot_to_mermaid(dot_text: str, direction: str = "LR") -> str:
    """Convert DOT syntax to Mermaid graph syntax."""
    labels: dict[str, str] = {}
    edges: list[tuple[str, str, str | None]] = []

    # Node label mapping
    NODE_LABEL = re.compile(r'^\s*(?P<id>[A-Za-z0-9_]+)\s*\[.*label="(?P<label>[^"]*)".*\];\s*$')
    for line in dot_text.splitlines():
        m = NODE_LABEL.match(line)
        if m:
            labels[m.group("id")] = m.group("label")

    # Edge extraction
    EDGE = re.compile(
        r'^\s*(?P<u1>[A-Za-z0-9_]+)\s*->\s*(?P<v1>[A-Za-z0-9_]+)\s*(?:[.*label="(?P<label>[^"]*)".*])? ;\s*$'
    )
    for line in dot_text.splitlines():
        m = EDGE.match(line)
        if m:
            edges.append((m.group("u1"), m.group("v1"), m.group("label")))

    mmd = [f"graph {direction}"]
    # Add nodes with labels
    for nid, lab in labels.items():
        mmd.append(f'    {nid}["{lab}"]')

    # Add edges
    for u, v, l in edges:
        if l:
            mmd.append(f'    {u} -- "{l}" --> {v}')
        else:
            mmd.append(f"    {u} --> {v}")

    return "\n".join(mmd)


def main() -> None:
    """Run CLI for DOT to Mermaid conversion."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    txt = args.input.read_text(encoding="utf-8")
    out = dot_to_mermaid(txt)
    if args.output:
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)


if __name__ == "__main__":
    main()
