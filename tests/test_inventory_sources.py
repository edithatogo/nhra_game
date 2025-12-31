from __future__ import annotations

import os
from pathlib import Path

from scripts.audit.inventory_sources import discover_sources


def test_discover_sources_finds_zips_and_diagrams(tmp_path: Path) -> None:
    # Setup mock structure
    (tmp_path / "archive").mkdir()
    (tmp_path / "archive" / "test1.zip").write_text("fake zip")
    (tmp_path / "test2.zip").write_text("fake zip")
    (tmp_path / "diagrams").mkdir()
    (tmp_path / "diagrams" / "flow.mmd").write_text("graph TD")
    (tmp_path / "diagrams" / "structure.dot").write_text("digraph G {}")
    (tmp_path / "ignored.txt").write_text("ignore me")

    # Change cwd to tmp_path for the test
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        sources = discover_sources()

        # Verify zips
        zips = [p.as_posix() for p in sources["zips"]]
        assert "archive/test1.zip" in zips
        assert "test2.zip" in zips

        # Verify diagrams
        diagrams = [p.as_posix() for p in sources["diagrams"]]
        assert "diagrams/flow.mmd" in diagrams
        assert "diagrams/structure.dot" in diagrams

        assert len(sources["zips"]) == 2
        assert len(sources["diagrams"]) == 2
    finally:
        os.chdir(old_cwd)


def test_verify_sources_integrity(tmp_path: Path) -> None:
    import zipfile

    from scripts.audit.inventory_sources import verify_sources_integrity

    # Create valid zip
    valid_zip = tmp_path / "valid.zip"
    with zipfile.ZipFile(valid_zip, "w") as zf:
        zf.writestr("test.txt", "content")

    # Create invalid zip
    invalid_zip = tmp_path / "corrupt.zip"
    invalid_zip.write_text("not a zip file")

    sources = {"zips": [valid_zip, invalid_zip], "diagrams": []}

    report = verify_sources_integrity(sources)

    assert report["valid_zips"] == [valid_zip]
    assert invalid_zip in report["corrupt_zips"]
    assert report["corrupt_zips"][invalid_zip] == "File is not a zip file"
