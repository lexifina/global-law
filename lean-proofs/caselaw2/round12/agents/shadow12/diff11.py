"""compare round-12 node rows (C6/K9/C8 on round12/data_orders) with v11d's h11 rows by order nodes; CHANGED.tsv nodes."""
import json, os, sys, collections
C2 = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
N0 = 6892454
lids = [l.split("\t")[0] for l in open(os.path.join(C2, "round12/data_orders/nodes.tsv"), encoding="utf-8")][1:]
nid = {N0 + i: l for i, l in enumerate(lids)}
changed = {l.split("	")[0] for l in list(open(os.path.join(C2, "round12/data_orders/CHANGED.tsv"), encoding="utf-8"))[1:]}
old = {}
for line in open(os.path.join(C2, "round11/stage/v11d/history.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    b = int(p[2])
    if N0 <= b < N0 + len(lids):
        old[(b, int(p[1]))] = (p[0], p[3] if len(p) > 3 else "")
new = {}
for l in open(sys.argv[1], encoding="utf-8"):
    r = json.loads(l)
    new[(r["by"], r["target"])] = r
c = collections.Counter()
drop, keep_new = [], []
for k, v in old.items():
    ch = nid[k[0]] in changed
    if k in new:
        c["old_same_pair_changed" if ch else "old_same_pair"] += 1
        if ch:
            drop.append(v[0]); keep_new.append(new[k])
    else:
        c["old_lost_changed" if ch else "old_lost_unchanged"] += 1
        if ch:
            drop.append(v[0])
        print("LOST", v[0], nid[k[0]], "changed" if ch else "", k)
oldby = {k[0] for k in old}
for k, r in new.items():
    if k in old:
        continue
    ch = nid[k[0]] in changed
    tag = r["rule"].split(":")[1]
    c["new_%s_%s%s" % (tag, "changed" if ch else "unchanged", "_byhadrow" if k[0] in oldby else "")] += 1
    if tag != "olist-C8":
        keep_new.append(r)
        print("NEWPAIR", tag, nid[k[0]], "changed" if ch else "", k, "old by row" if k[0] in oldby else "")
print(dict(sorted(c.items())))
print("changed nodes", len(changed), "with v11d rows", len({k[0] for k in old if nid[k[0]] in changed}))
os.makedirs("work", exist_ok=True)
open("work/drop_h11_changed.txt", "w", newline="\n").write("".join(x + "\n" for x in sorted(drop)))
with open("rows_recert.jsonl", "w", newline="\n") as f:
    for r in keep_new:
        f.write(json.dumps(r) + "\n")
print("drop", len(drop), "recert/new C6-K9 rows", len(keep_new))
