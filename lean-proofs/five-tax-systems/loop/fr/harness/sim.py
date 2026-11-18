"""Production simulator checks for the headline returns (~/fr/harness/sim_run.py post/parse; sequential, 1.2 s
apart; run under flock ~/fr/.sim.lock). Saves ../runs/sim.jsonl with frloop's answer alongside."""
import json, os, sys, time
sys.path.insert(0, os.path.expanduser("~/fr/harness"))
sys.dont_write_bytecode = True
from sim_run import post, parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib as L
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs", "sim.jsonl")
S = {"0AC": 1, "0DA": 1975}
CD2 = dict(S, **{"1AJ": 150000, "2DC": 800000, "2BH": 800000})
BAND = dict(S, **{"1AJ": 30000, "2DC": 290000, "2BH": 290000})
cases = [
    ("cd2", CD2, None), ("cd2_pme", dict(CD2, **{"7CF": 50000}), {"PME": 50000}),
    ("cd2_pme_hh", dict(CD2, **{"7CF": 50000, "7DB": 12000}), {"PME": 50000}),
    ("band", BAND, None), ("band_def", dict(BAND, **{"4BC": 10700}), None),
    ("dtr_base", dict(S, **{"1AS": 30000, "3VG": 700000}), None),
    ("dtr_allow", dict(S, **{"1AS": 30000, "3VG": 200000, "3VA": 500000}), None),
]
done = {json.loads(l)["id"] for l in open(OUT)} if os.path.exists(OUT) else set()
with open(OUT, "a") as f:
    for cid, b, x in cases:
        if cid in done:
            continue
        try:
            s = parse(post(2025, b))
        except Exception as e:
            s = {"_error": repr(e)[:200]}
        lb = {k: v for k, v in b.items() if k != "3VA"}
        if cid == "dtr_allow":
            lb["2EE"] = 500000
        lo = L.one(lb, x)
        f.write(json.dumps({"id": cid, "boxes": b, "extra": x, "sim": s, "lean": lo}) + "\n"); f.flush()
        print(cid, {k: s.get(k) for k in ("IRNET", "ITRED", "CEHR", "CDHR", "REVKIRE", "PAYER", "_error")},
              "| lean", lo["IMPNET"], lo["ITRED"], lo["CHRAPRES"], lo["CDHR"], lo["REVKIRE"], flush=True)
        time.sleep(1.2)
