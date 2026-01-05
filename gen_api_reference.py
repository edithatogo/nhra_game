from __future__ import annotations

import importlib
import pkgutil
import sys
import traceback
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import mkdocs_gen_files


@dataclass(frozen=True)
class ModuleDoc:
    name: str
    importable: bool
    error_summary: str | None = None
    error_detail: str | None = None


def _try_import(name: str) -> tuple[bool, str | None, str | None]:
    try:
        importlib.import_module(name)
    except Exception as exc:
        summary = f"{type(exc).__name__}: {exc}"
        detail = traceback.format_exc()
        return False, summary, detail
    return True, None, None


def _iter_modules(package_name: str) -> list[str]:
    pkg = importlib.import_module(package_name)
    if not hasattr(pkg, "__path__"):
        return []
    names: list[str] = []
    for mod in pkgutil.walk_packages(pkg.__path__, prefix=f"{package_name}."):
        names.append(mod.name)
    return sorted(set(names))


def _write_module_page(module: ModuleDoc) -> None:
    rel_path = module.name.replace(".", "/") + ".md"
    doc_path = f"reference/api/{rel_path}"

    with mkdocs_gen_files.open(doc_path, "w") as fd:
        fd.write(f"# `{module.name}`\n\n")

        if module.importable:
            fd.write(f"::: {module.name}\n")
            fd.write("    options:\n")
            fd.write("      show_root_heading: false\n")
            fd.write("      members_order: source\n")
            return

        fd.write('!!! warning "Module not importable during docs build"\n')
        if module.error_summary:
            fd.write(f"    - Error: `{module.error_summary}`\n")
        fd.write("\n")
        if module.error_detail:
            fd.write("    <details>\n")
            fd.write("    <summary>Traceback</summary>\n\n")
            fd.write("    ```text\n")
            for line in module.error_detail.rstrip("\n").splitlines():
                fd.write(f"    {line}\n")
            fd.write("    ```\n\n")
            fd.write("    </details>\n")


def _write_index(modules: list[ModuleDoc]) -> None:
    by_group: defaultdict[str, list[ModuleDoc]] = defaultdict(list)
    for m in modules:
        group = m.name.split(".", 2)[1] if m.name.count(".") else m.name
        by_group[group].append(m)

    with mkdocs_gen_files.open("reference/api/index.md", "w") as fd:
        fd.write("# Full API Index\n\n")
        fd.write(
            "Auto-generated module reference for the `nhra_gt` package. "
            "Modules that cannot be imported in the docs build are listed with an error.\n\n"
        )

        total = len(modules)
        ok = sum(1 for m in modules if m.importable)
        fd.write(f"- Modules: **{ok} / {total} importable**\n\n")

        for group in sorted(by_group):
            fd.write(f"## `{group}`\n\n")
            for m in sorted(by_group[group], key=lambda x: x.name):
                rel = m.name.replace(".", "/") + ".md"
                status = "ok" if m.importable else "blocked"
                fd.write(f"- `{status}` [`{m.name}`]({rel})\n")
            fd.write("\n")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    src_root = repo_root / "src"
    sys.path.insert(0, str(src_root))

    module_names = _iter_modules("nhra_gt")
    modules: list[ModuleDoc] = []
    for name in module_names:
        ok, summary, detail = _try_import(name)
        modules.append(
            ModuleDoc(name=name, importable=ok, error_summary=summary, error_detail=detail)
        )
        _write_module_page(modules[-1])

    _write_index(modules)


main()
