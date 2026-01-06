"""Ensures each file meets the minimum test coverage threshold."""

import json
import sys
from pathlib import Path

THRESHOLD = 80.0


def main() -> None:
    """Check coverage.json against threshold."""
    cov_path = Path("coverage.json")
    if not cov_path.exists():
        print("coverage.json not found. Run pytest with --cov-report=json:coverage.json")
        sys.exit(2)

    with open(cov_path) as f:
        data = json.load(f)

    bad = []
    for f, f_data in data.get("files", {}).items():
        pct = f_data["summary"]["percent_covered"]
        if pct < THRESHOLD:
            bad.append((f, pct))

    if bad:
        print(f"Per-file coverage threshold not met: {THRESHOLD:.1f}%")
        for f, pct in sorted(bad, key=lambda x: x[1]):
            print(f"  {f}: {pct:.2f}%")
        sys.exit(1)

    print(f"Per-file coverage OK (>= {THRESHOLD:.1f}%) for {len(data.get('files', {}))} files.")


if __name__ == "__main__":
    main()
