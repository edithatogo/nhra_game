from __future__ import annotations

from typing import Any

from nhra_gt.agents.evidence_logic import EvidenceAnalyzer, EvidenceEvaluator
from nhra_gt.domain.evidence import ConstraintEvidence
from nhra_gt.domain.registry import EvidenceEntry


class LLMEvidenceExtractor:
    """
    Real-world implementation of an Evidence Parser.
    Converts raw text/reports into structured EvidenceEntry objects for the model registry.
    """

    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        self.evaluator = EvidenceEvaluator()
        self.analyzer = EvidenceAnalyzer()

    def _call_llm_structured(self, raw_text: str) -> dict[str, Any]:
        """
        Simulates a structured LLM call (e.g. via Instructor or Outlines).
        Parses raw text into intermediate JSON.
        """
        # In a real environment, this would call LiteLLM or similar.
        # Here we use heuristic extraction to enable the pipeline.
        text = raw_text.lower()

        # Heuristic parameter detection
        param = "unknown"
        if "within 4" in text or "ed wait" in text:
            param = "within4_base"
        elif "occupancy" in text:
            param = "occupancy_base"
        elif "cost shifting" in text:
            param = "cost_shifting_intensity"

        # Heuristic value detection (look for decimals or percentages)
        import re

        matches = re.findall(r"(\d+\.?\d*)%", text)
        val = 0.5
        if matches:
            val = float(matches[0]) / 100.0
        else:
            matches = re.findall(r"\b0\.\d+\b", text)
            if matches:
                val = float(matches[0])

        return {
            "parameter": param,
            "mean": val,
            "lower_ci": val * 0.9,
            "upper_ci": val * 1.1,
            "nhmrc_level": "II" if "report" in text else "IV",
        }

    def _call_llm(self, raw_text: str) -> dict[str, Any]:
        """Backward-compatible hook for tests/mocking."""
        return self._call_llm_structured(raw_text)

    def parse_evidence(self, raw_text: str) -> EvidenceEntry:
        """Parses raw text into an EvidenceEntry using structured extraction."""
        response = self._call_llm(raw_text)

        # Schema enforcement
        return EvidenceEntry(
            parameter=str(response["parameter"]),
            mean=float(response["mean"]),
            lower_ci=float(response["lower_ci"]) if "lower_ci" in response else None,
            upper_ci=float(response["upper_ci"]) if "upper_ci" in response else None,
            nhmrc_level=str(response.get("nhmrc_level", "IV")),
        )

    def extract_and_analyze(self, raw_text: str) -> ConstraintEvidence:
        """
        Full pipeline: Raw Text -> Evidence List -> Aggregated ConstraintEvidence.
        """
        # 1. 'Extract' by splitting into sentences as pseudo-sources
        parts = raw_text.split(". ")
        mock_results = [{"title": f"Fragment {i}", "snippet": p} for i, p in enumerate(parts)]

        # 2. Evaluate quality
        evidence_list = self.evaluator.extract_from_raw(mock_results)

        # 3. Analyze confidence
        return self.analyzer.analyze(evidence_list)
