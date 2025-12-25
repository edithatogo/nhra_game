from __future__ import annotations

from pathlib import Path


def discover_sources() -> dict[str, list[Path]]:
    """Recursively discover zip files and diagram files."""
    root = Path(".")
    zips = sorted(root.rglob("*.zip"))
    # Diagrams can be mermaid (.mmd) or graphviz (.dot)
    diagrams = sorted(list(root.rglob("*.mmd")) + list(root.rglob("*.dot")))

    # Filter out anything in .nox, .gemini, etc.
    ignore_dirs = {
        ".nox",
        ".gemini",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "site",
    }

    def is_ignored(p: Path) -> bool:
        return any(part in ignore_dirs for part in p.parts)

    return {
        "zips": [p for p in zips if not is_ignored(p)],
        "diagrams": [p for p in diagrams if not is_ignored(p)],
    }


if __name__ == "__main__":
    sources = discover_sources()
    print(f"Found {len(sources['zips'])} zip files.")
    for z in sources["zips"]:
        print(f"  - {z}")
    print(f"Found {len(sources['diagrams'])} diagram files.")
    for d in sources["diagrams"]:
        print(f"  - {d}")