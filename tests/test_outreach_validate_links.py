from __future__ import annotations

from pathlib import Path

import pytest

from scripts.outreach.validate_links import _extract_urls, collect_series_urls, validate_urls


class _DummyResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code

    def close(self) -> None:  # pragma: no cover
        return None


def test_extract_urls_trims_punctuation() -> None:
    text = (
        "See https://example.com/foo). And [bar](https://example.com/bar), "
        "and https://doi.org/10.2307/1907266."
    )
    urls = _extract_urls(text)
    assert "https://example.com/foo" in urls
    assert "https://example.com/bar" in urls
    assert "https://doi.org/10.2307/1907266" in urls


@pytest.fixture
def mini_series(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "series"
    meta = root / "00_series_meta"
    meta.mkdir(parents=True)

    manifest = meta / "series_manifest.yaml"
    manifest.write_text(
        """
series:
  id: p4_outreach_series
bundles:
  - order: 1
    slug: demo_bundle
    outputs:
      required: [linkedin_article]
""".lstrip(),
        encoding="utf-8",
    )

    library = tmp_path / "library.yaml"
    library.write_text(
        """
- id: Demo
  url: "https://example.com/library"
""".lstrip(),
        encoding="utf-8",
    )

    article_dir = root / "01_demo_bundle" / "article"
    article_dir.mkdir(parents=True)
    (article_dir / "linkedin_article_v1_20260101.md").write_text(
        "Old link https://example.com/old", encoding="utf-8"
    )
    (article_dir / "linkedin_article_v2_20260102.md").write_text(
        "New link https://example.com/new", encoding="utf-8"
    )

    return root, manifest, library


def test_collect_series_urls_uses_latest_version(mini_series: tuple[Path, Path, Path]) -> None:
    root, manifest, library = mini_series
    urls = collect_series_urls(
        manifest_path=manifest, series_root=root, library_path=library, bundle_slug=None
    )
    assert "https://example.com/library" in urls
    assert "https://example.com/new" in urls
    assert "https://example.com/old" not in urls


def test_validate_urls_classification(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, *args, **kwargs):  # noqa: ANN001
        if "doi.org" in url:
            return _DummyResponse(302)
        if url.endswith("/ok"):
            return _DummyResponse(200)
        if url.endswith("/warn"):
            return _DummyResponse(403)
        return _DummyResponse(404)

    monkeypatch.setattr("scripts.outreach.validate_links.requests.get", fake_get)

    ok, warn, fail = validate_urls(
        urls={
            "https://doi.org/10.2307/1907266",
            "https://example.com/ok",
            "https://example.com/warn",
            "https://example.com/bad",
        },
        timeout_s=1.0,
    )
    assert {r.url for r in ok} == {"https://doi.org/10.2307/1907266", "https://example.com/ok"}
    assert {r.url for r in warn} == {"https://example.com/warn"}
    assert {r.url for r in fail} == {"https://example.com/bad"}

