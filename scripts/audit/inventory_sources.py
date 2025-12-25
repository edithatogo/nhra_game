from __future__ import annotations

import zipfile
from pathlib import Path
from typing import TypedDict


class IntegrityReport(TypedDict):
    valid_zips: list[Path]
    corrupt_zips: dict[Path, str]


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


def verify_sources_integrity(
    sources: dict[str, list[Path]],
) -> IntegrityReport:
    """Verify integrity of discovered sources."""
    report: IntegrityReport = {
        "valid_zips": [],
        "corrupt_zips": {},
    }

    for z in sources["zips"]:
        if not zipfile.is_zipfile(z):
            report["corrupt_zips"][z] = "File is not a zip file"
            continue

        try:
            with zipfile.ZipFile(z, "r") as zf:
                bad_file = zf.testzip()
                if bad_file:
                    report["corrupt_zips"][z] = f"Corrupt file within zip: {bad_file}"
                else:
                    report["valid_zips"].append(z)
        except Exception as e:
            report["corrupt_zips"][z] = str(e)

    return report


if __name__ == "__main__":
    sources = discover_sources()
    print(f"Found {len(sources['zips'])} zip files.")
    for z in sources["zips"]:
        print(f"  - {z}")
    print(f"Found {len(sources['diagrams'])} diagram files.")
    for d in sources["diagrams"]:
        print(f"  - {d}")

    print("\nVerifying integrity...")
    report = verify_sources_integrity(sources)
    print(f"Valid Zips: {len(report['valid_zips'])}")
    if report["corrupt_zips"]:
        print("Corrupt Zips:")
        for z, err in report["corrupt_zips"].items():
            print(f"  - {z}: {err}")
