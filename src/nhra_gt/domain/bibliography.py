"""Bibliography and Citation Management.

Handles parsing and exporting references in multiple formats (RIS, BibTeX, ENW).
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel


class Reference(BaseModel):
    """Pydantic model for an academic reference."""

    record_number: int
    label: str
    author: str
    year: int
    title: str
    journal: str | None = None
    volume: str | None = None
    issue: str | None = None
    pages: str | None = None
    doi: str | None = None
    url: str | None = None
    publisher: str | None = None
    access_date: str | None = None


def parse_endnote_token(token: str) -> dict[str, Any]:
    """Parses {Author, YYYY @Label #RecordNumber} tokens.

    Example: {Australian Institute of Health and Welfare, 2024 @AIHW_MyHospitals #101}
    """
    # Regex pattern to match the components
    # { (Author) , (Year) @(Label) #(RecordNumber) }
    pattern = r"\{(.+?),\s*(\d{4})\s*@(\w+)\s*#(\d+)\}"

    match = re.search(pattern, token)
    if not match:
        raise ValueError(f"Invalid Endnote token format: {token}")

    author, year, label, record_num = match.groups()

    return {
        "author": author.strip(),
        "year": int(year),
        "label": label.strip(),
        "record_number": int(record_num),
    }


class BibliographyManager:
    """Manages a collection of academic references and exports to various formats."""

    def __init__(self) -> None:
        """Initialize an empty bibliography manager."""
        self.references: dict[int, Reference] = {}

    def add_reference(self, ref: Reference) -> None:
        """Add a reference to the collection."""
        self.references[ref.record_number] = ref

    def to_ris(self) -> str:
        """Export to Research Information Systems (RIS) format."""
        lines = []
        for ref in self.references.values():
            lines.append("TY  - JOUR")
            lines.append(f"ID  - {ref.label}")
            lines.append(f"AU  - {ref.author}")
            lines.append(f"PY  - {ref.year}")
            lines.append(f"TI  - {ref.title}")
            if ref.journal:
                lines.append(f"JO  - {ref.journal}")
            if ref.volume:
                lines.append(f"VL  - {ref.volume}")
            if ref.issue:
                lines.append(f"IS  - {ref.issue}")
            if ref.pages:
                sp, ep = ref.pages.split("-") if "-" in ref.pages else (ref.pages, "")
                lines.append(f"SP  - {sp}")
                lines.append(f"EP  - {ep}")
            if ref.doi:
                lines.append(f"DO  - {ref.doi}")
            if ref.url:
                lines.append(f"UR  - {ref.url}")
            lines.append("ER  - ")
            lines.append("")
        return "\n".join(lines)

    def to_enw(self) -> str:
        """Export to EndNote (ENW) format."""
        lines = []
        for ref in self.references.values():
            lines.append("%0 Journal Article")
            lines.append(f"%A {ref.author}")
            lines.append(f"%D {ref.year}")
            lines.append(f"%T {ref.title}")
            if ref.journal:
                lines.append(f"%J {ref.journal}")
            if ref.volume:
                lines.append(f"%V {ref.volume}")
            if ref.issue:
                lines.append(f"%N {ref.issue}")
            if ref.pages:
                lines.append(f"%P {ref.pages}")
            if ref.doi:
                lines.append(f"%R {ref.doi}")
            if ref.url:
                lines.append(f"%U {ref.url}")
            lines.append(f"%F {ref.label}")
            lines.append(f"%M {ref.record_number}")
            lines.append("")
        return "\n".join(lines)

    def to_bibtex(self) -> str:
        """Export to BibTeX format."""
        lines = []
        for ref in self.references.values():
            lines.append(f"@article{{{ref.label},")
            lines.append(f"  author = {{{ref.author}}},")
            lines.append(f"  year = {{{ref.year}}},")
            lines.append(f"  title = {{{ref.title}}},")
            if ref.journal:
                lines.append(f"  journal = {{{ref.journal}}},")
            if ref.volume:
                lines.append(f"  volume = {{{ref.volume}}},")
            if ref.issue:
                lines.append(f"  number = {{{ref.issue}}},")
            if ref.pages:
                lines.append(f"  pages = {{{ref.pages}}},")
            if ref.doi:
                lines.append(f"  doi = {{{ref.doi}}},")
            if ref.url:
                lines.append(f"  url = {{{ref.url}}}")
            lines.append("}")
            lines.append("")
        return "\n".join(lines)
