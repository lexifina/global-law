"""Compare the DGFiP production simulator's answers (runs/sim.jsonl) with Mlang (published M code) and Lean."""
import json, subprocess, sys, collections, os

LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
sim = [json.loads(l) for l in open(sys.argv[1])]
cases = {}
for l in open(sys.argv[2]):
    c = json.loads(l)
    cases[c["id"]] = c
m = {}
for l in open(sys.argv[3]):
    d = json.loads(l)
    m[d["id"]] = d
ids = [s["id"] for s in sim if "_error" not in s["sim"] and s["id"] in m]
inp = "".join(f"{i};{cases[i]['year']};" + ",".join(f"{k}={v}" for k, v in cases[i]["boxes"].items()) + "\n" for i in ids)
lean = {}
for l in subprocess.run([LEAN], input=inp, capture_output=True, text=True).stdout.splitlines():
    p = l.split(";")
    lean[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:]}

# simulator field -> (M value, Lean value)
def fields(s, mv, lv):
    return {
        "parts": (s.get("NBPT"), mv.get("NBPT"), lv.get("NBPT")),
        "RFR": (s.get("REVKIRE"), mv.get("REVKIRE"), lv.get("REVKIRE")),
        "taxable income": (s.get("RNI"), mv.get("RNI"), lv.get("RNI")),
        "gross tax (capped, before complement)": (s.get("IDRS"), mv.get("IDRS2"), lv.get("IDRSCAP")),
        "décote": (s.get("IDEC", 0.0), mv.get("IDEC"), lv.get("IDEC")),
        "reductions": (s.get("ITRED", 0.0), mv.get("ITRED"), lv.get("ITRED")),
        "flat taxes": (s.get("PROP", 0.0), mv.get("IPROP", 0.0), lv.get("PFU")),
        "CEHR": (s.get("CEHR", 0.0), mv.get("CHRAPRES", 0.0), lv.get("CHRAPRES")),
        "amount payable (tax + CEHR + CDHR + levies, less refund)":
            ((s.get("PAYER") or 0) - (s.get("REMB") or 0) if "PAYER" in s else None,
             (mv.get("IRN") or 0) + (mv.get("CHRAPRES") or 0) + (mv.get("CDHR") or 0) + (mv.get("PSNET") or 0),
             (lv.get("IMPNET") or 0) + (lv.get("CHRAPRES") or 0) + (lv.get("CDHR") or 0) + (lv.get("PSNET") or 0)),
    }

stat = collections.defaultdict(collections.Counter)
allm = alll = 0
diffs = []
for i in ids:
    s, mv, lv = next(x["sim"] for x in sim if x["id"] == i), m[i], lean[i]
    okm_all = okl_all = True
    for name, (sv, mvv, lvv) in fields(s, mv, lv).items():
        if sv is None:
            continue
        okm = mvv is not None and abs(sv - mvv) < 0.5
        okl = lvv is not None and abs(sv - lvv) < 0.5
        stat[name]["M"] += okm
        stat[name]["Lean"] += okl
        stat[name]["n"] += 1
        okm_all &= okm
        okl_all &= okl
        if not okm or not okl:
            diffs.append((i, cases[i]["year"], name, sv, mvv, lvv))
    allm += okm_all
    alll += okl_all
n = len(ids)
print(f"households answered by the simulator: {n}; every figure equal: M {allm}/{n}, Lean {alll}/{n}")
for name, c in stat.items():
    print(f"  {name:20s} M {c['M']}/{c['n']}  Lean {c['Lean']}/{c['n']}")
json.dump(diffs, open(sys.argv[4], "w"))
for d in diffs[:40]:
    i = d[0]
    print("  DIFF", d, {k: v for k, v in cases[i]["boxes"].items() if k[0] in "123456789"})
