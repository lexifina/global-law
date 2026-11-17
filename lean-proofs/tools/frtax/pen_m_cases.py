"""Penalty study: build the Lean-vs-M correctif cases.
Writes data/pen/m_cases.json (for pen_m_run.py), data/pen/m_cases_lean.txt (X lines for pen_eval.lean) and
data/pen/m_cases_meta.json (what each case is, statute-wise).
M penalty code -> statute reading, from M's own tables (m_ext/<year>/correctif.m taux_penalite and get_strate_pena,
chap-majo.m, chap-inr.m) and from the first runs:
  01, 99: no majoration and no interest (M computes none: read as mention expresse / service error)
  02, 07, 10: 10 % (art. 1758 A: good-faith insufficiency, late return without notice)
  17: 20 % (art. 1758 A, late return within 30 days of a formal notice; M: 2 x TX1758A)
  03, 08, 11, 30, 55: 40 %  (1729 a, 1728 b, 1758, 1729 b reduced)
  04, 05, 09, 12, 31, 32, 35: 80 %   06: 100 %
  22: interest at 70 % (LPF L62)   24: interest at 50 % (art. 1727, V)"""
import json
RATE = {1: "0n", 2: "10", 3: "40", 4: "80", 5: "80", 6: "100", 7: "10l", 8: "40l", 9: "80", 10: "10l", 11: "40l",
        12: "80", 17: "20l", 22: "0", 24: "0", 30: "40", 31: "80", 32: "80", 35: "80", 55: "40", 99: "0n"}
RELIEF = {22: "l62", 24: "spontaneous"}
BASE = {"0AM": 1, "0DA": 1980, "0DB": 1980, "1AJ": 30000, "1BJ": 20000}
B2 = {"0AM": 1, "0DA": 1980, "0DB": 1980, "1AJ": 21000, "1BJ": 16000}
ITEMS = [("0AM", 1), ("0DA", 1980), ("0DB", 1980), ("1AJ", 30000), ("1BJ", 20000)]
cases, lean, meta = [], [], []
def add(cid, decl, rapp, my, what, year=2023, keep=False, layers=None, relief=None):
    """rapp: [(MMYYYY, box, amount, code)]; Lean layers default to one layer per rappel with its code's rate and
    its own stop month."""
    cases.append({"id": cid, "year": year, "decl": decl, "rappels": [list(x) for x in rapp]})
    if layers is None:
        layers = [(RATE[c] + (f"@{int(str(m)[-4:])}{int(str(m)[:-4]):02d}" if m != my else ""), [(b, a)]) for m, b, a, c in rapp]
    if relief is None:
        relief = next((RELIEF[c] for _, _, _, c in rapp if c in RELIEF), "none")
    d = ",".join(f"{k}={v}" for k, v in decl.items())
    ls = ("=" if keep else "") + "|".join(f"{r}:" + ",".join(f"{k}={v}" for k, v in bx) for r, bx in layers)
    lean.append(f"X;{cid};{year};{d};{ls};{int(str(my)[-4:])};{int(str(my)[:-4])};{relief}")
    meta.append({"id": cid, "what": what, "year": year, "rappels": rapp, "lean_layers": ls})
# A. one reassessment, every penalty code
for c in RATE:
    add(f"A{c:02d}", BASE, [(102024, "1AJ", 20000, c)], 102024, f"1AJ +20000, code {c:02d}, proposition 10/2024")
# B. the stop month (code 03)
for my in [72024, 82024, 122024, 12025, 62025, 122025, 62026, 122026, 122027]:
    add(f"B{my:06d}", BASE, [(my, "1AJ", 20000, 3)], my, f"code 03, proposition {my:06d}")
# C. two or three layers (art. 1729 A, 1)
for cid, rs in [("C1", [("1AJ", 20000, 3), ("1BJ", 30000, 5)]), ("C2", [("1BJ", 30000, 5), ("1AJ", 20000, 3)]),
                ("C3", [("1AJ", 20000, 2), ("1BJ", 5000, 4)]), ("C4", [("1AJ", 3000, 1), ("1BJ", 20000, 3)]),
                ("C5", [("1AJ", 20000, 3), ("1BJ", 3000, 2)]), ("C6", [("1AJ", 3000, 2), ("1BJ", 20000, 3)]),
                ("C7", [("1AJ", 8000, 2), ("1BJ", 15000, 3), ("4BA", 12000, 5)]),
                ("C8", [("4BA", 12000, 5), ("1AJ", 8000, 2), ("1BJ", 15000, 3)]),
                ("C9", [("1AJ", 3000, 99), ("1BJ", 20000, 3)])]:
    add(cid, BASE, [(102024, b, a, p) for b, a, p in rs], 102024,
        "layers " + ", ".join(f"{b}+{a} code {p:02d}" for b, a, p in rs))
# D. late return: the whole return arrives as rappels with a late-filing code, filed 02/2025 (due 05/2024)
for p in [7, 8, 10, 11, 17]:
    add(f"D{p:02d}", {}, [(22025, b, a, p) for b, a in ITEMS], 22025, f"late return filed 02/2025, code {p:02d}",
        layers=[(RATE[p], ITEMS)])
# E. late return then a reassessment (art. 1729 A, 2 and 1727, IV, 3)
for cid, lp, rp in [("E1", 7, 3), ("E2", 8, 3), ("E3", 7, 5), ("E4", 7, 2), ("E5", 17, 3)]:
    add(cid, {}, [(22025, b, a, lp) for b, a in ITEMS] + [(102025, "1AJ", 20000, rp)], 102025,
        f"late return code {lp:02d} (02/2025) + reassessment code {rp:02d} (10/2025)", keep=True,
        layers=[(RATE[lp] + "@202502", ITEMS), (RATE[rp], [("1AJ", 20000)])] if int(RATE[rp].rstrip("nl")) > int(RATE[lp].rstrip("nl")) else
               [(RATE[lp] + "@202502", ITEMS), (RATE[lp], [("1AJ", 20000)])])
# F. BOFiP BOI-CF-INF-10-20-30-20 exemples 1 and 2 transposed to salaries: 21000/16000 declared
add("F1", B2, [(102024, "1AJ", 20000, 3), (102024, "1BJ", 3000, 1)], 102024, "BOFiP ex. 1, good-faith layer code 01")
add("F1b", B2, [(102024, "1AJ", 20000, 3), (102024, "1BJ", 3000, 2)], 102024, "BOFiP ex. 1, good-faith layer code 02 (1758 A)")
add("F2", B2, [(102024, "1AJ", 30000, 5), (102024, "1BJ", 10000, 3)], 102024, "BOFiP ex. 2 (80 % + 40 %)")
# G. small reassessments: art. 1727, II, 4 tolerance (a twentieth)
for cid, a, p in [("G1", 1000, 1), ("G2", 1000, 2), ("G3", 1000, 3), ("G4", 3000, 1), ("G5", 2700, 1),
                  ("G6", 2400, 2), ("G7", 2500, 2), ("G8", 2700, 2), ("G9", 3000, 2), ("G10", 2400, 7)]:
    add(cid, BASE, [(102024, "1AJ", a, p)], 102024, f"1AJ +{a} code {p:02d} (tolerance?)")
# I. reliefs over time
for cid, my, p in [("I1", 122025, 22), ("I2", 122025, 24), ("I3", 62027, 24), ("I4", 72024, 24)]:
    add(cid, BASE, [(my, "1AJ", 20000, p)], my, f"code {p:02d}, {my:06d}")
# K. other income years (each with its own M code): start 1 July N+1
for y in [2022, 2024]:
    for cid, my in [(f"K{y}a", 10 * 10000 + y + 1), (f"K{y}b", 12 * 10000 + y + 2)]:
        add(cid, BASE, [(my, "1AJ", 20000, 3)], my, f"income {y}, code 03, {my:06d}", year=y)
# P. primitif only, for the declared tax
for cid, d in [("P0", BASE), ("P2", B2)]:
    cases.append({"id": cid, "year": 2023, "decl": d, "rappels": []})
json.dump(cases, open("data/pen/m_cases.json", "w"), indent=1)
open("data/pen/m_cases_lean.txt", "w").write("\n".join(lean) + "\n")
json.dump(meta, open("data/pen/m_cases_meta.json", "w"), indent=1)
print(len(cases), "M cases,", len(lean), "Lean lines")
