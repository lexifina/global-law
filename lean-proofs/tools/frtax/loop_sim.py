"""Loophole hunt: the DGFiP production simulator on the headline returns (harness/sim_run.py conventions).

Strictly sequential, 1.2 s apart; run under `flock ~/fr/.sim.lock`. A hard cap of 40 requests over all runs
(counted in runs/loop/sim.jsonl). Each answer is also run through Lean and Mlang for the comparison.
usage: flock ~/fr/.sim.lock python loop_sim.py cases.jsonl
cases.jsonl: {"id": ..., "year": ..., "boxes": {...}, "note": ...}
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim_run import post, parse
import loop_lib as L

OUT = os.path.expanduser("~/fr/runs/loop/sim.jsonl")
CAP = 40

cases = [json.loads(l) for l in open(sys.argv[1])]
done = {}
if os.path.exists(OUT):
    for l in open(OUT):
        r = json.loads(l)
        done[r["id"]] = r
used = len(done)
os.makedirs(OUT + ".html", exist_ok=True)
lean = L.lean([(c["id"], c["year"], c["boxes"]) for c in cases])
m, ko = L.mlang([(c["id"], c["year"], c["boxes"]) for c in cases])
with open(OUT, "a") as f:
    for c in cases:
        if c["id"] in done:
            continue
        if used >= CAP:
            print("CAP reached; not sent:", c["id"])
            continue
        try:
            page = post(c["year"], c["boxes"])
            open(f"{OUT}.html/{c['id']}.html", "w", encoding="latin-1", errors="replace").write(page)
            s = parse(page)
        except Exception as e:
            s = {"_error": repr(e)[:200]}
        used += 1
        lo = lean.get(c["id"], {})
        mm = m.get(c["id"])
        r = {"id": c["id"], "year": c["year"], "note": c.get("note"), "boxes": c["boxes"], "sim": s,
             "lean": {k: lo.get(k) for k in ("NBPT", "RNI", "IDRS", "IDEC", "ITRED", "IMPNET", "REVKIRE", "PSNET", "CHRAPRES", "CDHR")},
             "lean_burden": L.burden(c["boxes"], lo) if lo else None,
             "m": {k: mm.get(k) for k in ("NBPT", "RNI", "IDRS", "IDEC", "ITRED", "IRN", "REVKIRE", "PSNET", "CHRAPRES", "CDHR")} if mm else ko.get(c["id"]),
             "m_burden": L.m_burden(c["boxes"], mm) if mm else None}
        f.write(json.dumps(r) + "\n"); f.flush()
        print(c["id"], json.dumps(s)[:300], flush=True)
        time.sleep(1.2)
print("SIM-DONE used", used)
