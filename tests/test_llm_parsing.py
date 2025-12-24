from __future__ import annotations

import pytest

# Implementation will be in a new module
from scripts.llm_evidence_parser import LLMEvidenceExtractor


def test_llm_parsing_to_schema(mocker):
    """Verify that the LLM parser maps raw text to the EvidenceEntry schema."""
    raw_text = "Table 1 shows ED performance was 53% (95% CI: 51-55%) across Australia."

    # Mock LLM response
    mock_response = {
        "parameter": "within4_base",
        "mean": 0.53,
        "lower_ci": 0.51,
        "upper_ci": 0.55,
        "nhmrc_level": "III-2",
    }

    extractor = LLMEvidenceExtractor()
    # Mock the internal call to the LLM
    mocker.patch.object(extractor, "_call_llm", return_value=mock_response)

    entry = extractor.parse_evidence(raw_text)

    assert entry.parameter == "within4_base"
    assert entry.mean == 0.53
    assert entry.lower_ci == 0.51
    assert entry.nhmrc_level == "III-2"


def test_llm_parsing_invalid_schema(mocker):
    """Verify that the parser handles malformed LLM responses."""
    raw_text = "Invalid data"
    mock_response = {"incomplete": "data"}

    extractor = LLMEvidenceExtractor()
    mocker.patch.object(extractor, "_call_llm", return_value=mock_response)

    with pytest.raises(KeyError):
        extractor.parse_evidence(raw_text)


def test_internal_call_llm_placeholder():
    """Verify that the placeholder internal method returns an empty dict."""
    extractor = LLMEvidenceExtractor()
    assert extractor._call_llm("test") == {}
