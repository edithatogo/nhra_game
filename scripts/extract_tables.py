from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


class PDFTableExtractor:
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        
    def get_hash(self) -> str:
        """Calculate SHA-256 hash of the PDF file."""
        sha256_hash = hashlib.sha256()
        with open(self.pdf_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
        
    def extract_raw_tables(self) -> list[Any]:
        """Extract tables from the PDF.
        
        Note: Actual implementation would use Camelot or PyMuPDF.
        For now, returns a list to satisfy the interface.
        """
        # In a real implementation, we'd use:
        # import camelot
        # tables = camelot.read_pdf(str(self.pdf_path))
        # return [t.df for t in tables]
        return []
