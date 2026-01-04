"""
Evidence Types and Reliability Schemas.

Defines the structure of evidence entries used in the registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class EvidenceType(Enum):
    EMPIRICAL = auto()
    THEORETICAL = auto()
    EXPERT_OPINION = auto()
    ANECDOTAL = auto()

    def reliability_score(self) -> float:
        scores = {
            EvidenceType.EMPIRICAL: 0.95,
            EvidenceType.THEORETICAL: 0.80,
            EvidenceType.EXPERT_OPINION: 0.65,
            EvidenceType.ANECDOTAL: 0.30,
        }
        return scores.get(self, 0.5)


@dataclass(frozen=True)
class Evidence:
    """Represents a piece of evidence supporting or refuting a claim."""

    source: str
    content: str
    type: EvidenceType
    strength: float  # 0.0 to 1.0
    sentiment: float  # -1.0 (refutes) to 1.0 (supports)


@dataclass(frozen=True)
class ConstraintEvidence:
    """Enhanced evidence structure with dual confidence scoring."""

    source: str
    citation: str
    value: float
    unit: str
    confidence_positive: float  # Supporting confidence (0..1)
    confidence_negative: float  # Contradicting confidence (0..1)
    uncertainty: float  # Residual uncertainty (0..1)
    tags: tuple[str, ...] = ()
