import spacy
from typing import List, Dict, Any
from pathlib import Path
from beartype import beartype

class EvidenceProcessor:
    """Standardized NLP interface for processing policy evidence."""
    
    def __init__(self, model: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            # Fallback or strict error depending on requirements
            # For now, suggest download
            raise RuntimeError(f"SpaCy model '{model}' not found. Run 'python -m spacy download {model}'")

    @beartype
    def parse_text(self, text: str) -> Dict[str, Any]:
        """Parses text to extract entities and key phrases."""
        doc = self.nlp(text)
        
        entities = [
            {"text": ent.text, "label": ent.label_}
            for ent in doc.ents
        ]
        
        # Basic keyword extraction (noun chunks)
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        
        return {
            "entities": entities,
            "noun_chunks": noun_chunks,
            "tokens": [token.text for token in doc]
        }

    @beartype
    def process_file(self, path: Path | str) -> Dict[str, Any]:
        """Reads and processes a text file."""
        text = Path(path).read_text(encoding="utf-8")
        return self.parse_text(text)
