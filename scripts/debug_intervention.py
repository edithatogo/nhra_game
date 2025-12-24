from nhra_game_theory.engine import Params, apply_intervention

p = Params()
print(f"Original: {p.cost_shifting_intensity}")
p_new = apply_intervention(p, "Pooled Funding")
print(f"New: {p_new.cost_shifting_intensity}")
