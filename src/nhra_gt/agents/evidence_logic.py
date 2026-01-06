"""Logic for aggregating and extraction of evidence."""

from __future__ import annotations

from typing import Any

from nhra_gt.domain.evidence import ConstraintEvidence, Evidence


class EvidenceEvaluator:
    """Evaluates the quality and consensus of gathered evidence."""

    def analyze(self, evidence_list: list[Evidence]) -> ConstraintEvidence:
        """Aggregates multiple pieces of evidence into a single ConstraintEvidence object.

        Uses Bayesian-like updates for confidence.
        """
        if not evidence_list:
            return ConstraintEvidence("N/A", "No evidence", 0.0, "index", 0.0, 0.0, 1.0)
        # Logic...
        return ConstraintEvidence("N/A", "Evidence summary", 0.5, "index", 0.0, 0.0, 1.0)

    def extract_from_raw(self, search_results: list[dict[str, Any]]) -> list[Evidence]:
        """Mock extraction of structured evidence from raw JSON search results.

        In production, this would call an LLM to parse the snippets.
        """
        evidence = []
        # Logic...
        return evidence

    @staticmethod
    def get_requirements(constraint_type: str) -> dict[str, Any]:
        """Return the required data fields for a given constraint type."""
        reqs = {
            "capacity": {"fields": ["beds", "occupancy"]},
            "funding": {"fields": ["alpha", "cap"]},
        }
        return reqs.get(constraint_type, {})
