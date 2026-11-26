"""Hash source PDFs and retain the historical table-extraction interface."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


class PDFTableExtractor:
    """Identify a PDF by its bytes and expose its table-extraction interface."""

    def __init__(self, pdf_path: Path):
        """Keep the source path for hashing."""
        self.pdf_path = pdf_path

    def get_hash(self) -> str:
        """Calculate the SHA-256 hash of the source PDF."""
        with self.pdf_path.open("rb") as stream:
            return hashlib.file_digest(stream, "sha256").hexdigest()

    def extract_raw_tables(self) -> list[Any]:
        """Return the historical empty result for table extraction."""
        return []
