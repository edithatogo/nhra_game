from __future__ import annotations

"""Build a single, shareable context pack for local development.

This concatenates key project documentation and `context/` files into one
document so you can paste/share it with other tools (or colleagues)
without losing structure.

Usage:
    python scripts/build_context_pack.py

Outputs:
    context/CONTEXT_PACK.md
"""

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTX = ROOT / "context"

ORDER = [
    # Kiro-style project docs
    "requirements.md",
    "design.md",
    "tasks.md",
    # Core context
    "00_project_intent.md",
    "01_policy_questions.md",
    "03_model_overview.md",
    "04_parameter_registry.csv",
    "05_evidence_provenance.md",
    "08_glossary_abbreviations.md",
]


def read_any(path: Path) -> str:
    if path.suffix.lower() == ".csv":
        # render small CSV as markdown table-ish
        text = path.read_text(encoding="utf-8").strip()
        return "```csv\n" + text + "\n```\n"
    return path.read_text(encoding="utf-8").strip() + "\n"


def main() -> None:
    out = CTX / "CONTEXT_PACK.md"
    parts: list[str] = []
    parts.append(f"# Context Pack — NHRA game-theory repo (built {date.today().isoformat()})\n")
    missing: list[str] = []

    for name in ORDER:
        # Prefer root-level docs; fall back to context/ copies
        p = ROOT / name
        if not p.exists():
            p = CTX / name
        if not p.exists():
            missing.append(name)
            continue
        parts.append("\n---\n")
        parts.append(f"## {name}\n")
        parts.append(read_any(p))

    if missing:
        parts.append("\n---\n## Missing files\n")
        parts.extend([f"- {m}\n" for m in missing])

    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
