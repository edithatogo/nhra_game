from __future__ import annotations

"""
Best-effort Mermaid (.mmd) to Graphviz DOT conversion for common flowchart patterns.

Supports:
- flowchart LR/TD and graph LR/TD
- node definitions: A["Label"], A[Label], A("Label"), A{Label}
- inline node defs within edges: A["Label"] --> B["Label"]
- edges:
    A --> B
    A -.-> B
    A --- B
    A -->|label| B
    A -- label --> B

Limitations:
- subgraphs/clusters and most styling directives are ignored
- very complex Mermaid constructs won't convert perfectly
"""

import re
from pathlib import Path

INLINE_NODE = re.compile(r'(?P<id>[A-Za-z0-9_]+)\s*\[\s*"(?P<label>[^"]+)"\s*\]')
INLINE_NODE2 = re.compile(r"(?P<id>[A-Za-z0-9_]+)\s*\[\s*(?P<label>[^\]]+)\s*\]")
INLINE_NODEP = re.compile(r'(?P<id>[A-Za-z0-9_]+)\s*\(\s*"(?P<label>[^"]+)"\s*\)')
INLINE_NODEB = re.compile(r"(?P<id>[A-Za-z0-9_]+)\s*\{\s*(?P<label>[^\}]+)\s*\}")

EDGE_LBL_PIPE = re.compile(
    r"^(?P<src>[A-Za-z0-9_]+)\s*(?P<op>-->|-\.->|---|==>)\s*\|(?P<label>[^|]+)\|\s*(?P<dst>[A-Za-z0-9_]+)\s*$"
)
EDGE_LBL_MID = re.compile(
    r"^(?P<src>[A-Za-z0-9_]+)\s*--\s*(?P<label>[^-]+?)\s*-->(?P<dst>[A-Za-z0-9_]+)\s*$"
)
EDGE_SIMPLE = re.compile(
    r"^(?P<src>[A-Za-z0-9_]+)\s*(?P<op>-->|-\.->|---|==>)\s*(?P<dst>[A-Za-z0-9_]+)\s*$"
)


def _clean_label(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        s = s[1:-1]
    s = s.replace("<br/>", "\n").replace("<br>", "\n")
    return s


def _safe_id(nid: str) -> str:
    # DOT identifiers: use alnum + underscore; prefix if needed
    nid2 = re.sub(r"[^A-Za-z0-9_]", "_", nid)
    if not nid2:
        nid2 = "N"
    if nid2[0].isdigit():
        nid2 = "N_" + nid2
    return nid2


def mermaid_to_dot(mmd_text: str, title: str = "Mermaid converted") -> str:
    labels: dict[str, str] = {}
    edges: list[tuple[str, str, str | None, str]] = []

    for raw in mmd_text.splitlines():
        line = raw.strip()
        if (
            not line or line.startswith(("%%", "classDef", "class ", "style "))
        ):
            continue
        if line.lower().startswith(("flowchart", "graph", "subgraph", "end")):
            continue
        line = line.split("%%")[0].strip()
        if not line:
            continue

        # harvest inline node definitions, replace with ids
        for rx in (INLINE_NODE, INLINE_NODE2, INLINE_NODEP, INLINE_NODEB):
            for m in list(rx.finditer(line)):
                nid = m.group("id")
                lab = _clean_label(m.group("label"))
                labels[nid] = lab
            line = rx.sub(lambda m: m.group("id"), line)

        # strip class refs
        line = line.split(":::")[0].strip()

        # also support standalone node defs: A["label"]
        if "[" in raw and "]" in raw and "--" not in raw and "->" not in raw:
            # handled above by inline parsing; ignore
            continue

        # parse edges
        m = EDGE_LBL_PIPE.match(line)
        if m:
            edges.append(
                (m.group("src"), m.group("dst"), _clean_label(m.group("label")), m.group("op"))
            )
            continue
        m = EDGE_LBL_MID.match(line)
        if m:
            edges.append((m.group("src"), m.group("dst"), _clean_label(m.group("label")), "-->"))
            continue
        m = EDGE_SIMPLE.match(line)
        if m:
            edges.append((m.group("src"), m.group("dst"), None, m.group("op")))
            continue

    # ensure node labels for all endpoints
    for s, d, _, _ in edges:
        labels.setdefault(s, s)
        labels.setdefault(d, d)

    # map ids
    id_map = {nid: _safe_id(nid) for nid in labels}

    dot: list[str] = []
    dot.append("digraph MermaidConverted {")
    dot.append("  rankdir=LR;")
    dot.append(f'  graph [labelloc="t", label="{title}", fontsize=12];')
    dot.append(
        '  node [shape=box, style="rounded,filled", fillcolor="#F7F7F7", color="#555555", fontname="Inter", fontsize=11];'
    )
    dot.append('  edge [color="#444444", fontname="Inter", fontsize=10];')

    for nid, lab in sorted(labels.items()):
        lab = lab.replace("\n", "\\n")
        dot.append(f'  {id_map[nid]} [label="{lab}"];')

    for s, d, lab, op in edges:
        attrs = []
        if lab:
            attrs.append(f'label="{lab}"')
        if op == "-.->":
            attrs.append('style="dashed"')
        if attrs:
            dot.append(f"  {id_map[s]} -> {id_map[d]} [{', '.join(attrs)}];")
        else:
            dot.append(f"  {id_map[s]} -> {id_map[d]};")

    dot.append("}")
    return "\n".join(dot)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("mmd", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--title", type=str, default=None)
    args = ap.parse_args()

    text = args.mmd.read_text(encoding="utf-8")
    title = args.title or args.mmd.stem
    dot = mermaid_to_dot(text, title=title)
    args.out.write_text(dot, encoding="utf-8")


if __name__ == "__main__":
    main()
