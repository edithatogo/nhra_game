from __future__ import annotations

import warnings

# Re-exporting for backward compatibility, but marking as deprecated.
# New code should use nhra_gt.visualization directly.
from .visualization.distributional import plot_strategy_heatmap
from .visualization.sensitivity import plot_rank_tornado as tornado_from_rankcorr
from .visualization.trajectories import plot_trajectory

__all__ = ["plot_strategy_heatmap", "plot_trajectory", "tornado_from_rankcorr"]

warnings.warn(
    "nhra_gt.plotting is deprecated and will be removed in a future version. "
    "Please use nhra_gt.visualization instead.",
    DeprecationWarning,
    stacklevel=2,
)
