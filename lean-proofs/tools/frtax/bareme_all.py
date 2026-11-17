"""Brochure pratique scale tables ("Barème de l'impôt"), income 2020-2025, as collected in data/official_bareme_tables.jsonl:
each printed cell (situation, parts, taxable income -> tax after the QF cap and the décote). Run through Lean's table
mode (every cell) and, where plain boxes give that situation and parts, through Lean and Mlang as households.

usage: bareme_all.py tables.jsonl out.json
"""
import collections, json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from brochure_tables import household, run_lean, run_m

SIT = {"single": 0, "single, lives alone, raised a child alone >= 5 years (case L)": 1,
       "single, lives alone with children (case T)": 2, "widowed with dependent children": 3, "couple": 4}
rows = [json.loads(l) for l in open(sys.argv[1])]
by = collections.defaultdict(list)
for r in rows:
    f = r["facts"]
    by[r["income_year"]].append({"id": r["id"].replace(",", "."), "sit": SIT[f["situation"]], "parts": float(f["parts"]),
                                 "income": int(f["net_taxable_income"]),
                                 "tax": r["expected"]["impot_apres_plafonnement_et_decote"]})
out = {}
for year in sorted(by):
    cells = by[year]
    for i, c in enumerate(cells):
        c["id"] = f"y{year}_{i}"
        c["boxes"] = household(c["sit"], c["parts"])
    lt = run_lean([f"T;{c['id']};{year};{c['sit']};{int(round(c['parts'] * 4))};{c['income']}\n" for c in cells])
    hh = [c for c in cells if c["boxes"] is not None]
    cases = [(c["id"], {**c["boxes"], "4BA": c["income"]}) for c in hh]
    lh = run_lean([f"{cid};{year};" + ",".join(f"{k}={v}" for k, v in b.items()) + "\n" for cid, b in cases])
    mm = run_m(year, cases)
    for c in cells:
        c["lean_table"] = lt.get(c["id"], {}).get("TAX")
        if c["boxes"] is not None:
            c["lean_household"] = lh.get(c["id"], {}).get("IDRS4")
            c["m"] = mm.get(c["id"])
    n, nh = len(cells), len(hh)
    ok_lt = sum(c["lean_table"] == c["tax"] for c in cells)
    ok_lh = sum(c["lean_household"] == c["tax"] for c in hh)
    ok_m = sum(c["m"] == c["tax"] for c in hh)
    print(f"income {year}: {n} cells; Lean tableTax {ok_lt}/{n}; household cells {nh}: Lean {ok_lh}/{nh}, Mlang {ok_m}/{nh}")
    bad = [c for c in cells if c["lean_table"] != c["tax"] or (c["boxes"] and (c["m"] != c["tax"] or c["lean_household"] != c["tax"]))]
    for c in bad[:12]:
        print("   DIFF", {k: c.get(k) for k in ("sit", "parts", "income", "tax", "lean_table", "lean_household", "m")})
    out[year] = cells
json.dump(out, open(sys.argv[2], "w"))
