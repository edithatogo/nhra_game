from __future__ import annotations

from pathlib import Path

from scripts.outreach.validate_social import validate_x_threads


def test_validate_social_flags_long_tweet(tmp_path: Path) -> None:
    root = tmp_path / "series"
    social = root / "01_demo" / "social"
    social.mkdir(parents=True)
    (social / "x_thread_v1_20260103.md").write_text("Tweet 1: " + ("a" * 281), encoding="utf-8")
    issues = validate_x_threads(root=root)
    assert len(issues) == 1

