from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import requests
import yaml


@dataclass(frozen=True)
class LinkCheck:
    url: str
    status_code: int | None
    outcome: str  # ok|warn|fail
    detail: str | None = None


_url_re = re.compile(r"https?://[^\s<>()]+")


def _extract_urls(text: str) -> set[str]:
    urls: set[str] = set()
    for raw in _url_re.findall(text):
        url = raw.rstrip(').,;]}>\"\'')
        if url.startswith("http://") or url.startswith("https://"):
            urls.add(url)
    return urls


def _latest_versioned_md(folder: Path, stem_prefix: str) -> Path | None:
    if not folder.exists():
        return None
    pat = re.compile(rf"^{re.escape(stem_prefix)}_v(\d+)_(\d{{8}})\.md$")
    best: tuple[int, str, Path] | None = None
    for p in folder.iterdir():
        if not p.is_file():
            continue
        m = pat.match(p.name)
        if not m:
            continue
        v = int(m.group(1))
        d = m.group(2)
        cand = (v, d, p)
        if best is None or cand[:2] > best[:2]:
            best = cand
    return best[2] if best else None


def _bundle_dirs_from_manifest(manifest: dict) -> list[tuple[int, str, tuple[str, ...]]]:
    parsed: list[tuple[int, str, tuple[str, ...]]] = []
    for b in manifest.get("bundles") or []:
        order = int(b["order"])
        slug = str(b["slug"])
        required = tuple(((b.get("outputs") or {}).get("required") or []))
        parsed.append((order, slug, required))
    parsed.sort(key=lambda x: x[0])
    return parsed


def collect_series_urls(
    *,
    manifest_path: Path,
    series_root: Path,
    library_path: Path | None = None,
    bundle_slug: str | None = None,
) -> set[str]:
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    bundles = _bundle_dirs_from_manifest(manifest)

    expected_stems = {
        "linkedin_article": ("article", "linkedin_article"),
        "linkedin_post": ("social", "linkedin_post"),
        "x_thread": ("social", "x_thread"),
    }

    urls: set[str] = set()

    if library_path and library_path.exists():
        library = yaml.safe_load(library_path.read_text(encoding="utf-8")) or []
        if isinstance(library, list):
            for entry in library:
                if isinstance(entry, dict) and entry.get("url"):
                    urls |= _extract_urls(str(entry["url"]))

    for order, slug, required in bundles:
        if bundle_slug and slug != bundle_slug:
            continue
        bundle_root = series_root / f"{order:02d}_{slug}"
        for out in required:
            if out not in expected_stems:
                continue
            subdir, stem = expected_stems[out]
            latest = _latest_versioned_md(bundle_root / subdir, stem)
            if not latest:
                continue
            urls |= _extract_urls(latest.read_text(encoding="utf-8", errors="replace"))

    return urls


def _check_url(url: str, *, timeout_s: float) -> LinkCheck:
    headers = {
        "User-Agent": "NHRA-GT-LinkCheck/1.0",
        "Accept": "text/html,application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        if url.startswith("https://doi.org/") or url.startswith("http://doi.org/"):
            resp = requests.get(url, timeout=timeout_s, allow_redirects=False, headers=headers)
        else:
            # Avoid downloading large PDFs by default.
            ranged = dict(headers)
            ranged["Range"] = "bytes=0-0"
            resp = requests.get(
                url, timeout=timeout_s, allow_redirects=True, headers=ranged, stream=True
            )
        status = int(resp.status_code)
        resp.close()
    except requests.RequestException as exc:
        return LinkCheck(url=url, status_code=None, outcome="fail", detail=f"{type(exc).__name__}: {exc}")

    if 200 <= status < 400 or status == 206:
        return LinkCheck(url=url, status_code=status, outcome="ok")
    if status in {403, 429}:
        return LinkCheck(url=url, status_code=status, outcome="warn")
    return LinkCheck(url=url, status_code=status, outcome="fail")


def validate_urls(*, urls: set[str], timeout_s: float = 15.0) -> tuple[list[LinkCheck], list[LinkCheck], list[LinkCheck]]:
    ok: list[LinkCheck] = []
    warn: list[LinkCheck] = []
    fail: list[LinkCheck] = []

    for url in sorted(urls):
        res = _check_url(url, timeout_s=timeout_s)
        if res.outcome == "ok":
            ok.append(res)
        elif res.outcome == "warn":
            warn.append(res)
        else:
            fail.append(res)
    return ok, warn, fail


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that referenced URLs resolve (best-effort; treats 403/429 as warnings by default)."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml"),
    )
    parser.add_argument("--root", type=Path, default=Path("publications/P4_Outreach_Series"))
    parser.add_argument(
        "--library",
        type=Path,
        default=Path("publications/shared/references/library.yaml"),
    )
    parser.add_argument("--bundle", type=str, default=None, help="Validate only a single bundle slug")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings (403/429) as failures.",
    )
    args = parser.parse_args()

    urls = collect_series_urls(
        manifest_path=args.manifest,
        series_root=args.root,
        library_path=args.library,
        bundle_slug=args.bundle,
    )
    ok, warn, fail = validate_urls(urls=urls, timeout_s=args.timeout)

    if warn:
        print("Warnings (may be bot-protected / rate-limited):")
        for w in warn:
            code = "?" if w.status_code is None else str(w.status_code)
            print(f"- {code} {w.url}")
    if fail:
        print("Broken / unreachable links:")
        for f in fail:
            code = "?" if f.status_code is None else str(f.status_code)
            extra = "" if not f.detail else f" ({f.detail})"
            print(f"- {code} {f.url}{extra}")

    if fail or (args.strict and warn):
        return 2
    print(f"ok links_checked={len(ok) + len(warn) + len(fail)} warnings={len(warn)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

