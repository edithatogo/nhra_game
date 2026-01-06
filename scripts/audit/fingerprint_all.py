"""Generates fingerprints for all archived ZIP files."""

import json
from pathlib import Path

from nhra_gt.audit.fingerprint import fingerprint_zip


def main() -> None:
    """Run fingerprinting on all zip files in data/."""
    sources = {"zips": list(Path("data/raw").glob("*.zip"))}
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
    main()
