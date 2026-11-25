"""Frozen application records registered with JAX's own dataclass API."""

from dataclasses import dataclass, field, replace
from typing import Any, Self, dataclass_transform

try:
    from jax.tree_util import register_dataclass
except ImportError:  # pragma: no cover
    register_dataclass = None


@dataclass(frozen=True)
class PytreeRecord:
    """Shared value replacement for immutable state records."""

    def replace(self, **changes: Any) -> Self:
        """Return the same record type with the specified fields replaced."""
        return replace(self, **changes)


@dataclass_transform(frozen_default=True, field_specifiers=(field,))
def pytree_dataclass[Record](cls: type[Record]) -> type[Record]:
    """Register a frozen dataclass and its marked static fields."""
    result = dataclass(frozen=True)(cls)
    if register_dataclass is not None:
        return register_dataclass(result)
    return result
