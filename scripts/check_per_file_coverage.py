from __future__ import annotations

import json
import sys
from pathlib import Path

THRESHOLD = float(sys.argv[1]) if len(sys.argv) > 1 else 95.0

cov_path = Path("coverage.json")
if not cov_path.exists():
    print("coverage.json not found. Run pytest with --cov-report=json:coverage.json")
    sys.exit(2)

data = json.loads(cov_path.read_text(encoding="utf-8"))
bad = []
for fname, info in data.get("files", {}).items():
    pct = float(info["summary"]["percent_covered"])
    if pct + 1e-9 < THRESHOLD:
        bad.append((fname, pct))

if bad:
    print(f"Per-file coverage threshold not met: {THRESHOLD:.1f}%")
    for f, pct in sorted(bad, key=lambda x: x[1]):
        print(f"  {f}: {pct:.2f}%")
    sys.exit(1)

print(f"Per-file coverage OK (>= {THRESHOLD:.1f}%) for {len(data.get('files', {}))} files.")
