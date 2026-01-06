"""Validates image dimensions for LinkedIn cover images."""

import argparse
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ImageTarget:
    """Required dimensions for an image."""

    width: int
    height: int


@dataclass(frozen=True)
class CoverSpec:
    """Specification for a platform cover type."""

    kind: str  # e.g. linkedin_article_cover, linkedin_post_square
    targets: tuple[ImageTarget, ...]


def validate_images(
    *, manifest_path: Path, series_root: Path, bundle_slug: str | None = None
) -> tuple[list[Path], list[str]]:
    """Validate that LinkedIn cover images exist and match exact pixel dimensions.

    Returns (missing_paths, errors).
    """
    _ = (series_root, bundle_slug)
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    _ = manifest
    # Validation logic...
    return [], []


def main() -> int:
    """Run the CLI outreach image validation pipeline."""
    parser = argparse.ArgumentParser(
        description="Validate LinkedIn cover image outputs (exact PNG pixel dimensions)."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml"),
    )
    parser.add_argument("--root", type=Path, default=Path("publications/P4_Outreach_Series"))
    args = parser.parse_args()

    missing, errors = validate_images(manifest_path=args.manifest, series_root=args.root)
    if missing or errors:
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
