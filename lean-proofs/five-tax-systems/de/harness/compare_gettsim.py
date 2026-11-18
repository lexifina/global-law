#!/usr/bin/env python3
"""Compare detax (Lean) with GETTSIM household by household.

compare_gettsim.py households.jsonl lean.jsonl gettsim.jsonl [--show N] [--field F]

Per household and field: Lean value, GETTSIM value, difference. Fields:
  est   festzusetzende ESt (tariff tax + Kindergeld added back), euros
  zve   zu versteuerndes Einkommen (of the units, summed)
  abg   Abgeltungsteuer
  soli  Solidaritätszuschlag
  rv, av, kv, pv  employee contributions
  kg    Kindergeld paid
A household "agrees" on a field if |diff| <= tol (1 cent for amounts in cents, 0 for whole euros).
"""
import json, sys
from collections import Counter, defaultdict

def lean_fields(o):
    d = o["detail"]
    est = zve = abg = soli = 0.0
    rv = av = kv = pv = 0.0
    for u in d["units"]:
        est += u["tariffTax_32a"] + u["kindergeldAddedBack_2_6"]
        zve += u["zvE"]
        abg += u["abgeltungsteuer_32d"]
        soli += u["soli"]
        for m in u["members"]:
            rv += m["RV"]; av += m["AV"]; kv += m["KV"]; pv += m["PV"]
    return dict(est=est, zve=zve, abg=abg, soli=soli, rv=rv, av=av, kv=kv, pv=pv, kg=d["kindergeldPaid"],
                capInTariff=any(u["capitalInTariff_32d6"] for u in d["units"]),
                kidsFB=[u["kidsWithFreibetrag"] for u in d["units"]])

def g_fields(g):
    return dict(est=g["est"], zve=g["zve"], abg=g["abgeltung"], soli=g["soli"], rv=g["rv"], av=g["av"],
                kv=g["kv"], pv=g["pv"], kg=g["kindergeld"])

TOL = dict(est=0.0, zve=0.0, abg=0.01, soli=0.01, rv=0.01, av=0.01, kv=0.01, pv=0.01, kg=0.01)

def main():
    hs = [json.loads(l) for l in open(sys.argv[1])]
    lean = [json.loads(l) for l in open(sys.argv[2])]
    gt = [json.loads(l) for l in open(sys.argv[3])]
    show = int(sys.argv[sys.argv.index("--show") + 1]) if "--show" in sys.argv else 10
    only = sys.argv[sys.argv.index("--field") + 1] if "--field" in sys.argv else None
    agree = Counter(); n = len(hs)
    bad = defaultdict(list)
    allok = 0
    for h, l, g in zip(hs, lean, gt):
        assert l["id"] == g["id"] == h["id"]
        lf, gf = lean_fields(l), g_fields(g)
        ok_all = True
        for k in TOL:
            d = lf[k] - gf[k]
            if abs(d) <= TOL[k] + 1e-6:
                agree[k] += 1
            else:
                ok_all = False
                bad[k].append((abs(d), h["id"], round(lf[k], 4), round(gf[k], 4), round(d, 4)))
        allok += ok_all
    print(f"households: {n}; all fields agree: {allok}")
    for k in TOL:
        diffs = sorted(bad[k], reverse=True)
        small = sum(1 for x in diffs if x[0] <= 1.0)
        print(f"  {k:5s} agree {agree[k]:6d}/{n}   differ {len(diffs):5d} (of which |diff|<=1: {small})")
    for k in TOL:
        if only and k != only:
            continue
        if bad[k]:
            print(f"--- {k}: largest differences (abs, id, lean, gettsim, lean-gettsim)")
            for x in sorted(bad[k], reverse=True)[:show]:
                print("   ", x)

if __name__ == "__main__":
    main()
