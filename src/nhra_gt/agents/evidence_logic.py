"""
Evidence Analysis and Evaluation Logic.

Extracts structured insights from raw qualitative evidence for model grounding.
"""

from __future__ import annotations

import logging
from typing import Any

from nhra_gt.domain.evidence import ConstraintEvidence, Evidence, EvidenceType

logger = logging.getLogger(__name__)


class EvidenceAnalyzer:
    """Analyzes evidence using dual confidence scoring (Positive, Negative, Uncertainty)."""

    def analyze(self, evidence_list: list[Evidence]) -> ConstraintEvidence:
        """
        Aggregates multiple pieces of evidence into a single ConstraintEvidence object.
        Uses Bayesian-like updates for confidence.
        """
        if not evidence_list:
            return ConstraintEvidence("N/A", "No evidence", 0.0, "index", 0.0, 0.0, 1.0)

        # Weighted aggregate
        pos_scores = []
        neg_scores = []
        weights = []

        for ev in evidence_list:
            weight = ev.strength * ev.type.reliability_score()
            weights.append(weight)
            if ev.sentiment >= 0:
                pos_scores.append(ev.sentiment * weight)
                neg_scores.append(0.0)
            else:
                pos_scores.append(0.0)
                neg_scores.append(abs(ev.sentiment) * weight)

        total_weight = sum(weights) or 1.0
        conf_pos = sum(pos_scores) / total_weight
        conf_neg = sum(neg_scores) / total_weight

        # Uncertainty is high if weights are low or evidence is conflicting
        conflict = 1.0 - abs(conf_pos - conf_neg) if (conf_pos > 0 and conf_neg > 0) else 0.0
        uncertainty = max(0.0, 1.0 - (total_weight / len(evidence_list)) + 0.5 * conflict)
        uncertainty = min(1.0, uncertainty)

        return ConstraintEvidence(
            source="Aggregated",
            citation=f"N={len(evidence_list)} sources",
            value=1.0,  # Resulting 'multiplier' or index
            unit="index",
            confidence_positive=float(conf_pos),
            confidence_negative=float(conf_neg),
            uncertainty=float(uncertainty),
        )


class EvidenceEvaluator:
    """Evaluates evidence quality and relevance (extracts from raw search results)."""

    def extract_from_raw(self, search_results: list[dict[str, Any]]) -> list[Evidence]:
        """
        Mock extraction of structured evidence from raw JSON search results.
        In production, this would call an LLM to parse the snippets.
        """
        evidence = []
        for res in search_results:
            snippet = res.get("snippet", "").lower()

            # Simple heuristic parser
            sentiment = 0.5
            if "crisis" in snippet or "failure" in snippet or "overwhelmed" in snippet:
                sentiment = -0.8
            elif "stable" in snippet or "improving" in snippet or "efficient" in snippet:
                sentiment = 0.8

            e_type = EvidenceType.ANECDOTAL
            if "report" in snippet or "data" in snippet:
                e_type = EvidenceType.EMPIRICAL
            elif "study" in snippet or "theory" in snippet:
                e_type = EvidenceType.THEORETICAL

            evidence.append(
                Evidence(
                    source=res.get("title", "Unknown"),
                    content=res.get("snippet", ""),
                    type=e_type,
                    strength=0.7,
                    sentiment=sentiment,
                )
            )
        return evidence


class EvidenceRequirements:
    """Defines evidence requirements for different constraint types."""

    @staticmethod
    def get_requirements(constraint_type: str) -> dict[str, Any]:
        reqs = {
            "capacity": {
                "min_sources": 3,
                "preferred_type": EvidenceType.EMPIRICAL,
                "freshness_years": 2,
            },
            "efficiency": {
                "min_sources": 2,
                "preferred_type": EvidenceType.THEORETICAL,
                "freshness_years": 5,
            },
        }
        return reqs.get(
            constraint_type,
            {"min_sources": 1, "preferred_type": EvidenceType.ANECDOTAL, "freshness_years": 10},
        )
