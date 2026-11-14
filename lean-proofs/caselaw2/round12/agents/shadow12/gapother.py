"""diagnosis (h0-only file): gap cases linked to another decision -> which rule, candidate dates."""
import collections, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h0check
H = h0check.h0()
def dkc(s): return re.sub(r"[^0-9a-z]", "", s.lower().replace("no.", ""))
gap = {n: r for n, r in H.items() if r["class"] in ("NEG", "PART") and r["sc_in_corpus"] == "no"}
lk = {}
for line in open(sys.argv[1], encoding="utf-8"):
    p = line.rstrip("\n").split("\t"); lk.setdefault(p[0], []).append(p)
by_dk = collections.defaultdict(list)
for line in open(os.path.join(sys.argv[2], "nodes.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    for d in p[1].split(";"): by_dk[dkc(d)].append(p[0])
for n, r in gap.items():
    dks = [dkc(d) for d in re.split(r"[;,| ]+", r["sc_dockets"]) if dkc(d)]
    for lid in {l for d in dks for l in by_dk.get(d, ())}:
        for p in lk.get(lid, []):
            if p[2] != "-" and p[2] != str(n):
                print("OTHER", lid, "h0node", n, r["node_date"], "linked", p[2], p[6], r["title"][:60])
            if p[6].startswith("c8_none") or p[6] == "no_both_sides":
                print("UNL", p[6], lid, "h0node", n, r["node_date"], r["title"][:70])
