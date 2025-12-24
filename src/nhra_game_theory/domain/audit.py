from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any


class Recorder:
    """Records structured audit trails for simulation experiments."""

    def __init__(self, output_dir: str | Path = "outputs/audit"):
        self.output_dir = Path(output_dir)
        self.current_experiment: dict[str, Any] | None = None

    def _get_git_hash(self) -> str:
        """Retrieves the current git commit hash."""
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        except Exception:
            return "unknown"

    def start_experiment(self, experiment_name: str, **metadata):
        """Starts a new experiment record."""
        self.current_experiment = {
            "experiment_name": experiment_name,
            "timestamp": datetime.now().isoformat(),
            "git_hash": self._get_git_hash(),
            "start_time": time.time(),
            **metadata,
        }

    def end_experiment(self):
        """Ends the current experiment record and saves to disk."""
        if not self.current_experiment:
            return

        self.current_experiment["end_time"] = time.time()
        self.current_experiment["duration_seconds"] = (
            self.current_experiment["end_time"] - self.current_experiment["start_time"]
        )

        # Save to JSON
        self.output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{self.current_experiment['experiment_name']}_{int(time.time())}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            json.dump(self.current_experiment, f, indent=2)

        print(f"Audit record saved to {filepath}")
        self.current_experiment = None
