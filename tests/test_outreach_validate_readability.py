from __future__ import annotations

from scripts.outreach.validate_readability import _pick_latest_versions, score_text


def test_score_text_returns_grade() -> None:
    words, sentences, syllables, grade = score_text("This is a short sentence. This is another one.")
    assert words > 0
    assert sentences >= 1
    assert syllables > 0
    assert isinstance(grade, float)


def test_pick_latest_versions(tmp_path) -> None:
    d = tmp_path / "bundle" / "article"
    d.mkdir(parents=True)
    p1 = d / "linkedin_article_v1_20260103.md"
    p2 = d / "linkedin_article_v2_20260103.md"
    p1.write_text("a", encoding="utf-8")
    p2.write_text("b", encoding="utf-8")
    latest = _pick_latest_versions([p1, p2])
    assert latest == [p2]
