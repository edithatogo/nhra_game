from __future__ import annotations

import json
from pathlib import Path

from scripts.audit.inventory_sources import discover_sources
from src.nhra_gt.audit.fingerprint import fingerprint_zip


def fingerprint_all() -> None:
    """Discover all zips and fingerprint their contents."""
    sources = discover_sources()
    all_fingerprints = {}

    print(f"Processing {len(sources['zips'])} zip files...")
    for zip_path in sources["zips"]:
        print(f"  Fingerprinting {zip_path}...")
        all_fingerprints[str(zip_path)] = fingerprint_zip(zip_path)

    output_dir = Path("data/audit")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "zip_fingerprints.json"
    with open(output_file, "w") as f:
        json.dump(all_fingerprints, f, indent=2)

    print(f"\nSaved fingerprints for {len(all_fingerprints)} archives to {output_file}")


if __name__ == "__main__":
    fingerprint_all()
