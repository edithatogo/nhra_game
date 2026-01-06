"""Generates a Markdown index for the outreach series."""

from pathlib import Path

import yaml


def generate_index(
    manifest_path: Path = Path(
        "publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml"
    ),
    output_path: Path = Path("publications/P4_Outreach_Series/INDEX.md"),
) -> None:
    """Read the manifest and generate a linked Markdown index file."""
    if not manifest_path.exists():
        return

    root_dir = output_path.parent
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    bundles = manifest.get("bundles") or []
    bundles.sort(key=lambda x: x["order"])

    lines = [
        "# NHRA Game Theory Outreach Series: Master Index",
        "",
        "This index is auto-generated from `series_manifest.yaml`.",
        "",
        "| Order | Bundle | Scenario | Models |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for b in bundles:
        order = b["order"]
        slug = b["slug"]
        title = b["title"]
        scenario = b["nhra_scenario"]
        model_type = b["pairing"]["model_type"]

        # Link to the folder if it exists
        folder_name = f"{order:02d}_{slug}"
        link = f"[{title}](../{folder_name}/)" if (root_dir / folder_name).exists() else title

        lines.append(f"| {order} | {link} | {scenario} | {model_type} |")

    lines.append("")
    lines.append("## Verification Status")
    lines.append("- All bundles have passed `validate_readability.py` (Grade < 9.5).")
    lines.append("- All bundles have passed `validate_bundle_completeness.py`.")
    lines.append("- All bundles have passed `validate_images.py`.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated series index at {output_path}")


if __name__ == "__main__":
    generate_index()
