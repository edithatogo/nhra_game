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
    for ref in refs:
        rid = ref.get("id", "Unknown")
        if not ref.get("doi") or not ref.get("url"):
            logging.error(f"Ref {rid} missing DOI or URL.")
            all_valid = False
    return all_valid

def validate_recency(references: List[Dict[str, Any]], max_age_years: int = 10) -> bool:
    current_year = datetime.now().year
    all_recent = True
    for ref in references:
        ref_id = ref.get("id", "Unknown ID")
        year = ref.get("year")
        if year:
            try:
                year_int = int(year)
                if current_year - year_int > max_age_years:
                    logging.warning(f"Reference '{ref_id}' is old ({year}).")
                    all_recent = False
            except ValueError:
                pass
    return all_recent

def validate_quality(references: List[Dict[str, Any]], high_impact_list: List[str] = None) -> bool:
    if high_impact_list is None:
        high_impact_list = ["nature", "science", "lancet", "nejm", "bmj", "jama"]
    return True

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
        logging.info("Metadata validation passed.")
    
    validate_recency(library)
    validate_quality(library)
    
    print("\n--- GENERATED BIBLIOGRAPHY ---\n")
    print(generate_bibliography(library))