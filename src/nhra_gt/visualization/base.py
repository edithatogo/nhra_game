from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from .config import PlotConfig

logger = logging.getLogger(__name__)


@runtime_checkable
class Plotter(Protocol):
    """Protocol for standardized figure generation functions."""

    def __call__(
        self, data: pd.DataFrame, config: PlotConfig | None = None, **kwargs: Any
    ) -> Figure: ...


def save_figure(
    fig: Figure,
    path: str | Path,
    config: PlotConfig | None = None,
    formats: list[str] | None = None,
) -> None:
    """
    Saves a matplotlib figure in multiple formats defined by PlotConfig.

    Args:
        fig: The matplotlib Figure object.
        path: File path (extension optional).
        config: PlotConfig for DPI and other settings.
        formats: List of formats (e.g. ['png', 'svg']). If None, uses config.format.
    """
    if config is None:
        config = PlotConfig()

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    target_formats = formats or [config.format]

    for fmt in target_formats:
        out_path = p.with_suffix(f".{fmt}")
        fig.savefig(
            out_path,
            dpi=config.dpi,
            bbox_inches=config.bbox_inches,
            transparent=config.transparent,
        )
        logger.info(f"Figure saved to {out_path}")

    plt.close(fig)