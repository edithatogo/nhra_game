import ast
import os
from pathlib import Path

def get_logic_map(file_path):
    """Extracts function and class names from a Python file AST."""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "r") as f:
        try:
            tree = ast.parse(f.read())
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
            
    logic = {"functions": [], "classes": {}}
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            logic["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            class_methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            logic["classes"][node.name] = class_methods
            
    return logic

def compare_logic(legacy_path, current_path):
    """Compares legacy vs current logic and identifies missing components."""
    legacy = get_logic_map(legacy_path)
    current = get_logic_map(current_path)
    
    if not legacy or not current:
        return None
        
    missing = {"functions": [], "classes": {}, "methods": {}}
    
    # Check functions
    for func in legacy["functions"]:
        if func not in current["functions"]:
            missing["functions"].append(func)
            
    # Check classes
    for cls, methods in legacy["classes"].items():
        if cls not in current["classes"]:
            missing["classes"][cls] = methods
        else:
            # Check methods
            for method in methods:
                if method not in current["classes"][cls]:
                    if cls not in missing["methods"]:
                        missing["methods"][cls] = []
                    missing["methods"][cls].append(method)
                    
    return missing

def main():
    current_v9 = "src/nhra_game_theory/v9.py"
    legacy_roots = [
        ".gemini/tmp/audit/v1",
        ".gemini/tmp/audit/v5",
        ".gemini/tmp/audit/v9",
        ".gemini/tmp/audit/v15",
        ".gemini/tmp/audit/v19"
    ]
    
    report = ["# Forensic Feature Audit Report (AST Comparison)\n"]
    report.append(f"**Current Reference:** `{current_v9}`\n")
    
    found_any = False
    
    for root in legacy_roots:
        # Look for the main model file in the legacy root
        # It might be named differently (e.g. nhra_hybrid_v5.py)
        legacy_files = list(Path(root).rglob("*.py"))
        
        for leg_file in legacy_files:
            # Skip non-model files (like setup.py, tests, etc)
            if any(x in leg_file.name for x in ["test", "setup", "conftest", "__init__"]):
                continue
                
            res = compare_logic(leg_file, current_v9)
            if res and (res["functions"] or res["classes"] or res["methods"]):
                found_any = True
                report.append(f"## Legacy File: `{leg_file}`")
                
                if res["functions"]:
                    report.append("### Missing Functions")
                    for f in res["functions"]:
                        report.append(f"- `{f}`")
                        
                if res["classes"]:
                    report.append("### Missing Classes")
                    for c, m in res["classes"].items():
                        report.append(f"- `{c}` (Methods: {', '.join(m)})")
                        
                if res["methods"]:
                    report.append("### Missing Methods in Existing Classes")
                    for c, m in res["methods"].items():
                        report.append(f"- `{c}`: {', '.join(m)}")
                
                report.append("\n")
                
    if not found_any:
        report.append("No missing logic detected between legacy versions and current `v9.py`.")
        
    out_path = Path("reports/lost_features_audit.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(report))
        
    print(f"Audit report generated at {out_path}")

if __name__ == "__main__":
    main()
