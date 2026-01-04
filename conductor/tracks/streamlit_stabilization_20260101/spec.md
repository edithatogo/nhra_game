# Track Specification: Streamlit Cloud Stabilization & Optimization

## 1. Overview

**Goal**: Stabilize the Streamlit Cloud deployment by resolving runtime crashes and optimizing the build process to reduce deployment time.
**Context**: The application crashes on Streamlit Cloud due to missing column errors. Build time is excessive (`~20m`) due to `packages.txt` installing the full X11 stack.
**Constraint**: All verification MUST be automated. No manual review steps.

## 2. Functional Requirements

- **Runtime Stability**: The application MUST NOT crash on startup or navigation.
- **Data Handling**: Gracefully handle missing `suspicion_mean` / `pressure_active_mean` columns.
- **Health Check**: The application MUST pass the Streamlit health check (`/_stcore/health`) and defined E2E scenarios.

## 3. Non-Functional Requirements

- **Build Time Optimization**: Remove `packages.txt` and rely on `pygambit` wheels or minimal binaries to achieve < 5 min builds.
- **Observability**: Display Git Commit Hash in the UI (sidebar) for automated version verification.
- **Automation**: All verification steps (build success, health check) must be scriptable.

## 4. Acceptance Criteria

- [ ] `python tests/verify_headless_gambit.py` passes locally (proving no X11 needed).
- [ ] `python scripts/verify_deployment.py` returns 200 OK from the remote Streamlit URL.
- [ ] Deployment build logs show < 5 minute runtime.
- [ ] `dashboard.py` displays the correct version hash.
