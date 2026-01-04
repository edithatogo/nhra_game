from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import yaml
from PIL import Image


@dataclass(frozen=True)
class ImageTarget:
    width: int
    height: int


@dataclass(frozen=True)
class CoverSpec:
    kind: str  # e.g. linkedin_article_cover, linkedin_post_square
    targets: tuple[ImageTarget, ...]


def _load_cover_specs_from_manifest(manifest: dict) -> tuple[CoverSpec, ...]:
    targets = manifest.get("platform_image_targets") or {}

    def parse_targets(key: str) -> CoverSpec:
        raw = targets.get(key) or []
        parsed = tuple(ImageTarget(int(t["width"]), int(t["height"])) for t in raw)
        if not parsed:
            raise ValueError(f"Missing platform_image_targets.{key} in manifest")
        return CoverSpec(kind=key, targets=parsed)

    return (
        parse_targets("linkedin_article_cover"),
        parse_targets("linkedin_post_square"),
    )


def _bundle_dirs_from_manifest(manifest: dict) -> list[tuple[int, str]]:
    bundles = manifest.get("bundles") or []
    parsed: list[tuple[int, str]] = []
    for b in bundles:
        parsed.append((int(b["order"]), str(b["slug"])))
    parsed.sort(key=lambda x: x[0])
    return parsed


def _expected_cover_filenames(spec: CoverSpec) -> list[str]:
    if spec.kind == "linkedin_article_cover":
        prefix = "cover_linkedin_article"
    elif spec.kind == "linkedin_post_square":
        prefix = "cover_linkedin_post_square"
    else:
        raise ValueError(f"Unknown cover spec kind: {spec.kind}")

    return [f"{prefix}_{t.width}x{t.height}.png" for t in spec.targets]


def validate_cover_images(
    *, manifest_path: Path, series_root: Path, bundle_slug: str | None = None
) -> tuple[list[Path], list[str]]:
    """
    Validate that LinkedIn cover images exist and match exact pixel dimensions.

    Returns (missing_paths, errors).
    """

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    cover_specs = _load_cover_specs_from_manifest(manifest)
    bundles = _bundle_dirs_from_manifest(manifest)

    missing: list[Path] = []
    errors: list[str] = []

    for order, slug in bundles:
        if bundle_slug and slug != bundle_slug:
            continue
        bundle_root = series_root / f"{order:02d}_{slug}" / "images" / "out"

        for spec in cover_specs:
            for filename in _expected_cover_filenames(spec):
                path = bundle_root / filename
                if not path.exists():
                    missing.append(path)
                    continue
                with Image.open(path) as img:
                    w, h = img.size
                expected = filename.rsplit("_", 1)[1].removesuffix(".png")
                ew, eh = expected.split("x")
                if (w, h) != (int(ew), int(eh)):
                    errors.append(f"{path}: expected {expected}px, got {w}x{h}px")

    return missing, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate LinkedIn cover image outputs (exact PNG pixel dimensions)."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml"),
    )
    parser.add_argument("--root", type=Path, default=Path("publications/P4_Outreach_Series"))
    parser.add_argument(
        "--bundle", type=str, default=None, help="Validate only a single bundle slug"
    )
    args = parser.parse_args()

    missing, errors = validate_cover_images(
        manifest_path=args.manifest, series_root=args.root, bundle_slug=args.bundle
    )

    if missing:
        print("Missing cover images:")
        for p in missing:
            print(f"- {p.as_posix()}")
    if errors:
        print("Cover image dimension errors:")
        for e in errors:
            print(f"- {e}")

    return 0 if (not missing and not errors) else 2


if __name__ == "__main__":
    raise SystemExit(main())
