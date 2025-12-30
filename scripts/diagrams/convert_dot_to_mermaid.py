from __future__ import annotations

"""
Graphviz DOT to Mermaid (.mmd) best-effort conversion.

Supported:
- node [label="..."]
- edges like: A -> B [label="..."]

Limitations:
- clusters/subgraphs are ignored
- styling is ignored
"""

import re
from pathlib import Path

NODE_LABEL = re.compile(r'^\s*(?P<id>[A-Za-z0-9_]+)\s*\[.*label="(?P<label>[^"]*)".*\];\s*$')
EDGE = re.compile(
    r"^\s*(?P<src>[A-Za-z0-9_]+)\s*->\s*(?P<dst>[A-Za-z0-9_]+)\s*(?:\[(?P<attrs>[^\]]+)\])?;\s*$"
)
ATTR_LABEL = re.compile(r'label="([^"]*)"')


def dot_to_mermaid(dot_text: str, direction: str = "LR") -> str:
    labels: dict[str, str] = {}
    edges: list[tuple[str, str, str | None]] = []

    for raw in dot_text.splitlines():
        line = raw.strip()
        if (
            not line
            or line.startswith("//")
            or line.startswith("digraph")
            or line.startswith("graph")
            or line.startswith("node")
            or line.startswith("edge")
            or line in ("{", "}")
        ):
            continue
        m = NODE_LABEL.match(line)
        if m:
            labels[m.group("id")] = m.group("label").replace("\\n", "\n")
            continue
        m = EDGE.match(line)
        if m:
            lab = None
            attrs = m.group("attrs") or ""
            ml = ATTR_LABEL.search(attrs)
            if ml:
                lab = ml.group(1)
            edges.append((m.group("src"), m.group("dst"), lab))

    for s, d, _ in edges:
        labels.setdefault(s, s)
        labels.setdefault(d, d)

    out = []
    out.append(
        '%%{init: {"theme":"base","flowchart":{"curve":"basis","nodeSpacing":55,"rankSpacing":75},"themeVariables":{"fontFamily":"Inter, Arial, sans-serif","fontSize":"14px","lineColor":"#444444"}}}%%'
    )
    out.append(f"flowchart {direction}")
    for nid, lab in sorted(labels.items()):
        lab = lab.replace('"', '"')
        lab = lab.replace("\n", "<br/>")
        out.append(f'  {nid}["{lab}"]')
    out.append("")
    for s, d, lab in edges:
        if lab:
            out.append(f"  {s} -->|{lab}| {d}")
        else:
            out.append(f"  {s} --> {d}")
    return "\n".join(out)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("dot", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--dir", type=str, default="LR")
    args = ap.parse_args()

    text = args.dot.read_text(encoding="utf-8")
    mmd = dot_to_mermaid(text, direction=args.dir)
    args.out.write_text(mmd, encoding="utf-8")


if __name__ == "__main__":
    main()
