# Plan: CI Fix, DISC Re-integration, and Publication Rigour
**Author:** Dylan A Mordaunt

## Goals
1. Commit and push all current changes once `mkdocs build` completes.
2. Monitor GitHub Actions for the deploy workflow.
3. Iteratively fix any CI errors and push again until the workflow passes.
4. Re-add `discharge_coordination_game` (DISC) to the current `HeuristicAgent` in `agents/base.py`.
5. **Elevate Publication Quality:** Expand manuscripts with rigorous research, recent high-quality references, and increased depth/length.

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
- **File**: `src/nhra_game_theory/agents/base.py` ✅ (Confirmed)
- **Games File**: `src/nhra_game_theory/subgames/games.py` ✅ (Confirmed)
- **Changes**:
  1. Import `discharge_coordination_game` from `subgames.games`.
  2. Add `DISC` to the `play_order` list.
  3. Add the solve logic:
     ```python
     elif g == "DISC":
         r_disc, c_disc = _solve(discharge_coordination_game(gp))
         results["DISC"] = "C" if (r_disc == "C" and c_disc == "C") else "F"
     ```
  4. Add heuristic fallback for non-equilibrium mode.

## Step 5: Publication Series Rigour (New)
- **Research Methods:**
    - [ ] Create `data/research/` directory.
    - [ ] Ingest user-provided PDFs.
    - [ ] Conduct literature search (Last 5 years, High Impact Journals).
- **Update References:**
    - [ ] Validate all references (DOI, Recency, Reality).
    - [ ] Ensure every claim is cited.
- **Expand Documents:**
    - [ ] Review current drafts against length/quality metrics.
    - [ ] Expand sections with deeper analysis and evidence.

## Step 6: Final Verification
- Run `mkdocs build` locally.
- Push and confirm CI passes.

---

## Recommended Improvements
1. **GitHub CLI (`gh`)**: Install `gh` CLI for faster CI monitoring instead of browser checks.
2. **Pre-commit bypass**: Use `--no-verify` for rapid iteration during CI debugging.
3. **Incremental Pushes**: Commit/push after each fix to see incremental CI results.

## [ ] Remediation: Implement Missing Features (from 2026 Audit)
- [ ] Task: Implement 'Public Health' funding stream in src/nhra_gt/rules.py and enable agent selection.
- [ ] Task: Formalize Audit 'Arms Race' feedback loop in src/nhra_gt/audit/fingerprint.py.
- [ ] Task: Add 'Mid-term Review' signal logic to the simulation orchestrator.
- [ ] Task: Model 'Dispute Resolution' and data matching business rules in the reconciliation loop.
- [ ] Task: Implement 'Equity' stratification for access and outcome metrics.
