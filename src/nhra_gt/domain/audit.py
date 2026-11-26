"""Records structured audit trails and manages versioned artifacts for experiments."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from git import Repo
from git.exc import GitError


class Recorder:
    """Records structured audit trails and manages versioned artifacts for experiments."""

    def __init__(self, base_output_dir: str | Path = "outputs/experiments"):
        """Initialize the audit logger with a base output directory."""
        self.base_output_dir = Path(base_output_dir)
        self.current_experiment: dict[str, Any] | None = None
        self.experiment_dir: Path | None = None

    def _get_git_hash(self) -> str:
        """Retrieves the current git commit hash."""
        try:
            with Repo(search_parent_directories=True) as repo:
                return repo.head.commit.hexsha
        except GitError, OSError, ValueError:
            return "unknown"

    def start_experiment(self, experiment_name: str, **metadata: Any) -> None:
        """Starts a new experiment record and creates a timestamped directory."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")

        # Structure: outputs/experiments/YYYY-MM-DD/experiment_name_HHMMSS/
        self.experiment_dir = self.base_output_dir / date_str / f"{experiment_name}_{time_str}"
        self.experiment_dir.mkdir(parents=True, exist_ok=True)

        self.current_experiment = {
            "experiment_name": experiment_name,
            "timestamp": now.isoformat(),
            "experiment_dir": str(self.experiment_dir),
            "git_hash": self._get_git_hash(),
            "start_time": time.time(),
            **metadata,
        }

    def get_artifact_path(self, filename: str) -> Path:
        """Returns a versioned path for an artifact within the current experiment directory."""
        if not self.experiment_dir:
            # Fallback if no experiment started, but ideally we should raise or start a default
            message = "Experiment not started. Call start_experiment first."
            raise RuntimeError(message)
        return self.experiment_dir / filename

    def end_experiment(self) -> None:
        """Ends the current experiment record and saves metadata to disk."""
        if not self.current_experiment or not self.experiment_dir:
            return

        self.current_experiment["end_time"] = time.time()
        self.current_experiment["duration_seconds"] = (
            self.current_experiment["end_time"] - self.current_experiment["start_time"]
        )

        # Save metadata to JSON within the experiment directory
        filepath = self.experiment_dir / "metadata.json"

        with open(filepath, "w") as f:
            json.dump(self.current_experiment, f, indent=2)

        self.current_experiment = None
        self.experiment_dir = None
