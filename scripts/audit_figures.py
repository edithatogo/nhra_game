import ast
import os
from pathlib import Path


def get_plotting_imports(tree: ast.AST) -> set[str]:
    """Identify aliases for plotting libraries."""
    aliases = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in [
                    "matplotlib.pyplot",
                    "plotly.graph_objects",
                    "plotly.express",
                    "seaborn",
                    "matplotlib.figure",
                ]:
                    aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module in [
            "matplotlib",
            "plotly",
            "seaborn",
        ]:
            for alias in node.names:
                aliases.add(alias.asname or alias.name)
    return aliases


def audit_file(filepath: Path) -> list[dict]:
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return []

    aliases = get_plotting_imports(tree)
    if not aliases and "plotting" not in filepath.name:
        # Double check if it uses 'plot' in function names even without imports (e.g. wrappers)
        pass

    findings = []

    # Check function definitions for 'plot' in name
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and (
            "plot" in node.name.lower()
            or "figure" in node.name.lower()
            or "chart" in node.name.lower()
        ):
            findings.append(
                {
                    "file": str(filepath),
                    "type": "definition",
                    "name": node.name,
                    "line": node.lineno,
                }
            )

    # Check for calls to plotting libraries
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id in aliases:
                    func_name = f"{node.func.value.id}.{node.func.attr}"
            elif isinstance(node.func, ast.Name) and node.func.id in aliases:
                func_name = node.func.id

            if func_name:
                findings.append(
                    {"file": str(filepath), "type": "usage", "name": func_name, "line": node.lineno}
                )

    return findings


def main():
    root_dir = Path(".")
    relevant_files = []

    # Scan src and scripts
    for path in [root_dir / "src", root_dir / "scripts"]:
        for r, _d, f in os.walk(path):
            for file in f:
                if file.endswith(".py"):
                    relevant_files.append(Path(r) / file)

    results = []
    for f in relevant_files:
        results.extend(audit_file(f))

    # Print Report
    print(f"Found {len(results)} potential plotting references.")

    # Group by file
    by_file = {}
    for r in results:
        by_file.setdefault(r["file"], []).append(r)

    for f, refs in by_file.items():
        print(f"\nFile: {f}")
        for r in refs:
            print(f"  - [{r['line']}] {r['type']}: {r['name']}")


if __name__ == "__main__":
    main()
