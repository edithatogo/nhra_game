from __future__ import annotations

from pathlib import Path

from scripts.outreach.validate_bundle_completeness import validate_bundles


def test_validate_bundles_missing(tmp_path: Path) -> None:
    root = tmp_path / "series"
    meta = root / "00_series_meta"
    meta.mkdir(parents=True)
    manifest = meta / "series_manifest.yaml"
    manifest.write_text(
        """
platform_image_targets:
  linkedin_article_cover: [{ width: 1200, height: 644 }]
  linkedin_post_square: [{ width: 1200, height: 1200 }]
bundles:
  - order: 1
    slug: demo
    outputs:
      required: [linkedin_article, linkedin_post, x_thread]
""".lstrip(),
        encoding="utf-8",
    )

    missing, errors = validate_bundles(manifest_path=manifest, series_root=root)
    assert errors == []
    assert len(missing) == 3


def test_validate_bundles_ok(tmp_path: Path) -> None:
    root = tmp_path / "series"
    meta = root / "00_series_meta"
    meta.mkdir(parents=True)
    manifest = meta / "series_manifest.yaml"
    manifest.write_text(
        """
platform_image_targets:
  linkedin_article_cover: [{ width: 1200, height: 644 }]
  linkedin_post_square: [{ width: 1200, height: 1200 }]
bundles:
  - order: 1
    slug: demo
    outputs:
      required: [linkedin_article, linkedin_post, x_thread]
""".lstrip(),
        encoding="utf-8",
    )

    bundle = root / "01_demo"
    (bundle / "article").mkdir(parents=True)
    (bundle / "social").mkdir(parents=True)

    (bundle / "article" / "linkedin_article_v1_20260103.md").write_text("hi", encoding="utf-8")
    (bundle / "social" / "linkedin_post_v1_20260103.md").write_text("hi", encoding="utf-8")
    (bundle / "social" / "x_thread_v1_20260103.md").write_text("Tweet 1: hi", encoding="utf-8")

    missing, errors = validate_bundles(manifest_path=manifest, series_root=root)
    assert missing == []
    assert errors == []


def test_validate_bundles_filtering_behavior(tmp_path: Path) -> None:
    root = tmp_path / "series"
    meta = root / "00_series_meta"
    meta.mkdir(parents=True)
    manifest = meta / "series_manifest.yaml"
    manifest.write_text(
        """
platform_image_targets:
  linkedin_article_cover: [{ width: 1200, height: 644 }]
  linkedin_post_square: [{ width: 1200, height: 1200 }]
bundles:
  - order: 1
    slug: one
    outputs:
      required: [linkedin_article]
  - order: 2
    slug: two
    outputs:
      required: [linkedin_article]
""".lstrip(),
        encoding="utf-8",
    )

    # Only bundle "one" has an article.
    (root / "01_one" / "article").mkdir(parents=True)
    (root / "01_one" / "article" / "linkedin_article_v1_20260103.md").write_text(
        "hi", encoding="utf-8"
    )

    missing, _errors = validate_bundles(manifest_path=manifest, series_root=root)
    assert any("02_two" in m for m in missing)
