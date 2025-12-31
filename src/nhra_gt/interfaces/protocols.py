from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

# --- Numeric Typing Aliases ---
# Standard numpy-based float array
FloatArray: Any = NDArray[np.float64]
# Standard numpy-based int array
IntArray: Any = NDArray[np.int_]

# Optional: jaxtyping support if available
try:
    from jaxtyping import Array, Float, Int  # noqa: F401

    has_jaxtyping = True
except ImportError:
    has_jaxtyping = False

HAS_JAXTYPING = has_jaxtyping

# --- Game Theory Protocols ---


@runtime_checkable
class Strategy(Protocol):
    """Protocol for a game-theory strategy (e.g., mixed or pure)."""

    def sample(self) -> Any:  # pragma: no cover
        """Sample an action from the strategy."""
        ...

    def probability(self, action: Any) -> float:  # pragma: no cover
        """Get the probability of a specific action."""
        ...


@runtime_checkable
class NormalFormGame(Protocol):
    """Protocol for a normal-form game container."""

    @property
    def num_players(self) -> int:  # pragma: no cover
        """Number of players in the game."""
        ...

    def payoffs(self, actions: IntArray) -> FloatArray:  # pragma: no cover
        """
        Calculate payoffs for all players given an action profile.

        Args:
            actions: An array of actions, one for each player.

        Returns:
            An array of payoffs, one for each player.
        """
        ...


@runtime_checkable
class ExtensiveFormGame(Protocol):
    """Protocol for an extensive-form (tree) game."""

    def is_terminal(self, state: Any) -> bool: ...  # pragma: no cover
    def get_payoffs(self, state: Any) -> FloatArray: ...  # pragma: no cover
    def get_legal_actions(self, state: Any) -> list[Any]: ...  # pragma: no cover
