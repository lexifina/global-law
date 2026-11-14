"""Print the cue neighbourhoods of B for failing pre-check rows (diagnosis only)."""
import os
import pickle
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "cert_remand", "precheck.tsv"), encoding="utf-8")]
fails = [r for r in rows if r[2] == "fail" and r[3] == "remandTie"]
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
pick = random.sample(fails, 6)
orders = {o["n"]: o for o in pickle.load(open(os.path.join(C2, "round6/history/rules/memo/work/orders.pkl"), "rb"))["orders"]}
bs = [int(re.search(r"B=(\d+)", r[4]).group(1)) for r in pick]
tx = L.fetch_texts(bs)
for r, b in zip(pick, bs):
    o = orders[int(r[0].split(":")[1])]
    print("=" * 100)
    print(r[0], "O date", o["date"], "docket", o["docket"], "cites", o["cites"], "caps", o["caps"])
    t = tx[b][1]
    for m in re.finditer(r"Supreme\s+Court", t):
        w = t[max(0, m.start() - 350):m.end() + 350]
        if re.search(r"vacat|remand|in light of|further consideration", w, re.I):
            print("---", m.start())
            print(w.replace("\n", " "))
            break
