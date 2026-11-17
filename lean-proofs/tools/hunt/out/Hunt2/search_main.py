"""Driver for search.py: one Simulation per move (all states x households), because a PolicyEngine input set on
some tax units (e.g. tax_unit_itemizes) becomes an input for every tax unit in that Simulation (others get the
default False) - see FINDINGS, PolicyEngine notes."""
import sys, json
sys.path.insert(0, '.')
from search import STATES, HOUSEHOLDS, MOVES, add_case
from policyengine_us import Simulation
year = 2025
tab = {}
for mv, move in MOVES.items():
    sit = {k: {} for k in ("people", "tax_units", "families", "spm_units", "marital_units", "households")}
    keys = []
    for state in STATES:
        for hi, h in enumerate(HOUSEHOLDS):
            cid = f"{state}_h{hi}"
            add_case(sit, cid, year, state, h, move)
            keys.append((state, hi))
    s = Simulation(situation=sit)
    fed = s.calculate("income_tax", year); st = s.calculate("state_income_tax", year)
    for i, k in enumerate(keys):
        tab[(k[0], k[1], mv)] = (float(fed[i]), float(st[i]))
    print(mv, "done", flush=True)
results = []
for state in STATES:
    for hi, h in enumerate(HOUSEHOLDS):
        f0, s0 = tab[(state, hi, "none")]
        for mv in MOVES:
            if mv == "none": continue
            f1, s1 = tab[(state, hi, mv)]
            results.append(dict(state=state, h=h, move=mv, fed0=round(f0), st0=round(s0), dfed=round(f1 - f0), dstate=round(s1 - s0), dtot=round(f1 + s1 - f0 - s0)))
json.dump(results, open("search_2025.json", "w"))
flag = sorted([r for r in results if r["dfed"] > 5 and r["dtot"] < -5], key=lambda r: r["dtot"])
print(f"{len(results)} results; {len(flag)} cost federally but save in total")
for r in flag[:80]: print(r)
