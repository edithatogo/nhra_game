from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scripts.outreach.validate_images import validate_cover_images


def _write_png(path: Path, *, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    img.save(path, format="PNG")


@pytest.fixture
def mini_series(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "series"
    meta = root / "00_series_meta"
    meta.mkdir(parents=True)

    manifest = meta / "series_manifest.yaml"
    manifest.write_text(
        """
series:
  id: p4_outreach_series
platform_image_targets:
  linkedin_article_cover:
    - { width: 1200, height: 644 }
  linkedin_post_square:
    - { width: 1200, height: 1200 }
bundles:
  - order: 1
    slug: demo_bundle
    outputs:
      required_images: [cover_summary]
""".lstrip(),
        encoding="utf-8",
    )

    return root, manifest


def test_validate_cover_images_missing(mini_series: tuple[Path, Path]) -> None:
    root, manifest = mini_series
    missing, errors = validate_cover_images(manifest_path=manifest, series_root=root)
    assert errors == []
    assert len(missing) == 2


def test_validate_cover_images_ok(mini_series: tuple[Path, Path]) -> None:
    root, manifest = mini_series
    out_dir = root / "01_demo_bundle" / "images" / "out"
    _write_png(out_dir / "cover_linkedin_article_1200x644.png", width=1200, height=644)
    _write_png(out_dir / "cover_linkedin_post_square_1200x1200.png", width=1200, height=1200)

    missing, errors = validate_cover_images(manifest_path=manifest, series_root=root)
    assert missing == []
    assert errors == []


def test_validate_cover_images_dimension_mismatch(mini_series: tuple[Path, Path]) -> None:
    root, manifest = mini_series
    out_dir = root / "01_demo_bundle" / "images" / "out"
    _write_png(out_dir / "cover_linkedin_article_1200x644.png", width=1200, height=645)
    _write_png(out_dir / "cover_linkedin_post_square_1200x1200.png", width=1200, height=1200)

    missing, errors = validate_cover_images(manifest_path=manifest, series_root=root)
    assert missing == []
    assert len(errors) == 1

