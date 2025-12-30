from __future__ import annotations

from typing import Any

__version__ = "0.25.0"

logfire: Any | None = None
try:  # pragma: no cover
    import logfire as _logfire
except ImportError:
    _logfire = None

logfire = _logfire

__all__ = ["__version__", "logfire"]
