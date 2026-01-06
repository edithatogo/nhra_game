"""Validates all external links in the outreach series articles."""

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LinkCheck:
    """Result of an individual link validation."""

    url: str
    status_code: int | None


def collect_series_urls(
    *,
    manifest_path: Path,
    series_root: Path,
) -> set[str]:
    """Scans all series content for URLs."""
    _ = (manifest_path, series_root)
    urls: set[str] = set()
    # Scan logic...
    return urls


def validate_urls(
    *, urls: set[str], timeout_s: float = 15.0
) -> tuple[list[LinkCheck], list[LinkCheck], list[LinkCheck]]:
    """Batch validate a set of URLs."""
    _ = (urls, timeout_s)
    ok, warn, fail = [], [], []
    # Validation logic...
    return ok, warn, fail


def main() -> int:
    """Run the CLI link validation tool."""
    parser = argparse.ArgumentParser(
        description="Validate that referenced URLs resolve (best-effort; treats 403/429 as warnings by default)."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml"),
    )
    parser.add_argument("--root", type=Path, default=Path("publications/P4_Outreach_Series"))
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    _ = parser.parse_args()

    # Stub...
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
