from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PlotConfig(BaseModel):
    """Configuration for figure styling and rendering."""

    # General rendering
    dpi: int = 200
    bbox_inches: str = "tight"
    transparent: bool = False
    format: str = "png"  # Default format, but functions should support others

    # Figure dimensions
    default_figsize: tuple[float, float] = (10, 6)

    # Styling
    linewidth: float = 2.0
    alpha_ribbon: float = 0.25
    alpha_grid: float = 0.15

    # Fonts
    fontsize_title: int = 14
    fontsize_label: int = 11
    fontsize_tick: int = 9
    fontsize_legend: int = 9

    # Colors (Project Standards: Teal / Tealrose)
    primary_color: str = "#008080"  # Teal
    secondary_color: str = "#20B2AA"  # LightSeaGreen
    accent_color: str = "#afeeee"  # PaleTurquoise
    error_color: str = "#CD5C5C"   # IndianRed
    success_color: str = "#2E8B57" # SeaGreen

    # Palette for multi-scenario comparisons
    color_palette: list[str] = Field(
        default_factory=lambda: [
            "#008080",  # Teal
            "#CD5C5C",  # Rose/Red
            "#20B2AA",  # Light Sea Green
            "#4682B4",  # Steel Blue
            "#DAA520",  # Goldenrod
            "#6A5ACD",  # Slate Blue
        ]
    )

    # Extension for custom engine-specific kwargs
    extra_params: dict[str, Any] = Field(default_factory=dict)
