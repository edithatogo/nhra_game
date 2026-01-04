# Plan: Streamlit Cloud Stabilization & Optimization

## Phase 1: Build Time Optimization (The "19-Minute" Problem)

The goal is to reduce deployment time by removing heavy system dependencies.

- [x] **Automated Verification Setup**: Create `tests/verify_headless_gambit.py` to assert `pygambit` works without X11.
- [x] **Prune System Packages**: Rename `packages.txt` to `packages.txt.bak` (effectively removing it).
- [x] **Trigger Build**: Push changes to trigger a new Streamlit Cloud build.
- [ ] **Wait for Build**: (Agent pauses until build completes).
- [ ] **Automated Build Verification**: Run `tests/verify_headless_gambit.py` locally and check remote logs.

## Phase 2: Observability & Runtime Stability

Ensure we know what runs and that it doesn't crash.

- [x] **UI Version Badge**: Add sidebar element in `dashboard.py` displaying Git Commit Hash (loaded from `version.txt` or env).
- [x] **Comprehensive Fallback Audit**: Scan `scripts/dashboard.py` for all column access and guard unsafe accesses.
- [x] **Deploy Fixes**: Push changes.
- [x] **Automated Health Check**: Create and run `scripts/verify_remote_health.py` (polls `/_stcore/health` and checks page title).

## Phase 3: Final Integration

- [x] **Final Automated Sweep**: Run `tests/e2e/test_scenarios.py` locally and `scripts/verify_remote_health.py` remotely.
- [x] **Cleanup**: Delete `packages.txt.bak` if build succeeds.sful.
