from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Any

try:
    __version__ = version("nhra_gt")
except PackageNotFoundError:
    __version__ = "unknown"

logfire: Any | None = None
try:  # pragma: no cover
    import logfire as _logfire
except ImportError:
    _logfire = None

logfire = _logfire

__all__ = ["__version__", "logfire"]
