"""Ask the DGFiP production simulator about the disagreement classes of the other implementations.

usage: flock ~/fr/.sim.lock python3 impl_sim.py   (strictly sequential, 1.2 s apart, resumable)
Cases: runs/impl/sim_cases.jsonl ({id, year, boxes, cls, note}); answers appended to runs/impl/sim.jsonl, raw pages in
runs/impl/sim.jsonl.html/. Uses sim_run.post/parse unchanged. Hard cap: 40 requests for this work in total.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim_run import post, parse

FR = os.path.expanduser("~/fr")
CASES, OUT = f"{FR}/runs/impl/sim_cases.jsonl", f"{FR}/runs/impl/sim.jsonl"
CAP = 40

cases = [json.loads(l) for l in open(CASES)]
done = [json.loads(l) for l in open(OUT)] if os.path.exists(OUT) else []
seen = {(d["id"], d["year"]) for d in done}
sent = len(done)
os.makedirs(OUT + ".html", exist_ok=True)
with open(OUT, "a") as f:
    for c in cases:
        if (c["id"], c["year"]) in seen:
            continue
        if sent >= CAP:
            print("cap reached")
            break
        try:
            page = post(c["year"], c["boxes"])
            open(f"{OUT}.html/{c['id']}_{c['year']}.html", "w", encoding="latin-1", errors="replace").write(page)
            r = parse(page)
        except Exception as e:
            r = {"_error": repr(e)[:200]}
        sent += 1
        f.write(json.dumps({"id": c["id"], "year": c["year"], "sim": r}) + "\n")
        f.flush()
        print(c["id"], c["year"], r, flush=True)
        time.sleep(1.2)
print("requests so far:", sent)
