import json, os, sys, time
sys.path.insert(0, os.path.expanduser("~/fr/harness")); sys.dont_write_bytecode = True
from sim_run import post, parse
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs", "sim.jsonl")
b = {"0AC": 1, "0DA": 1975, "1AS": 30000, "3UA": 700000, "3VA": 500000}
page = post(2025, b); s = parse(page)
open(OUT + ".dtr_allow2.html", "w", encoding="latin-1", errors="replace").write(page)
open(OUT, "a").write(json.dumps({"id": "dtr_allow2", "boxes": b, "sim": s}) + "\n")
print(s)
