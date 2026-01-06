# Plan: Streamlit Cloud Stabilization & Optimization

## CI-Relevant Commands

- `just lint`
- `just type`
- `just test`
- `just docs`

## Phase 1: Build Time Optimization (The "19-Minute" Problem)

The goal is to reduce deployment time by removing heavy system dependencies.

- [x] **Automated Verification Setup**: Create `tests/verify_headless_gambit.py` to assert `pygambit` works without X11.
- [x] **Prune System Packages**: Rename `packages.txt` to `packages.txt.bak` (effectively removing it).
- [x] **Trigger Build**: Push changes to trigger a new Streamlit Cloud build.
- [x] **Wait for Build**: (Agent pauses until build completes).
- [x] **Automated Build Verification**: Run `tests/verify_headless_gambit.py` locally and check remote logs.
- [x] **Phase Gate**: Recheck Phase 1 deliverables against tasks before testing.
- [x] **Phase Gate**: Run CI-relevant tests for build-time changes; fix failures before Phase 2.

## Phase 2: Observability & Runtime Stability

Ensure we know what runs and that it doesn't crash.

- [x] **UI Version Badge**: Add sidebar element in `dashboard.py` displaying Git Commit Hash (loaded from `version.txt` or env).
- [x] **Comprehensive Fallback Audit**: Scan `scripts/dashboard.py` for all column access and guard unsafe accesses.
- [x] **Deploy Fixes**: Push changes.
- [x] **Automated Health Check**: Create and run `scripts/verify_remote_health.py` (polls `/_stcore/health` and checks page title).
- [x] **Phase Gate**: Recheck Phase 2 deliverables against tasks before testing.
- [x] **Phase Gate**: Run CI-relevant tests for observability changes; fix failures before Phase 3.

## Phase 3: Final Integration

- [x] **Final Automated Sweep**: Run `tests/e2e/test_scenarios.py` locally and `scripts/verify_remote_health.py` remotely.
- [x] **Cleanup**: Delete `packages.txt.bak` if build succeeds.sful.
- [x] **Phase Gate**: Recheck Phase 3 deliverables against tasks before testing.
- [x] **Remote E2E (Streamlit Cloud)**: Add a Playwright-based smoke suite that targets the deployed Streamlit URL for critical flows; gate with env var/secret so it can run in CI.
- [x] **Track Gate**: Run full CI; monitor GitHub Actions with `gh` until green; fix any failures.
- [x] **Track Gate**: Verify Streamlit Cloud deployment health and key flows after CI passes.
- [x] **Track Gate**: Reconcile completed work against `spec.md` and record any deviations.
- [x] **Track Gate**: Evaluate the `spec.md` acceptance checklist and record pass/fail.
