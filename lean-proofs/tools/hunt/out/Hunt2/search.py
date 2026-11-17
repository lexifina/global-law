"""Blind search, PolicyEngine-US 2.138.1, tax year 2025: households x 51 jurisdictions x taxpayer moves.
Objective: federal income tax + state income tax (both after refundable credits). For every move we record the
federal and state change against the household's default (PolicyEngine's own federal itemizing choice, no move).
Flag: federal cost > 0 and total < default (a move that costs federally but pays at state level), and anything
where the state change has the opposite sign to the federal change by more than the federal change."""
import sys, json, itertools
from policyengine_us import Simulation

STATES = "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()

HOUSEHOLDS = []
for married, kids in [(False, 0), (True, 2)]:
    for wages in (45000, 90000, 180000, 400000):
        for itemizable in (0, 12000, 24000):
            HOUSEHOLDS.append(dict(married=married, kids=kids, wages=wages, mort=itemizable))

MOVES = {
    "none": {},
    "itemize": {"tax_unit_itemizes": True},
    "standard": {"tax_unit_itemizes": False},
    "k401_10k": {"k401": 10000},
    "k401_max": {"k401": 23500},
    "hsa": {"hsa": 4300},
    "charity_bunch": {"charity": 10000},     # pay next year's gifts this year (timing)
}

def add_case(sit, cid, year, state, h, move):
    p1 = f"{cid}_a"
    members = [p1]
    w = h["wages"] if not h["married"] else h["wages"] * 0.6
    people = {p1: {"age": {year: 40}, "employment_income": {year: w},
                   "mortgage_interest": {year: h["mort"] * 0.7}, "real_estate_taxes": {year: h["mort"] * 0.3},
                   "charitable_cash_donations": {year: move.get("charity", 0)},
                   "traditional_401k_contributions": {year: move.get("k401", 0)}}}
    if h["married"]:
        p2 = f"{cid}_b"
        people[p2] = {"age": {year: 40}, "employment_income": {year: h["wages"] * 0.4}}
        members.append(p2)
    for k in range(h["kids"]):
        c = f"{cid}_c{k}"
        people[c] = {"age": {year: 6 + 3 * k}}
        members.append(c)
    sit["people"].update(people)
    tu = {"members": members}
    if "tax_unit_itemizes" in move:
        tu["tax_unit_itemizes"] = {year: move["tax_unit_itemizes"]}
    if "hsa" in move:
        tu["health_savings_account_ald"] = {year: move["hsa"]}
    sit["tax_units"][cid] = tu
    sit["families"][cid] = {"members": members}
    sit["spm_units"][cid] = {"members": members}
    sit["marital_units"][cid] = {"members": members[:2] if h["married"] else [p1]}
    if h["married"]:
        for k in range(h["kids"]):
            sit["marital_units"][f"{cid}_mc{k}"] = {"members": [f"{cid}_c{k}"]}
    else:
        for k in range(h["kids"]):
            sit["marital_units"][f"{cid}_mc{k}"] = {"members": [f"{cid}_c{k}"]}
    sit["households"][cid] = {"members": members, "state_name": {year: state}}

if __name__ == "__main__":
    year = 2025
    states = sys.argv[1].split(",") if len(sys.argv) > 1 else STATES
    results = []
    for state in states:
        sit = {k: {} for k in ("people", "tax_units", "families", "spm_units", "marital_units", "households")}
        keys = []
        for hi, h in enumerate(HOUSEHOLDS):
            for mv, move in MOVES.items():
                cid = f"h{hi}_{mv}"
                add_case(sit, cid, year, state, h, move)
                keys.append((hi, mv))
        s = Simulation(situation=sit)
        fed = s.calculate("income_tax", year)
        st = s.calculate("state_income_tax", year)
        tab = {}
        for i, (hi, mv) in enumerate(keys):
            tab[(hi, mv)] = (float(fed[i]), float(st[i]))
        for hi, h in enumerate(HOUSEHOLDS):
            f0, s0 = tab[(hi, "none")]
            for mv in MOVES:
                if mv == "none":
                    continue
                f1, s1 = tab[(hi, mv)]
                df, ds = f1 - f0, s1 - s0
                results.append(dict(state=state, h=h, move=mv, dfed=round(df), dstate=round(ds), dtot=round(df + ds)))
        print(state, "done", flush=True)
    json.dump(results, open("search_2025.json", "w"))
    flagged = [r for r in results if r["dfed"] > 5 and r["dtot"] < -5]
    flagged.sort(key=lambda r: r["dtot"])
    print(f"\n{len(results)} (household, state, move) results; {len(flagged)} where the move costs federally but saves in total")
    for r in flagged[:60]:
        print(r)
