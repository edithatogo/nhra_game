from __future__ import annotations

import ast
import sys
from pathlib import Path

def get_module_names(src_dir: Path) -> set[str]:
    """Extract sub-package names from src."""
    modules = set()
    package_root = src_dir / "nhra_game_theory"
    if not package_root.exists():
        return modules
        
    for item in package_root.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            modules.add(item.name)
        elif item.suffix == ".py" and item.name != "__init__.py":
            modules.add(item.stem)
    return modules

def verify_c4_components(engineering_md: Path, modules: set[str]) -> bool:
    """Verify that C4 Component diagram mentions existing modules."""
    if not engineering_md.exists():
        print(f"Warning: {engineering_md} not found.")
        return True
        
    content = engineering_md.read_text()
    missing = []
    for mod in modules:
        # Simple check: module name should be in the file
        if mod.lower() not in content.lower():
            missing.append(mod)
            
    if missing:
        print(f"Drift Detected! The following modules are missing from C4 diagrams: {missing}")
        return False
    
    print("C4 Components verified against source structure.")
    return True

def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    eng_md = repo_root / "docs/diagrams/engineering_diagrams.md"
    
    modules = get_module_names(src_dir)
    success = verify_c4_components(eng_md, modules)
    
    if not success:
        sys.exit(1)
    
    print("Documentation verification successful.")

if __name__ == "__main__":
    main()
