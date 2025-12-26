import yaml
import sys
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def load_references(file_path: str) -> List[Dict[str, Any]]:
    """Loads references from a YAML file."""
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return []
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        return []

def validate_metadata(references: List[Dict[str, Any]]) -> bool:
    """
    Validates that each reference has a DOI and a URL.
    Returns True if all references are valid, False otherwise.
    """
    all_valid = True
    for ref in references:
        ref_id = ref.get("id", "Unknown ID")
        
        # Check for DOI
        if "doi" not in ref or not ref["doi"]:
            logging.error(f"Reference '{ref_id}' is missing a DOI.")
            all_valid = False
            
        # Check for URL
        if "url" not in ref or not ref["url"]:
            logging.error(f"Reference '{ref_id}' is missing a URL.")
            all_valid = False
            
    return all_valid

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_refs.py <path_to_references.yaml>")
        sys.exit(1)

    ref_file = sys.argv[1]
    refs = load_references(ref_file)
    
    if not refs:
        logging.warning("No references found or file is empty.")
        sys.exit(0)

    if validate_metadata(refs):
        logging.info("All references passed metadata validation.")
        sys.exit(0)
    else:
        logging.error("Some references failed metadata validation.")
        sys.exit(1)
