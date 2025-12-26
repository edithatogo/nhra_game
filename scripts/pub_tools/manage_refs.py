import yaml
import sys
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def load_references(file_path: str) -> List[Dict[str, Any]]:
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        return []

def validate_references(refs: List[Dict[str, Any]]) -> bool:
    all_valid = True
    current_year = datetime.now().year
    
    for ref in refs:
        rid = ref.get("id", "Unknown")
        # Metadata check
        if not ref.get("doi") and not ref.get("url"):
            logging.error(f"Ref {rid} missing both DOI and URL.")
            all_valid = False
        
        # Recency check
        year = ref.get("year")
        if year and isinstance(year, int):
            if current_year - year > 10:
                logging.warning(f"Ref {rid} is old ({year}). Ensure it is seminal.")
        
        # Quality check (Heuristic)
        quality = ref.get("quality", "medium")
        if quality == "low":
            logging.warning(f"Ref {rid} flagged as low quality.")

    return all_valid

def generate_bibliography(refs: List[Dict[str, Any]]) -> str:
    """Generates a numbered Vancouver-style bibliography."""
    bib = ""
    for i, ref in enumerate(refs, 1):
        author = ref.get("author", "Unknown")
        year = ref.get("year", "n.d.")
        title = ref.get("title", "No Title")
        journal = ref.get("journal", ref.get("publisher", ""))
        doi = ref.get("doi", "")
        url = ref.get("url", "")
        
        bib += f"{i}. {author}. ({year}). {title}. *{journal}*."
        if doi: bib += f" DOI: {doi}"
        elif url: bib += f" Available at: {url}"
        bib += "\n"
    return bib

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage_refs.py <library.yaml>")
        sys.exit(1)
    
    library = load_references(sys.argv[1])
    if validate_references(library):
        logging.info("Reference validation passed.")
    
    print("\n--- GENERATED BIBLIOGRAPHY ---\\n")
    print(generate_bibliography(library))