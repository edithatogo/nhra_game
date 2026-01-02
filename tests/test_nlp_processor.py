import pytest
from nhra_gt.nlp.processor import EvidenceProcessor

def test_evidence_processor_basic():
    processor = EvidenceProcessor()
    text = "The Federal government provides funding for public hospitals under the NHRA cap."
    result = processor.parse_text(text)
    
    assert result["token_count"] > 0
    assert result["sentence_count"] == 1
    # Check if 'funding' or 'cap' was identified as keyword
    assert any(k in result["keywords"] for k in ["funding", "cap"])
    
def test_evidence_processor_entities():
    processor = EvidenceProcessor()
    text = "IHACPA sets the NEP for 2025."
    result = processor.parse_text(text)
    
    # SpaCy should find IHACPA or NEP or 2025 as entities
    assert len(result["entities"]) >= 1
    labels = [e["label"] for e in result["entities"]]
    assert "DATE" in labels or "ORG" in labels
