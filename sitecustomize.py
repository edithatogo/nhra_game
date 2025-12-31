"""Runtime compatibility patches for CI environments.

This module is automatically imported by Python (via `site`) when present on
`sys.path`. We use it to smooth over small dependency API differences that can
otherwise break tooling like Snakemake in some environments (notably Windows).
"""

from __future__ import annotations


def _patch_pulp() -> None:
    try:
        import pulp  # type: ignore
    except Exception:
        return

    if not hasattr(pulp, "list_solvers") and hasattr(pulp, "listSolvers"):
        pulp.list_solvers = pulp.listSolvers  # type: ignore[attr-defined]


_patch_pulp()
