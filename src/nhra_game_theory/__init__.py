from __future__ import annotations

import contextlib

__all__ = ["v8", "v9", "logfire"]
__version__ = "0.25.0"

with contextlib.suppress(ImportError):
    import logfire
    # logfire.configure() # Disabled to prevent environment hangs
    # logfire.instrument_pydantic()
