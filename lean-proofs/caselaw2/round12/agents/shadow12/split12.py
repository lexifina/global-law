"""split build12 node rows into delta classes: c8 (+ corpus cap-C8 rows), sub, newnodes (C6/K9 pairs not in v11d),
recert (C6/K9 pairs of v11d on CHANGED.tsv nodes) + work/drop_recert.txt (their v11d h11 ids)."""
import json, os, sys
C2 = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
N0 = 6892454
lids = [l.split("\t")[0] for l in list(open(os.path.join(C2, "round12/data_orders/nodes.tsv"), encoding="utf-8"))[1:]]
changed = {l.split("\t")[0] for l in list(open(os.path.join(C2, "round12/data_orders/CHANGED.tsv"), encoding="utf-8"))[1:]}
old = {}
for line in open(os.path.join(C2, "round11/stage/v11d/history.tsv"), encoding="utf-8"):
    p = line.split("\t", 5)
    old[(int(p[2]), int(p[1]), p[4])] = p[0]
out = {k: [] for k in ("c8", "sub", "newnodes", "recert")}
drop = []
for f in sys.argv[1:]:
    for l in open(f, encoding="utf-8"):
        r = json.loads(l)
        tag = r["rule"].split(":")[1]
        key = (r["by"], r["target"], r["kind"])
        if tag in ("cap-C8", "olist-C8"):
            out["c8"].append(r)
        elif tag.startswith("olist-sub-"):
            out["sub"].append(r)
        elif key in old:
            if N0 <= r["by"] < N0 + len(lids) and lids[r["by"] - N0] in changed:
                out["recert"].append(r)
                drop.append(old[key])
        else:
            out["newnodes"].append(r)
for k, rows in out.items():
    with open("rows_%s.jsonl" % k, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(k, len(rows))
open("work/drop_recert.txt", "w", newline="\n").write("".join(x + "\n" for x in sorted(drop)))
print("drop", len(drop))
