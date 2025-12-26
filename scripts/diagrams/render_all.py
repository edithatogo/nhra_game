from __future__ import annotations

"""
Render and cross-convert diagrams.

- For each Mermaid file in diagrams/mermaid_user and diagrams/mermaid_generated:
  - create a DOT counterpart in diagrams/graphviz_from_mermaid
  - render DOT to PNG and SVG into outputs/v9/diagrams

- For each DOT file in diagrams/graphviz_sources:
  - create a Mermaid counterpart in diagrams/mermaid_from_graphviz
  - render DOT to PNG and SVG into outputs/v9/diagrams

This is best-effort: complex Mermaid features may not convert perfectly.
"""

import subprocess
from pathlib import Path

from convert_dot_to_mermaid import dot_to_mermaid
from convert_mermaid_to_dot import mermaid_to_dot


def render_dot(dot_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{dot_path.stem}.png"
    svg = out_dir / f"{dot_path.stem}.svg"
    subprocess.run(["bash", "-lc", f"dot -Tpng '{dot_path}' -o '{png}'"], check=True)
    subprocess.run(["bash", "-lc", f"dot -Tsvg '{dot_path}' -o '{svg}'"], check=True)


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    diagrams = repo / "diagrams"
    out_dir = repo / "outputs" / "diagrams"
    out_dir.mkdir(parents=True, exist_ok=True)

    m_user_dirs = [diagrams / "mermaid_user", diagrams / "mermaid_user_improved"]
    m_gen = diagrams / "mermaid_generated"
    g_from_m = diagrams / "graphviz_from_mermaid"
    g_sources = diagrams / "graphviz_sources"
    m_from_g = diagrams / "mermaid_from_graphviz"

    for d in (m_user_dirs[0], m_user_dirs[1], m_gen, g_from_m, g_sources, m_from_g):
        d.mkdir(parents=True, exist_ok=True)

    # Mermaid -> DOT
    for m_user in m_user_dirs:
        for mmd in m_user.glob("*.mmd"):
            dot_text = mermaid_to_dot(mmd.read_text(encoding="utf-8"), title=mmd.stem)
            dot_path = g_from_m / f"{mmd.stem}.dot"
            dot_path.write_text(dot_text, encoding="utf-8")
            render_dot(dot_path, out_dir)
    for mmd in m_gen.glob("*.mmd"):
        dot_text = mermaid_to_dot(mmd.read_text(encoding="utf-8"), title=mmd.stem)
        dot_path = g_from_m / f"{mmd.stem}.dot"
        dot_path.write_text(dot_text, encoding="utf-8")
        render_dot(dot_path, out_dir)
    # DOT -> Mermaid
    for dot in g_sources.glob("*.dot"):
        mmd_text = dot_to_mermaid(dot.read_text(encoding="utf-8"), direction="LR")
        mmd_path = m_from_g / f"{dot.stem}.mmd"
        mmd_path.write_text(mmd_text, encoding="utf-8")
        render_dot(dot, out_dir)

    print(f"Rendered diagrams to {out_dir}")


if __name__ == "__main__":
    main()
