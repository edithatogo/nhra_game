from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from .config import PlotConfig


@runtime_checkable
class Plotter(Protocol):
    """Protocol for standardized figure generation functions."""

    def __call__(
        self, data: pd.DataFrame, config: PlotConfig | None = None, **kwargs: Any
    ) -> Figure: ...


def save_figure(fig: Figure, path: Path, config: PlotConfig) -> None:
    """Standardized utility to save figures using PlotConfig."""
    path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure extension matches config if not provided in path
    if not path.suffix:
        path = path.with_suffix(f".{config.format}")

    fig.savefig(
        path,
        dpi=config.dpi,
        bbox_inches=config.bbox_inches,
        transparent=config.transparent,
    )
    plt.close(fig)
