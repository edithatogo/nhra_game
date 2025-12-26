# Task: CI Fix and DISC Re-integration

## 1. Initial Commit & Push `[git]`
- [x] Commit current changes <!-- id: 1 -->
- [ ] Push to remote <!-- id: 2 -->

## 2. Monitor CI `[ci]` (Iterative)
- [ ] Check GitHub Actions status <!-- id: 10 -->
- [ ] If failed, retrieve logs <!-- id: 11 -->
- [ ] Fix error <!-- id: 12 -->
- [ ] Commit and push fix <!-- id: 13 -->
- [ ] Repeat until CI passes <!-- id: 14 -->

## 3. Re-add DISC Game `[backend]`
- [ ] Update `src/nhra_game_theory/agents/base.py` <!-- id: 20 -->
  - [ ] Import `discharge_coordination_game` from `subgames.games`
  - [ ] Add "DISC" to `play_order`
  - [ ] Add equilibrium solve logic for DISC
  - [ ] Add heuristic fallback for DISC

## 4. Final Verification `[test]`
- [ ] Run `mkdocs build` locally <!-- id: 30 -->
- [ ] Commit and push <!-- id: 31 -->
- [ ] Confirm CI passes <!-- id: 32 -->
