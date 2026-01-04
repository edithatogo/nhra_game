# Local handover prompt

Use this prompt if you want another model/agent to continue development locally.

## Prompt

You are helping maintain a Python repository that contains stylised mechanism models for NHRA negotiations.

Goals:

- Produce scenario and sensitivity analysis outputs that are decision-useful for NHRA discussions (2025–2030) and are defensible for an MJA original article.
- Keep all inputs empirically grounded to **publicly retrievable sources**. If not possible, record a detailed assumption rationale and plausible range.

Repo conventions:

- Run: `just all` for full pipeline.
- Context and assumptions live in the `context/` folder.
- Parameter grounding is enforced by `just check-params`.

Your tasks:

1) Identify the weakest assumptions and propose public sources or better proxies.
2) Suggest one additional intervention scenario that is strongly policy-relevant.
3) Extend the D3 network overlay to use year-specific values rather than copying 2030 values across years.
