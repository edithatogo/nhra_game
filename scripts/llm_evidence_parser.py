from __future__ import annotations

from typing import Any

from nhra_gt.domain.registry import EvidenceEntry


class LLMEvidenceExtractor:
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name

    def _call_llm(self, raw_text: str) -> dict[str, Any]:
        """Internal method to call the LLM API.

        Note: In production, this would use an actual LLM client.
        For this track, it's designed to be mocked in tests.
        """
        # Placeholder for real API call
        return {}

    def parse_evidence(self, raw_text: str) -> EvidenceEntry:
        """Parses raw text into an EvidenceEntry using an LLM."""
        response = self._call_llm(raw_text)

        # Schema enforcement
        return EvidenceEntry(
            parameter=str(response["parameter"]),
            mean=float(response["mean"]),
            lower_ci=float(response["lower_ci"]) if "lower_ci" in response else None,
            upper_ci=float(response["upper_ci"]) if "upper_ci" in response else None,
            nhmrc_level=str(response.get("nhmrc_level", "IV")),
        )
