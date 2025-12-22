"""Synchronise Mermaid and Graphviz diagrams.

This is a *best-effort* converter intended for repository hygiene and quick publication workflows.
It supports the common subset used in this repo:
  - Mermaid flowchart edges: A --> B, A --- B, A -.-> B, A ==> B
  - Ignores styling classes/subgraphs; keeps node IDs and labels when present as A["Label"].

It writes:
  - diagrams/graphviz/<name>.dot for every .mmd in diagrams/mermaid and diagrams/mermaid_user
  - diagrams/mermaid_from_graphviz/<name>.mmd for every .dot in diagrams/graphviz
"""
from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MERMAID_DIRS = [ROOT / "diagrams" / "mermaid", ROOT / "diagrams" / "mermaid_user"]
GV_DIR = ROOT / "diagrams" / "graphviz"
MM_FROM_GV_DIR = ROOT / "diagrams" / "mermaid_from_graphviz"


EDGE_PAT = re.compile(r"^\s*([A-Za-z0-9_]+)(\[[^\]]+\]|\([^\)]+\)|\{[^\}]+\}|\[\"[^\"]+\"\])?\s*([-.=]+>)\s*([A-Za-z0-9_]+)(\[[^\]]+\]|\([^\)]+\)|\{[^\}]+\}|\[\"[^\"]+\"\])?\s*$")
NODE_LABEL_PAT = re.compile(r"^([A-Za-z0-9_]+)\s*(?:\[\"?(.*?)\"?\]|\((.*?)\)|\{(.*?)\})$")


def _parse_node(token: str) -> tuple[str, str | None]:
    token = token.strip()
    m = NODE_LABEL_PAT.match(token)
    if not m:
        return token, None
    node_id = m.group(1)
    label = m.group(2) or m.group(3) or m.group(4)
    return node_id, label


def mermaid_to_dot(mmd_text: str, name: str) -> str:
    nodes: dict[str, str] = {}
    edges: list[tuple[str, str, str]] = []

    for raw in mmd_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%") or line.startswith("flowchart") or line.startswith("graph") or line.startswith("subgraph") or line == "end":
            continue
        if ":::" in line:
            line = line.split(":::")[0].strip()
        # edge line?
        if "--" in line and ">" in line:
            # normalise tokens around arrow
            parts = re.split(r"\s+(-+>|-\.->|==>|-+>)\s+", line)
            # fall back: use regex
            m = EDGE_PAT.match(line)
            if not m:
                continue
            left_token = m.group(1) + (m.group(2) or "")
            arrow = m.group(3)
            right_token = m.group(4) + (m.group(5) or "")

            u, ulab = _parse_node(left_token)
            v, vlab = _parse_node(right_token)
            if ulab:
                nodes[u] = ulab
            if vlab:
                nodes[v] = vlab
            edges.append((u, v, arrow))
            continue

        # bare node with label?
        if "[" in line or "(" in line or "{" in line:
            tok = line.split()[0]
            nid, lab = _parse_node(tok)
            if lab:
                nodes[nid] = lab

    def edge_style(arrow: str) -> str:
        if arrow.startswith("=="):
            return "bold"
        if "-.->" in arrow:
            return "dashed"
        return "solid"

    out = []
    out.append(f'digraph "{name}" {{')
    out.append("  rankdir=LR;")
    out.append('  node [shape=box, style="rounded"];')
    for nid, lab in sorted(nodes.items()):
        safe = lab.replace('"', '\"')
        out.append(f'  {nid} [label="{safe}"];')
    for u, v, a in edges:
        style = edge_style(a)
        out.append(f'  {u} -> {v} [style="{style}"];')
    out.append("}")
    return "\n".join(out) + "\n"


DOT_EDGE_PAT = re.compile(r"^\s*([A-Za-z0-9_]+)\s*->\s*([A-Za-z0-9_]+)")


def dot_to_mermaid(dot_text: str, name: str) -> str:
    edges: list[tuple[str, str]] = []
    labels: dict[str, str] = {}
    for raw in dot_text.splitlines():
        line = raw.strip().rstrip(";")
        m = DOT_EDGE_PAT.match(line)
        if m:
            edges.append((m.group(1), m.group(2)))
        if "[label=" in line:
            nid = line.split()[0]
            m2 = re.search(r'label="(.*?)"', line)
            if m2:
                labels[nid] = m2.group(1).replace('\"', '"')
    out = []
    out.append("flowchart LR")
    for nid, lab in labels.items():
        out.append(f'  {nid}["{lab}"]')
    for u, v in edges:
        out.append(f"  {u} --> {v}")
    return "\n".join(out) + "\n"


def main() -> None:
    GV_DIR.mkdir(parents=True, exist_ok=True)
    MM_FROM_GV_DIR.mkdir(parents=True, exist_ok=True)

    # Mermaid -> dot
    for d in MERMAID_DIRS:
        if not d.exists():
            continue
        for mmd in d.glob("*.mmd"):
            name = mmd.stem
            txt = mmd.read_text(encoding="utf-8")
            dot = mermaid_to_dot(txt, name)
            (GV_DIR / f"{name}.dot").write_text(dot, encoding="utf-8")

    # dot -> Mermaid
    for dot in GV_DIR.glob("*.dot"):
        name = dot.stem
        mmd = dot_to_mermaid(dot.read_text(encoding="utf-8"), name)
        (MM_FROM_GV_DIR / f"{name}.mmd").write_text(mmd, encoding="utf-8")


if __name__ == "__main__":
    main()
