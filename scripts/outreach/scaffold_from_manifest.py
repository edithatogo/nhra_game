"""Scaffolds the directory structure for the outreach series based on series_manifest.yaml."""

import argparse
from pathlib import Path

import yaml


def _parse_bundles_minimal(manifest_text: str) -> list[tuple[int, str]]:
    """Minimal YAML parsing to extract bundle `order` and `slug`.

    Rationale:
    - Avoid adding new dependencies for bootstrap.
    - Avoid repo-wide scans in sync-backed filesystems; rely on the manifest as inventory.
    """
    bundles: list[dict[str, object]] = []
    # Simplified parser logic or full YAML load if available
    return []


def scaffold_from_manifest(
    *, manifest_path: Path, series_root: Path, dry_run: bool = False
) -> list[Path]:
    """Create bundle directories and initial files from manifest data."""
    if not manifest_path.exists():
        return []

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    bundles = manifest.get("bundles") or []
    created = []

    for b in bundles:
        order = b["order"]
        slug = b["slug"]
        dir_name = f"{order:02d}_{slug}"
        full_path = series_root / dir_name

        if not dry_run:
            full_path.mkdir(parents=True, exist_ok=True)
            (full_path / "images" / "src").mkdir(parents=True, exist_ok=True)
            (full_path / "images" / "out").mkdir(parents=True, exist_ok=True)

        created.append(full_path)

    return created


def main() -> int:
    """Run the CLI directory scaffolding tool."""
    parser = argparse.ArgumentParser(
        description="Create outreach series folder scaffold from series_manifest.yaml (manifest-only, no scans)."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml"),
    )
    parser.add_argument("--root", type=Path, default=Path("publications/P4_Outreach_Series"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    created = scaffold_from_manifest(
        manifest_path=args.manifest, series_root=args.root, dry_run=args.dry_run
    )

    if args.dry_run:
        for p in created:
            print(p.as_posix())
    else:
        print(f"scaffolded_paths={len(created)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
