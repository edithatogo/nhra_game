from __future__ import annotations

from nhra_gt.domain.evidence import EvidenceType
from scripts.llm_evidence_parser import LLMEvidenceExtractor


def test_evidence_parsing_basic():
    parser = LLMEvidenceExtractor()
    report_text = "The AIHW report indicates that ED within 4 hour performance has dropped to 55%."

    entry = parser.parse_evidence(report_text)

    assert entry.parameter == "within4_base"
    assert entry.mean == 0.55
    assert entry.nhmrc_level == "II"


def test_evidence_analysis_pipeline():
    parser = LLMEvidenceExtractor()
    raw_input = "Hospital occupancy is at 98%. System stability is improving. Recent data confirms a crisis in staffing."

    agg_evidence = parser.extract_and_analyze(raw_input)

    # Check dual confidence scores
    assert agg_evidence.confidence_positive >= 0.0
    assert agg_evidence.confidence_negative >= 0.0
    assert agg_evidence.uncertainty <= 1.0
    assert "N=3 sources" in agg_evidence.citation


def test_evidence_type_reliability():
    assert EvidenceType.EMPIRICAL.reliability_score() == 0.95
    assert EvidenceType.ANECDOTAL.reliability_score() == 0.30
