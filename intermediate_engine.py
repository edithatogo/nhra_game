from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_ARCHIVE_ENGINE_PATH = Path(__file__).resolve().parent / "archive" / "intermediate_engine.py"
_SPEC = spec_from_file_location("_nhra_intermediate_engine", _ARCHIVE_ENGINE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load legacy module at {_ARCHIVE_ENGINE_PATH}")

_MOD = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)  # type: ignore[union-attr]

Params = _MOD.Params
State = _MOD.State
baseline_state = _MOD.baseline_state
step = _MOD.step

__all__ = ["Params", "State", "baseline_state", "step"]
