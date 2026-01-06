"""Checks codebase for usage of glossary terms."""

import sys
from pathlib import Path


def parse_glossary_mapping(glossary_path):
    """Parses the Parameter Mapping table from the glossary markdown."""
    mappings = {}
    with open(glossary_path) as f:
        lines = f.readlines()

    in_table = False
    for line in lines:
        if "Parameter Mapping" in line:
            in_table = True
            continue
        if (
            in_table
            and line.strip().startswith("|")
            and not line.strip().startswith("| Manuscript")
        ):
            # Skip header and separator
            if "---" in line:
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                # parts[0] is empty (before first |), parts[1] is symbol, parts[2] is code var
                code_vars = parts[2]
                # Handle multiple vars like `var1` / `var2`
                clean_vars = [v.strip(" `") for v in code_vars.split("/")]
                mappings[parts[1]] = clean_vars
    return mappings


def check_code_usage(root_dir, variables):
    """Checks if variables exist in the codebase."""
    found = dict.fromkeys(variables, False)
    src_path = Path(root_dir) / "src"

    for py_file in src_path.rglob("*.py"):
        with open(py_file) as f:
            content = f.read()
            for var in variables:
                if not found[var] and var in content:
                    found[var] = True

    return found


def main() -> None:
    """Scan src/ for glossary variables."""
    project_root = Path(__file__).parent.parent
    glossary_path = project_root / "context/08_glossary_abbreviations.md"

    if not glossary_path.exists():
        print(f"Error: Glossary not found at {glossary_path}")
        sys.exit(1)

    mappings = parse_glossary_mapping(glossary_path)
    all_vars = []
    for v_list in mappings.values():
        all_vars.extend(v_list)

    print(f"Checking {len(all_vars)} glossary variables against codebase...")

    found_status = check_code_usage(project_root, all_vars)

    missing = [v for v, f in found_status.items() if not f]

    if missing:
        print("\n[FAIL] The following glossary variables were NOT found in src/:")
        for v in missing:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All glossary variables verified in codebase.")
        sys.exit(0)


if __name__ == "__main__":
    main()
