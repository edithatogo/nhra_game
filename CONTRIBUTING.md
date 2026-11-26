# Contributing to NHRA Game Theory

Thank you for your interest in contributing! This project follows [pyOpenSci](https://www.pyopensci.org/) standards.

## Development Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/edithatogo/nhra_game.git
    cd nhra_game
    ```

2. **Install dependencies (using uv or pip):**

    ```bash
    pip install -e ".[dev]"
    # or
    uv pip install -e ".[dev]"
    ```

3. **Run tests:**

    ```bash
    nox
    # or
    pytest
    ```

## Pull Request Process

1. Create a feature branch.
2. Ensure `pytest` passes.
3. Ensure `ruff check .` passes.
4. Submit a PR with a description of changes.

## Documentation link check

CI checks links in tracked Markdown, including the regenerated context pack.
If the hosted runner cannot reach public sources, the repository owner can set
the Actions variable `NHRA_LINK_CHECK_REF` to the branch under test and start an
ephemeral GitHub Actions runner in Apple Container with the label
`nhra-links-<run-id>-<attempt>`. Only owner-triggered pushes and pull requests
from the same repository use this runner. Remove the variable once the run
finishes. The link checker uses the same files and failure criteria on either runner.

## Code Style

- **Formatting:** We use `ruff format`.
- **Linting:** We use `ruff check` and `mypy`.
- **Testing:** We require 95% test coverage for new features.

## Game capability intake

UOGTO owns game-theoretic semantics and Paignia owns reusable game
representations and solvers. Every newly identified, added or materially changed
game must have linked records under both upstream contracts:

- [UOGTO semantic coverage and extension intake](https://github.com/edithatogo/UOGTO/blob/main/docs/contracts/downstream-game-intake.md).
- [Paignia generic capability and fixture intake](https://github.com/edithatogo/paignia/blob/main/docs/integrations/downstream-game-intake.md).

Use the same intake key in both records and link them from the local plan or
pull request. Identify the originating source path and immutable revision,
players, actions, information, timing, payoff meaning and requested solution.
Record the semantic and implementation dispositions separately:

| Upstream | Allowed dispositions |
| --- | --- |
| UOGTO | `reuse_existing`, `extension_required`, `unsupported`, `mapping_review_pending` |
| Paignia | `reuse_existing`, `extension_required`, `unsupported`, `domain_only`, `assessment_pending` |

For `reuse_existing`, add or refine the UOGTO mapping/example with full term
IRIs and link the supported Paignia API/profile, its limits and fixture evidence.
For `extension_required`, link the upstream proposal, a minimal synthetic example
and independently expected results. `unsupported` records the missing requirement
and its effect on claims or execution. Paignia's `domain_only` records why the
change needs no generic implementation. Pending assessments need a reason,
owner and next action; they do not establish semantic or executable support.

Inspect existing upstream work before proposing another term, solver or fixture.
An unchanged game with new parameters can reuse its intake key and add an
application example. Data, assumptions, payoff construction and calibration
remain here; Paignia receives only reusable representations, algorithms and
conformance fixtures. Preserve source revision, licence and attribution for
any transferred example or implementation.

On adoption, record the exact UOGTO revision/profile and full IRIs, Paignia
revision or artifact hash, fixture identity, and focused semantic/native/consumer
checks actually run, including independent expected results and invalid or
unsupported cases. Ontology conformance and numerical verification are separate.
A record or dependency pin alone does not complete a migration.

Existing local or pedagogical implementations may remain while migration is
assessed, with their scope and limitations labelled. New game changes still
require intake. This policy does not replace algorithms, change model assumptions
or promote heuristic outputs to verified equilibria.
