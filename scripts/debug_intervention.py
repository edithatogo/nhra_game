"""Debug script to test intervention logic application."""

from nhra_gt.domain.params import Params

p = Params()
print(f"Original: {p.cost_shifting_intensity}")
p_new = apply_intervention(p, "Pooled Funding")
print(f"New: {p_new.cost_shifting_intensity}")
