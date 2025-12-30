from __future__ import annotations

import re
from pathlib import Path


def build_glossary():
    source_path = Path("context/08_glossary_abbreviations.md")
    target_path = Path("docs_mkdocs/guides/glossary.md")

    if not source_path.exists():
        print("Glossary source not found.")
        return

    content = source_path.read_text()

    # Extract terms using regex: "- **TERM**: Description"
    terms = re.findall(r"- \*\*(.*?)\*\*: (.*)", content)

    output = "# Glossary & Abbreviations\n\n"
    output += "Definitions for key terms and acronyms used in the NHRA Game model.\n\n"

    for term, desc in terms:
        output += f"{term}\n: {desc}\n\n"

    target_path.write_text(output)
    print(f"Glossary built: {target_path}")


if __name__ == "__main__":
    build_glossary()
