# Review Log (Round 1) - P2 Protocol v1.0
**Lead Reviewer:** Dylan A Mordaunt

## Lens-Based Feedback

### 1. Methodological Rigour
*   **Critique:** Section 5 "Implementation" is too brief. ODD requires a "Details" section to define the specific submodels (e.g., the pressure-to-risk mapping).
*   **Action:** Expand the protocol to include explicit submodel definitions for the SD backbone and the Nash solvers.

### 2. Game Theory Logic
*   **Critique:** The audit policy is currently modeled as a rule-based referee (NHFP engine). To be a true game, the Auditor/Regulator must be modeled as a strategic player with a budget constraint.
*   **Action:** Document this as a "Proposed Model Refinement". Even if implemented as a heuristic, the *specification* should treat it as a player.

### 3. Clinical Executive
*   **Critique:** The "Efficiency Gap" is a static variable. In practice, this gap drives service substitution behaviors (e.g., shifting to non-admitted care).
*   **Action:** Ensure the "Provider Move" section mentions service-stream substitution as an action.

## Implementation Plan
1.  Add Section 6 "Submodels" to the protocol.
2.  Refine the "Entities" section to better define the Auditor role.
3.  Implement Protocol changes in v1.1.
