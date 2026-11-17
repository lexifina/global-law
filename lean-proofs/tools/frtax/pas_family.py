"""Per-family table for a targeted PAS set: Lean against M (and production when a sim file is given).

usage: pas_family.py cases.jsonl OUT_DIR [sim.jsonl]
"""
import json, sys, collections

cases = {c["id"]: c for c in map(json.loads, open(sys.argv[1]))}
out = sys.argv[2]
m = {r["id"]: r for r in map(json.loads, open(f"{out}/pas_m.jsonl"))}
lean = {r["id"]: r for r in map(json.loads, open(f"{out}/pas_lean.jsonl"))}
sim = {r["id"]: r for r in map(json.loads, open(sys.argv[3]))} if len(sys.argv) > 3 else {}


def eq(a, b):
    return a is not None and b is not None and abs(a - b) < 1e-6


rows = collections.defaultdict(collections.Counter)
ex = {}
for cid, c in cases.items():
    f = c["family"]
    r = rows[f]
    r["n"] += 1
    mv, lv = m.get(cid), lean.get(cid)
    if mv is None:
        r["M refused"] += 1
        continue
    if lv is None or "TXFOYER" not in lv:
        r["Lean out of scope"] += 1
        continue
    r["hh equal"] += eq(lv["TXFOYER"], mv.get("RASTXFOYER", 0))
    if "TXDEC1" in lv:
        r["couples"] += 1
        r["ind equal (couples' decote)"] += all(eq(lv["TXDEC" + k], mv.get("RASTXDEC" + k, 0)) for k in "12")
        r["ind equal (single decote)"] += all(eq(lv["TXDEC" + k + "S"], mv.get("RASTXDEC" + k, 0)) for k in "12")
    s = sim.get(cid, {}).get("sim", {})
    if "TXFOYER" in s:
        r["prod"] += 1
        r["prod = M (hh)"] += eq(s["TXFOYER"], mv.get("RASTXFOYER", 0))
        r["prod = Lean (hh)"] += eq(s["TXFOYER"], lv["TXFOYER"])
        if "TXDEC1" in s and "TXDEC1" in lv:
            r["prod ind"] += 1
            r["prod = M (ind)"] += all(eq(s["TXDEC" + k], mv.get("RASTXDEC" + k, 0)) for k in "12")
            r["prod = Lean (ind)"] += all(eq(s["TXDEC" + k], lv["TXDEC" + k]) for k in "12")
            r["prod = Lean single-decote (ind)"] += all(eq(s["TXDEC" + k], lv["TXDEC" + k + "S"]) for k in "12")
    bad = not eq(lv["TXFOYER"], mv.get("RASTXFOYER", 0)) or ("TXDEC1" in lv and not all(
        eq(lv["TXDEC" + k], mv.get("RASTXDEC" + k, 0)) for k in "12"))
    if bad and f not in ex:
        ex[f] = {"id": cid, "year": c["year"], "boxes": c["boxes"], "note": c.get("note"),
                 "Lean": {k: lv.get(k) for k in ("TXFOYER", "TXFOYER61", "PASIR", "PASNUM", "PASDEN", "PASII", "TXDEC1", "TXDEC2", "TXDEC1S", "TXDEC2S", "REVKIRE", "IMPNET")},
                 "M": {k: mv.get(k) for k in ("RASTXFOYER", "IRTOTAL", "PASNUMF", "PASDENF", "INDTAZ", "RASTXDEC1", "RASTXDEC2", "REVKIRE", "IRINDIV1")},
                 "prod": s or None}
for f in sorted(rows):
    r = rows[f]
    print(f"{f}: " + ", ".join(f"{k} {v}" for k, v in r.items()))
json.dump({"rows": {f: dict(r) for f, r in rows.items()}, "examples": ex}, open(f"{out}/pas_family.json", "w"), indent=1, ensure_ascii=False)
print("examples:")
for f, e in ex.items():
    print(" ", f, json.dumps(e, ensure_ascii=False))
