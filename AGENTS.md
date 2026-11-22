# Working on NHRA Game Theory

Read [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md) and the owning
[Conductor plan](conductor/tracks.md) before editing. Preserve existing model
assumptions, evidence and other contributors' work.

## Game capability ownership

UOGTO is the authoritative game ontology; Paignia owns reusable game
representations and solvers. For every newly identified, added or materially
changed game, follow
the [contributor intake rule](CONTRIBUTING.md#game-capability-intake) and record
both semantic coverage and reusable implementation needs using:

- [UOGTO downstream game intake](https://github.com/edithatogo/UOGTO/blob/main/docs/contracts/downstream-game-intake.md).
- [Paignia downstream game intake](https://github.com/edithatogo/paignia/blob/main/docs/integrations/downstream-game-intake.md).

Record UOGTO's `reuse_existing`, `extension_required`, `unsupported` or
`mapping_review_pending` disposition separately from Paignia's `reuse_existing`,
`extension_required`, `unsupported`, `domain_only` or `assessment_pending`.
Funding rules, scenario data, payoff construction and calibration
remain here. Route generic changes and synthetic conformance fixtures upstream;
do not introduce a second reusable solver in this application.

Existing local models may remain while migration is assessed, with their scope
and limitations labelled. This policy does not replace algorithms or certify
their results. Consume accepted immutable provider revisions and record the
focused conformance checks actually run before claiming a migration complete.
