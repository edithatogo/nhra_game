import os
from pathlib import Path

def fix_file(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'sys.path.append' in content:
        return # Already fixed
        
    # Find a good place to insert (after __future__ or at top)
    import_block = """import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))
"""
    
    if 'from __future__ import annotations' in content:
        new_content = content.replace('from __future__ import annotations', 'from __future__ import annotations\n\n' + import_block)
    else:
        new_content = import_block + '\n' + content
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Fixed {path}")

def main():
    dir_path = Path("scripts/reintroduced")
    for f in dir_path.glob("*.py"):
        if f.name != "fix_imports.py":
            fix_file(f)

if __name__ == "__main__":
    main()
