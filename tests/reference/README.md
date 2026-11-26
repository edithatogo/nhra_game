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
