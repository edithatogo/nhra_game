"""Compiles the project glossary from context documentation."""

from pathlib import Path


def build_glossary() -> None:
    """Parse glossary markdown and generate documentation."""
    source_path = Path("context/08_glossary_abbreviations.md")
    target_path = Path("docs_mkdocs/guides/glossary.md")
    if not source_path.exists():
        print("Glossary source not found.")
        return

    content = source_path.read_text(encoding="utf-8")

    # Simple transformation for now
    output = "# Glossary and Abbreviations\n\n"
    output += "This glossary is compiled from the project context files.\n\n"
    output += content

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(output)
    print(f"Glossary built: {target_path}")


if __name__ == "__main__":
    build_glossary()
