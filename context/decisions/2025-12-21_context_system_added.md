# Decision log — context system

Date: 2025-12-21

## Decision

Add a lightweight `context/` folder and automation scripts to support **local handover** and **evidence-traceability**.

## Rationale

The project spans modelling, policy advocacy, and manuscript preparation. Without a single source of truth for assumptions, parameters, sources, and scope, iteration becomes brittle.

## Consequences

- Developers can regenerate a standalone `CONTEXT_PACK.md` which is safe to paste into other assistants or workflows.
- CI can enforce that every parameter is either (i) cited to a publicly retrievable source or (ii) explicitly justified with a plausible range.
