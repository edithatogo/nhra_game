# NHRA scalar trajectory reference

The fixture uses the scalar engine from [ab65315](https://github.com/edithatogo/nhra_game/tree/ab65315de2d6be438f0655302f48cc568e0f851f/src/nhra_gt), the parent of the
[JAX consolidation](https://github.com/edithatogo/nhra_game/commit/30db9afc4f7defeb632e487d383d1cb3ae7cc561).
Its scalar engine, queue, policy and Nash modules all run from the historical
tree. The deleted root-level `intermediate_engine.py` at
[da4c64b](https://github.com/edithatogo/nhra_game/blob/da4c64b24c8fc137acf5386f490ab8547262ff29/intermediate_engine.py)
called `step_jax` and is unsuitable as a reference.

Both engines start in January 2025 with the same scenario demand and
occupancy calibration and the scalar starting efficiency gap and funding
share. The one-month cases use seed 42 in each engine. The 72-month pressure
cases remove demand noise. The baseline trajectory keeps the existing
coordinated actions. The stress case uses higher demand, pressure and
occupancy, cost shifting and workforce competition. Occupancy is calibrated
to the starting point in each case. The historical funding transition did
not apply the current monthly growth cap, so the funding-share comparison
covers the initial step, before cap activation, at the original tolerance.
Pressure parity covers every month at the original tolerance and does not
validate the other trajectory fields. The agreement-cycle and cap tests
continue to exercise the current model's distinct policy behavior.

To regenerate from the repository root with CPython 3.15.2, NumPy 2.5.5 and
pandas 3.1.1, extract the historical source into an isolated directory and
run the generator against that copy.

```sh
scalar_source=$(mktemp -d)
git archive ab65315de2d6be438f0655302f48cc568e0f851f src | tar -xf - -C "$scalar_source"
uv venv --python 3.15.2 "$scalar_source/.venv"
uv pip install --python "$scalar_source/.venv/bin/python" numpy==2.5.5 pandas==3.1.1
PYTHONPATH="$scalar_source/src" "$scalar_source/.venv/bin/python" \
  tests/reference/generate_scalar_trajectory.py > "$scalar_source/actual.json"
cmp tests/reference/scalar_trajectory.json "$scalar_source/actual.json"
```

## Historical model audit

The audit and candidate scan in `model_audit/` are exact copies of the
completed audit track at commit
[19fe29f](https://github.com/edithatogo/nhra_game/tree/19fe29f0f30ad4186c6615bd80ce602d5512c580/conductor/tracks/model_audit_20260101).
The track files were removed in
[3911547](https://github.com/edithatogo/nhra_game/commit/3911547d7c2ba6c384d796d099100a358f36b666).
The original four test modules still check the report structure, assumptions,
references and recorded results. The phase 2 checks still cross-reference the
maintained bibliography. These files record the January 2026 audit, including
its unresolved source checks. The fixtures preserve the source bytes as test
inputs. The current model has its own numerical and input-grounding checks.

| Fixture | SHA-256 |
| --- | --- |
| `model_audit/audit.md.fixture` | `37682a0e044159abaf2fcdf5dc388f033742f0a7d26196fa0b63dd0a27582c40` |
| `model_audit/model_candidates.md.fixture` | `7ab20aef5d318f1b74ac5f008c8ab4ae037f1aa7ffcf580bce455bc3a3a7861a` |
