# Plan: CI Fix and DISC Re-integration

## Goals
1. Commit and push all current changes once `mkdocs build` completes.
2. Monitor GitHub Actions for the deploy workflow.
3. Iteratively fix any CI errors and push again until the workflow passes.
4. Re-add `discharge_coordination_game` (DISC) to the current `HeuristicAgent` in `agents/base.py`.

---

## Step 1: Commit and Push
- Wait for `mkdocs build` to finish.
- Run `git add .` and `git commit -m "chore: cleanup and simplify docs workflow"`.
- Run `git push`.

## Step 2: Monitor Remote
- Check GitHub Actions status using the browser or CLI:
  ```bash
  gh run list --limit 3
  ```
- If actions fail, retrieve logs:
  ```bash
  gh run view <RUN_ID> --log-failed
  ```

## Step 3: Fix Errors (Iterative)
- Common expected issues:
  - Missing dependencies in `pip install` (add to workflow).
  - Missing docs files referenced in `mkdocs.yml`.
  - Linting/type errors from code changes.
- Fix the issue, commit, push, and re-check.

## Step 4: Re-add DISC to `HeuristicAgent`
- **File**: `src/nhra_game_theory/agents/base.py` (or current package path).
- **Changes**:
  1. Import `discharge_coordination_game` from `subgames.games`.
  2. Add `DISC` to the `games_to_play` list and `play_order`.
  3. Add the solve logic:
     ```python
     elif g == "DISC":
         r_disc, c_disc = _solve(discharge_coordination_game(gp))
         results["DISC"] = "C" if (r_disc == "C" and c_disc == "C") else "F"
     ```
  4. Add heuristic fallback for non-equilibrium mode.

## Step 5: Final Verification
- Run `mkdocs build` locally.
- Push and confirm CI passes.

---

## User Review Required
> [!IMPORTANT]
> The `nhra_gt/` package appears to have been deleted. Please confirm the current package name/path for the code edits in Step 4.
