from __future__ import annotations

import argparse
import re
from pathlib import Path


def _parse_bundles_minimal(manifest_text: str) -> list[tuple[int, str]]:
    """
    Minimal YAML parsing to extract bundle `order` and `slug`.

    Rationale:
    - Avoid adding new dependencies for bootstrap.
    - Avoid repo-wide scans in sync-backed filesystems; rely on the manifest as inventory.
    """

    bundles: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    for line in manifest_text.splitlines():
        if re.match(r"^\s*-\s+order:\s*\d+\s*$", line):
            if current:
                bundles.append(current)
            current = {"order": int(line.split(":", 1)[1].strip())}
            continue

        match_slug = re.match(r"^\s+slug:\s*([^\s]+)\s*$", line)
        if match_slug and current is not None:
            current["slug"] = match_slug.group(1).strip()

    if current:
        bundles.append(current)

    parsed: list[tuple[int, str]] = []
    for bundle in bundles:
        order = int(bundle["order"])
        slug = str(bundle.get("slug") or "").strip()
        if not slug:
            raise ValueError(f"Missing slug for bundle order {order}")
        parsed.append((order, slug))

    parsed.sort(key=lambda x: x[0])
    return parsed


def scaffold_from_manifest(
    *, manifest_path: Path, series_root: Path, dry_run: bool = False
) -> list[Path]:
    manifest_text = manifest_path.read_text(encoding="utf-8", errors="replace")
    bundles = _parse_bundles_minimal(manifest_text)

    created: list[Path] = []
    for order, slug in bundles:
        bundle_root = series_root / f"{order:02d}_{slug}"
        for sub in ("article", "social", "images/src", "images/out", "feedback"):
            path = bundle_root / sub
            if dry_run:
                created.append(path)
            else:
                path.mkdir(parents=True, exist_ok=True)
                created.append(path)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create outreach series folder scaffold from series_manifest.yaml (manifest-only, no scans)."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml"),
        help="Path to series_manifest.yaml",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("publications/P4_Outreach_Series"),
        help="Series root to create numbered bundle folders under",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print paths without writing")
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

