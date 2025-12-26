# Usage Guide: NHRA Strategic Scenario Analysis

This guide explains how to use the interactive dashboard to simulate NHRA negotiation outcomes and Patient Safety Risk.

## 1. Core Workflow
1.  **Adjust Levers:** Use the sidebar to set the "Nominal Cth Share Target", "NEP Growth", and operational capacity indices.
2.  **Analyze Trajectories:** Observe the grey (Baseline) vs teal (Scenario) lines in the Patient Safety and System Pressure plots.
3.  **Audit Convergence:** Check the "Simulation Confidence" metric in the sidebar. If confidence is Low/Medium, click **"Boost to SOTA Accuracy"** for a high-fidelity 1000-sample run.

## 2. Expert Strategic Mode
Enable the **🧠 Expert Strategic Mode** toggle in the sidebar to reveal direct subgame overrides.

### Manual Overrides
You can manually force any of the following games into a specific strategy:
- **Definition:** Realism (R) vs Strict (E)
- **Bargaining:** Agree (A) vs Defer (D)
- **Cost-Shifting:** Invest (I) vs Shift (S)
- **Discharge:** Coordinate (C) vs Fragment (F)
- **Integration:** Integrate (I) vs Separate (S)
- **Compliance:** Tight (T) vs Light (L)

### Strategic Conflict Detection
If a manual override logically contradicts your selected policy levers (e.g., forcing a 'Strict' definition while promoting 'NEP Realism'), a **⚠️ Strategic Contradiction** warning will appear in the sidebar. This highlights the inherent tension between your desired policy intent and forced strategic behavior.

## 3. Forensic Audit
Use the **🔍 Forensic Audit** tab to inspect the raw `State` dictionary at each time step. This is useful for verifying functional parity between the interactive dashboard and the core engine.