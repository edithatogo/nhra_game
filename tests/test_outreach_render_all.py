from __future__ import annotations

from pathlib import Path

from PIL import Image
from scripts.outreach import render_all


def test_render_mermaid_includes_puppeteer_config_when_present(tmp_path: Path, monkeypatch) -> None:
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    mermaid_cfg = cfg_dir / "mermaid-config.json"
    puppeteer_cfg = cfg_dir / "puppeteer-config.json"
    mermaid_cfg.write_text("{}", encoding="utf-8")
    puppeteer_cfg.write_text('{"args": []}', encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_run(cmd, check, stdout, stderr, text):  # type: ignore[no-untyped-def]
        captured["cmd"] = cmd
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr(render_all.subprocess, "run", fake_run)

    render_all._render_mermaid_svg(
        src=tmp_path / "in.mmd", dest_svg=tmp_path / "out.svg", mermaid_config=mermaid_cfg
    )

    cmd = captured["cmd"]
    assert isinstance(cmd, list)
    assert "-p" in cmd
    assert str(puppeteer_cfg) in cmd


def test_render_mermaid_omits_puppeteer_config_when_absent(tmp_path: Path, monkeypatch) -> None:
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    mermaid_cfg = cfg_dir / "mermaid-config.json"
    mermaid_cfg.write_text("{}", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_run(cmd, check, stdout, stderr, text):  # type: ignore[no-untyped-def]
        captured["cmd"] = cmd
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr(render_all.subprocess, "run", fake_run)

    render_all._render_mermaid_png(
        src=tmp_path / "in.mmd", dest_png=tmp_path / "out.png", mermaid_config=mermaid_cfg
    )

    cmd = captured["cmd"]
    assert isinstance(cmd, list)
    assert "-p" not in cmd


def test_pad_to_exact_size(tmp_path: Path) -> None:
    src = tmp_path / "src.png"
    dest = tmp_path / "dest.png"
    Image.new("RGB", (200, 100), color=(255, 255, 255)).save(src, format="PNG")

    render_all._pad_to_exact_size(src_png=src, dest_png=dest, width=1200, height=644)

    with Image.open(dest) as img:
        assert img.size == (1200, 644)
