from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml
from PIL import Image, ImageOps


@dataclass(frozen=True)
class ImageTarget:
    width: int
    height: int


def _bundle_dirs_from_manifest(manifest: dict) -> list[tuple[int, str, list[str]]]:
    parsed: list[tuple[int, str, list[str]]] = []
    for b in manifest.get("bundles") or []:
        order = int(b["order"])
        slug = str(b["slug"])
        required_images = list((b.get("outputs") or {}).get("required_images") or [])
        parsed.append((order, slug, required_images))
    parsed.sort(key=lambda x: x[0])
    return parsed


def _targets_from_manifest(manifest: dict, key: str) -> list[ImageTarget]:
    raw = (manifest.get("platform_image_targets") or {}).get(key) or []
    return [ImageTarget(int(t["width"]), int(t["height"])) for t in raw]


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _render_mermaid_svg(*, src: Path, dest_svg: Path, mermaid_config: Path) -> None:
    puppeteer_config = mermaid_config.parent / "puppeteer-config.json"
    cmd = ["mmdc", "-i", str(src), "-o", str(dest_svg), "-c", str(mermaid_config)]
    if puppeteer_config.exists():
        cmd += ["-p", str(puppeteer_config)]
    _run(cmd)


def _render_mermaid_png(*, src: Path, dest_png: Path, mermaid_config: Path) -> None:
    puppeteer_config = mermaid_config.parent / "puppeteer-config.json"
    cmd = ["mmdc", "-i", str(src), "-o", str(dest_png), "-c", str(mermaid_config)]
    if puppeteer_config.exists():
        cmd += ["-p", str(puppeteer_config)]
    _run(cmd)


def _render_graphviz_svg(*, src: Path, dest_svg: Path) -> None:
    _run(["dot", "-Tsvg", str(src), "-o", str(dest_svg)])


def _render_graphviz_png(*, src: Path, dest_png: Path) -> None:
    _run(["dot", "-Tpng", str(src), "-o", str(dest_png)])


def _pad_to_exact_size(*, src_png: Path, dest_png: Path, width: int, height: int) -> None:
    with Image.open(src_png) as img:
        img_rgba = img.convert("RGBA")
        padded = ImageOps.pad(
            img_rgba,
            (width, height),
            method=Image.Resampling.LANCZOS,
            color=(255, 255, 255, 255),
            centering=(0.5, 0.5),
        )
        padded.save(dest_png, format="PNG", optimize=True)


def render_bundle_covers(
    *,
    manifest_path: Path,
    series_root: Path,
    bundle_slug: str | None = None,
    strict_sources: bool = False,
) -> None:
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    bundles = _bundle_dirs_from_manifest(manifest)

    mermaid_config = series_root / "00_series_meta" / "mermaid-config.json"
    if not mermaid_config.exists():
        raise FileNotFoundError(f"Missing Mermaid config: {mermaid_config}")

    if shutil.which("mmdc") is None:
        raise RuntimeError("`mmdc` not found on PATH")
    if shutil.which("dot") is None:
        raise RuntimeError("`dot` (Graphviz) not found on PATH")

    article_targets = _targets_from_manifest(manifest, "linkedin_article_cover")
    square_targets = _targets_from_manifest(manifest, "linkedin_post_square")
    if not article_targets or not square_targets:
        raise ValueError("Missing platform_image_targets in manifest")

    for order, slug, required_images in bundles:
        if bundle_slug and slug != bundle_slug:
            continue
        if "cover_summary" not in required_images:
            continue

        src_dir = series_root / f"{order:02d}_{slug}" / "images" / "src"
        out_dir = series_root / f"{order:02d}_{slug}" / "images" / "out"
        out_dir.mkdir(parents=True, exist_ok=True)

        mmd = src_dir / "cover_summary.mmd"
        dot = src_dir / "cover_summary.dot"
        if mmd.exists():
            master_svg = out_dir / "cover_summary.svg"
            tmp_png = out_dir / "_cover_summary_tmp.png"
            _render_mermaid_svg(src=mmd, dest_svg=master_svg, mermaid_config=mermaid_config)
            _render_mermaid_png(src=mmd, dest_png=tmp_png, mermaid_config=mermaid_config)
        elif dot.exists():
            master_svg = out_dir / "cover_summary.svg"
            tmp_png = out_dir / "_cover_summary_tmp.png"
            _render_graphviz_svg(src=dot, dest_svg=master_svg)
            _render_graphviz_png(src=dot, dest_png=tmp_png)
        else:
            if strict_sources:
                raise FileNotFoundError(
                    f"Missing cover source for bundle {slug}: {mmd} or {dot}"
                )
            continue

        for t in article_targets:
            dest = out_dir / f"cover_linkedin_article_{t.width}x{t.height}.png"
            _pad_to_exact_size(src_png=tmp_png, dest_png=dest, width=t.width, height=t.height)

        for t in square_targets:
            dest = out_dir / f"cover_linkedin_post_square_{t.width}x{t.height}.png"
            _pad_to_exact_size(src_png=tmp_png, dest_png=dest, width=t.width, height=t.height)

        tmp_png.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render outreach series images (currently: cover_summary LinkedIn targets)."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml"),
    )
    parser.add_argument(
        "--root", type=Path, default=Path("publications/P4_Outreach_Series")
    )
    parser.add_argument("--bundle", type=str, default=None, help="Render only a single bundle slug")
    parser.add_argument(
        "--strict-sources",
        action="store_true",
        help="Fail if required cover_summary source is missing",
    )
    args = parser.parse_args()

    render_bundle_covers(
        manifest_path=args.manifest,
        series_root=args.root,
        bundle_slug=args.bundle,
        strict_sources=args.strict_sources,
    )
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
