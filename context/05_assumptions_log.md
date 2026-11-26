# Assumptions log

The [parameter registry](04_parameter_registry.csv) records the default, units,
source and justification for every public scalar input. It also records eight
inherited JAX scalars that the public constructor leaves in the runtime record.
The runtime rule objects and economic spine are injected separately. Their
source material belongs in the [data provenance record](06_data_provenance.md).

The reference edition uses the [public parameter definitions](https://github.com/edithatogo/nhra_game/blob/6250bdc12946016b42cb9d3e61818d04b5ee38c2/src/nhra_gt/domain/params.py).
The [coefficient abstraction](https://github.com/edithatogo/nhra_game/commit/5b40b4642e0a60f74e92e5cfd24cefea1142548c)
retains the transition, strategy and policy coefficients from the earlier
implementation. The registry identifies their individual model roles and
definition locations. The paired trajectory checks hold the inner coefficients
and ordered cutoffs at their reference values.

The legacy JAX code generator takes its historical flat input via
`--registry`. The current ledger contains grouped runtime coefficients and
public defaults, including the public demand and equilibrium selections.

### Interpreting bounds

Equal endpoints record a fixed design value for this reference. Unequal
endpoints record scenario bounds. The six parameters in the mechanism Morris
screen use the bounds declared by that screen. Other inherited scenario
bounds retain their documented scope. Code endpoints for the cap, audit and
orchestration selectors describe discrete alternatives.

Sensitivity studies specify the parameters varied, their scenario intervals
and the output being assessed. Fixed reference values need a justified
interval before they can be used as sensitivity axes. Scientific qualification
requires the actual source series and holdout design.

### Empirical anchors

AIHW's 2024–25 national emergency department result anchors
`within4_base` at 0.53. The model’s 0.88 initial occupancy and 18-minute
offload value are scenario inputs. The historical National Health Reform
Agreement documents a 6.5% annual funding cap and a 45% Commonwealth share of
efficient growth under that cap. The model uses the latter as its nominal
agreement-share input. [AIHW ED data](https://www.aihw.gov.au/hospitals/topics/emergency-departments/time-spent-in-emergency) ·
[2020–25 Addendum](https://www.mtaa.org.au/sites/default/files/uploaded-content/field_f_content_file/2020-25_national_health_reform_agreement.pdf)

## Current high-impact assumptions (track for refinement)

- Rurality and remoteness mix fractions used to compute an “efficiency gap”.
- Mappings from pressure → ED≤4h and offload minutes (calibration/normalisation).
- Behavioural/payoff weights in stage games (political salience, bargaining cost, audit pressure).
