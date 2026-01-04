from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class BundleRequirement:
    order: int
    slug: str
    required_outputs: tuple[str, ...]


def _load_bundle_requirements(manifest: dict) -> list[BundleRequirement]:
    bundles = manifest.get("bundles") or []
    parsed: list[BundleRequirement] = []
    for b in bundles:
        order = int(b["order"])
        slug = str(b["slug"])
        required = tuple(((b.get("outputs") or {}).get("required") or []))
        parsed.append(BundleRequirement(order=order, slug=slug, required_outputs=required))
    parsed.sort(key=lambda x: x.order)
    return parsed


def _find_any_versioned_md(folder: Path, stem_prefix: str) -> list[Path]:
    if not folder.exists():
        return []
    pattern = re.compile(rf"^{re.escape(stem_prefix)}_v\d+_\d{{8}}\.md$")
    matches: list[Path] = []
    for p in folder.iterdir():
        if p.is_file() and pattern.match(p.name):
            matches.append(p)
    return sorted(matches)


def validate_bundles(*, manifest_path: Path, series_root: Path) -> tuple[list[str], list[str]]:
    """
    Validate that each bundle has at least one versioned Markdown draft per required output.

    Returns (missing, errors).
    """
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    bundles = _load_bundle_requirements(manifest)

    missing: list[str] = []
    errors: list[str] = []

    expected_stems = {
        "linkedin_article": ("article", "linkedin_article"),
        "linkedin_post": ("social", "linkedin_post"),
        "x_thread": ("social", "x_thread"),
    }

    for b in bundles:
        bundle_root = series_root / f"{b.order:02d}_{b.slug}"
        for out in b.required_outputs:
            if out not in expected_stems:
                errors.append(f"{bundle_root}: unknown required output '{out}' in manifest")
                continue
            subdir, stem = expected_stems[out]
            matches = _find_any_versioned_md(bundle_root / subdir, stem)
            if not matches:
                missing.append(f"{bundle_root}/{subdir}: missing {stem}_v#_YYYYMMDD.md")

    return missing, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate outreach bundle completeness (required versioned Markdown drafts exist)."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml"),
    )
    parser.add_argument(
        "--root", type=Path, default=Path("publications/P4_Outreach_Series")
    )
    parser.add_argument(
        "--bundle",
        type=str,
        default=None,
        help="Validate only a single bundle slug (e.g., definition_game).",
    )
    args = parser.parse_args()

    missing, errors = validate_bundles(manifest_path=args.manifest, series_root=args.root)
    if args.bundle:
        missing = [m for m in missing if f"_{args.bundle}/" in m]
        errors = [e for e in errors if f"_{args.bundle}/" in e or f" {args.bundle} " in e]
    if missing:
        print("Missing bundle outputs:")
        for m in missing:
            print(f"- {m}")
    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"- {e}")
    return 0 if (not missing and not errors) else 2


if __name__ == "__main__":
    raise SystemExit(main())
