from __future__ import annotations

import spacy
from typing import Dict, Any
from pathlib import Path
from beartype import beartype

class EvidenceProcessor:
    """Standardized NLP interface for processing policy evidence.
    
    This class uses SpaCy to extract entities, keywords, and structural
    patterns from policy documents to automate parameter grounding.
    """
    
    def __init__(self, model: str = "en_core_web_sm"):
        """Initializes the processor with a specific SpaCy model."""
        try:
            self.nlp = spacy.load(model)
        except OSError:
            raise RuntimeError(
                f"SpaCy model '{model}' not found. "
                f"Please run 'python -m spacy download {model}'"
            )

    @beartype
    def parse_text(self, text: str) -> Dict[str, Any]:
        """Parses text to extract entities and key phrases.
        
        Args:
            text: The raw text string to process.
            
        Returns:
            A dictionary containing entities, noun chunks, and token counts.
        """
        doc = self.nlp(text)
        
        entities = [
            {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
            for ent in doc.ents
        ]
        
        # Extract specific policy-relevant concepts (heuristic)
        keywords = [
            chunk.text.lower() for chunk in doc.noun_chunks 
            if any(term in chunk.text.lower() for term in ["funding", "cap", "audit", "nwau", "nep", "state", "federal"])
        ]
        
        return {
            "entities": entities,
            "noun_chunks": [chunk.text for chunk in doc.noun_chunks],
            "keywords": sorted(list(set(keywords))),
            "token_count": len(doc),
            "sentence_count": len(list(doc.sents))
        }

    @beartype
    def process_file(self, path: Path | str) -> Dict[str, Any]:
        """Reads and processes a text file.
        
        Args:
            path: Path to the text file.
            
        Returns:
            The parsed result dictionary.
        """
        text = Path(path).read_text(encoding="utf-8")
        return self.parse_text(text)