# Audit Report: Stubbed & Planned Features
**Date:** 2025-12-26

## 1. LLM / Cognitive Agents
*   **Location:** `src/nhra_game_theory/agents/base.py`
*   **Status:** Explicitly stubbed (`MOCK/STUB logic for now`).
*   **Plan:** The `decide` method currently uses heuristics. The intent is to delegate this to an LLM via the `automated_evidence_api` track, but the core integration in the agent base class remains a mock.

## 2. JAX / Differentiable Calibration
*   **Location:** `src/nhra_game_theory/calibration/bayesian.py`
*   **Status:** Placeholder comments for `step()` logic translation.
*   **Context:** While Optuna is used for calibration, the `bayesian.py` file suggests an abandoned or future intent to use JAX for gradient-based calibration or faster execution.
*   **Test Evidence:** `tests/test_jax_compliance.py` contains a placeholder `test_nash_solver_placeholder`.

## 3. Dashboard Data Integration
*   **Location:** `scripts/dashboard.py`
*   **Status:** Uses a placeholder file for the "Registry".
*   **Impact:** The dashboard might not be visualizing the *actual* active parameter set used in the simulation, leading to a disconnect between inputs and outputs in the UI.

## 4. Evidence Parsing API
*   **Location:** `scripts/llm_evidence_parser.py`
*   **Status:** `Placeholder for real API call`.
*   **Impact:** The automated evidence gathering pipeline likely returns mock data or requires manual overrides, limiting its utility for live "evidence-to-model" updates.
