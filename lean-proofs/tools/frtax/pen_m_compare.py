"""Penalty study: compare M correctif results (runs/pen/m_cases_m.json) with Lean (runs/pen/m_cases_lean.out).
Usage: python3 -I harness/pen_m_compare.py [M.json] [LEAN.out] [META.json]"""
import json, sys
mj = sys.argv[1] if len(sys.argv) > 1 else "runs/pen/m_cases_m.json"
lo = sys.argv[2] if len(sys.argv) > 2 else "runs/pen/m_cases_lean.out"
me = sys.argv[3] if len(sys.argv) > 3 else "data/pen/m_cases_meta.json"
R = {r["id"]: r for r in json.load(open(mj))}
META = {m["id"]: m for m in json.load(open(me))}
L = {}
for l in open(lo):
    p = l.strip().split(";"); L[p[0]] = dict(x.split("=", 1) for x in p[1:])
rows = []
for i, r in R.items():
    v = r["vals"]; g = lambda k: int(round(v[k])) if k in v else None
    if i.startswith("P"):
        print(i, "primitif", {k: int(x) for k, x in v.items()}); continue
    lv = L.get(i, {})
    mm = (g("NMAJ1") or 0) + (g("NMAJ3") or 0) + (g("NMAJ4") or 0)
    row = {"id": i, "what": META.get(i, {}).get("what"), "M_IRN": g("IRN"), "M_months": g("NBMOIS2"), "M_int": g("RETIR"),
           "M_majo": mm, "M_tx": [g("MAJTX1"), g("MAJTX3"), g("MAJTX4")], "M_nmaj": [g("NMAJ1"), g("NMAJ3"), g("NMAJ4")],
           "L_tend": int(lv.get("TEND", -1)), "L_inc": int(lv.get("INC", -1)), "L_months": int(lv.get("MONTHS", -1)),
           "L_int": int(lv.get("INT", -1)), "L_majo": int(lv.get("MAJO", -1)), "L_layers": lv.get("LAYERS")}
    row["eq_months"] = row["M_months"] == row["L_months"]
    row["eq_int"] = row["M_int"] == row["L_int"]
    row["eq_majo"] = row["M_majo"] == row["L_majo"]
    rows.append(row)
    flag = "" if row["eq_int"] and row["eq_majo"] and row["eq_months"] else "  <-- DIFF"
    print(f"{i:8s} M irn={row['M_IRN']} mo={row['M_months']} int={row['M_int']} majo={mm} tx={row['M_tx']} n={row['M_nmaj']} | "
          f"L tend={row['L_tend']} inc={row['L_inc']} mo={row['L_months']} int={row['L_int']} majo={row['L_majo']} {row['L_layers']}{flag}")
n = len(rows)
print(f"months equal {sum(r['eq_months'] for r in rows)}/{n}; interest equal {sum(r['eq_int'] for r in rows)}/{n}; "
      f"majorations equal {sum(r['eq_majo'] for r in rows)}/{n}; all three {sum(r['eq_months'] and r['eq_int'] and r['eq_majo'] for r in rows)}/{n}")
json.dump(rows, open("runs/pen/m_compare.json", "w"), indent=1)
