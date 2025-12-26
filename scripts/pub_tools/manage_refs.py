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

from datetime import datetime

def validate_recency(references: List[Dict[str, Any]], max_age_years: int = 10) -> bool:
    """
    Checks if references are within the specified age limit.
    Returns True if all references are recent (or have no year), False if any are too old.
    Note: This is a warning check, usually it shouldn't block the process, but we return False to indicate potential issues.
    """
    current_year = datetime.now().year
    all_recent = True
    
    for ref in references:
        ref_id = ref.get("id", "Unknown ID")
        year = ref.get("issued", {}).get("year") # Assuming CSL-JSON structure or similar where year might be nested
        
        # Fallback if year is top-level (common in simple yamls)
        if not year:
            year = ref.get("year")

        if year:
            try:
                year_int = int(year)
                age = current_year - year_int
                if age > max_age_years:
                    logging.warning(f"Reference '{ref_id}' is {age} years old (Year: {year}). Threshold is {max_age_years}.")
                    all_recent = False
            except ValueError:
                logging.warning(f"Reference '{ref_id}' has invalid year format: {year}")
        else:
             logging.info(f"Reference '{ref_id}' has no year specified. Skipping recency check.")

    return all_recent

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_refs.py <path_to_references.yaml>")
        sys.exit(1)

    ref_file = sys.argv[1]
    refs = load_references(ref_file)
    
    if not refs:
        logging.warning("No references found or file is empty.")
        sys.exit(0)

    metadata_valid = validate_metadata(refs)
    recency_valid = validate_recency(refs)

    if metadata_valid:
        logging.info("Metadata validation passed.")
    else:
        logging.error("Metadata validation failed.")

    if recency_valid:
        logging.info("Recency check passed.")
    else:
        logging.warning("Recency check flagged some older references.")

    if not metadata_valid:
        sys.exit(1)
    
    sys.exit(0)
