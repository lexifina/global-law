"""diagnosis only: reader picks on the unlinked C8-domain gap nodes vs the h0 node of the gap case (h0-only file)."""
import json, re, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h0check
H = h0check.h0()
def dkc(s): return re.sub(r"[^0-9a-z]", "", s.lower().replace("no.", ""))
nodes = {}
for i, l in enumerate(open("../../data_orders/nodes.tsv", encoding="utf-8")):
    if i: p = l.split("\t"); nodes[p[0]] = p[1]
lids = [x.strip() for x in open("work/diag_lids.txt")]
c = collections.Counter()
for f, off in (("readers/ans_d1.jsonl", 0), ("readers/ans_d2.jsonl", 16)):
    if not os.path.exists(f): continue
    for l in open(f, encoding="utf-8"):
        a = json.loads(l); lid = lids[off + a["item"] - 1]
        dks = {dkc(d) for d in nodes[lid].split(";")}
        h = [n for n, r in H.items() if r["class"] in ("NEG", "PART") and dks & {dkc(d) for d in re.split(r"[;,| ]+", r["sc_dockets"])}]
        k = "pick_none" if a["pick"] in ("none", "unsure") else ("agree_h0" if a["pick"] in map(str, h) else "differ_h0")
        c[(a["category"], k)] += 1
for k, v in sorted(c.items()): print(v, *k)
