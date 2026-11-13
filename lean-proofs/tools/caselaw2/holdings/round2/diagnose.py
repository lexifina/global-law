"""Task 1: classify gold misses and after-resolution rows (measure only; gold is read here and nowhere else).
    python diagnose.py <out dir> [data dir] [dest tsv]  -> round2/splits_misses.tsv (+ counts on stdout)
Needs <out dir>/splits_recall_splits.tsv (score_splits.py)."""
import sys, os, collections, json
import common as C
out = sys.argv[1]
data = sys.argv[2] if len(sys.argv) > 2 else C.DATA
dst = sys.argv[3] if len(sys.argv) > 3 else os.path.join(C.C2, "round2", "splits_misses.tsv")
iss = C.load_issues(data)
cs = C.courts(data)
gold = []
hdr = None
for l in open(os.path.join(C.C2, "gold", "splits_resolved.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    if hdr is None:
        hdr = f
        continue
    r = dict(zip(hdr, f))
    if r["statutory"] == "1":
        gold.append(r)
verdict = {}
for l in open(os.path.join(out, "splits_recall_splits.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    verdict[(f[0], f[2])] = f[4]
# holdings with a US Code section
hs = C.load_holdings(data, lambda f: iss.get(f[2], [0, 0, 0, "-"])[3] != "-")
nodes = {int(f[1]) for f in hs} | {int(g["node"]) for g in gold}
for g in gold:
    nodes |= {int(x) for x in g["conflict_nodes"].split(",") if x.isdigit()}
meta = C.node_meta(nodes, data)
by_sec = collections.defaultdict(list)
by_node = collections.defaultdict(list)
for f in hs:
    n = int(f[1])
    m = meta.get(n)
    if not m:
        continue
    c = cs.get(m[0])
    h = dict(hid=f[0], node=n, issue=f[2], answer=f[4], split=f[2].startswith("usc:"), kind=C.court_kind(c),
             circ=c[2] if c else 0, date=m[1], pub=m[2], conf=float(f[13]), usc=iss[f[2]][3])
    by_sec[C.sect(h["usc"])].append(h)
    by_node[n].append(h)
allh_node = collections.defaultdict(list)
gn = {int(g["node"]) for g in gold}
for f in C.load_holdings(data, lambda f: int(f[1]) in gn):
    allh_node[int(f[1])].append(f)
sp = collections.defaultdict(list)
for l in open(os.path.join(out, "splits.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    sp[C.sect(iss[f[0]][3])].append((f[0], int(f[1]), int(f[2]), int(f[5])))
rows = [["part", "scotus_node", "date", "name", "usc", "gold_circuits", "class", "detail"]]
cnt = collections.Counter()
cnt2 = collections.Counter()
for g in gold:
    d = int(g["date"])
    u = g["usc"]
    s = C.sect(u)
    node = int(g["node"])
    v = verdict.get((g["node"], u), "?")
    if v != "missed":
        continue
    H = [h for h in by_sec.get(s, []) if h["kind"] == "coa" and h["date"] < d]
    S = [h for h in H if h["split"] and h["answer"] in ("yes", "no")]
    cn = [int(x) for x in g["conflict_nodes"].split(",") if x.isdigit()]
    cn_read = sum(1 for x in cn if any(h["split"] for h in by_node.get(x, [])))
    det = "gold_conflict_nodes=%d read_as_split=%d coa_split_holdings=%d coa_local_holdings=%d" % (
        len(cn), cn_read, len(S), len(H) - len(S))
    anyS = any(h["split"] for h in by_sec.get(s, []))
    if not S:
        if not anyS:
            cls = "A1 section not read for splits; no circuit holdings name the section" if not H else \
                  "A2 section not read for splits; circuit decision-local holdings exist (no question, answer -)"
        else:
            cls = "A3 section read, but no court-of-appeals split holding before the resolution date"
    else:
        circs = {h["circ"] for h in S}
        byk = collections.defaultdict(list)
        for h in S:
            byk[h["issue"]].append(h)
        shared = {k: v for k, v in byk.items() if len({h["circ"] for h in v}) >= 2}
        opp = {k: v for k, v in shared.items()
               if any(a["answer"] != b["answer"] and a["circ"] != b["circ"] for a in v for b in v)}
        if len(circs) < 2:
            cls = "B only one circuit extracted on the section before resolution"
        elif not shared:
            cls = "C holdings of >=2 circuits, no shared issue key (not clustered)"
        elif not opp:
            cls = "D shared issue key, answers not opposite as coded"
        else:
            pubopp = any(a["answer"] != b["answer"] and a["circ"] != b["circ"] and a["pub"] == "published"
                         and b["pub"] == "published" for v in opp.values() for a in v for b in v)
            cls = "E opposite answers on a shared key, no engine row (%s)" % (
                "status/force" if pubopp else "a side unpublished")
        det += " circuits=%s keys=%d shared=%d" % (",".join(map(str, sorted(circs))), len(byk), len(shared))
    cnt[cls] += 1
    rows.append(["missed", g["node"], g["date"], g["name"], u, g["circuits"], cls, det])
for g in gold:
    d = int(g["date"])
    u = g["usc"]
    s = C.sect(u)
    node = int(g["node"])
    for (issue, c1, c2, sd) in sp.get(s, []):
        if sd < d:
            continue
        mine = allh_node.get(node, [])
        on_key = [f for f in mine if f[2] == issue]
        on_sec = [f for f in mine if f[2].startswith("usc:") and C.sect(iss[f[2]][3]) == s]
        if not mine:
            cls = "R1 resolving decision has no holdings row"
        elif on_key:
            cls = "R4 resolving decision holds on this key; the split arose later (date/order or status)"
        elif on_sec:
            cls = "R2 resolving decision has split holdings on the section under other issue keys"
        else:
            cls = "R3 resolving decision has only decision-local holdings (answer -)"
        cnt2[cls] += 1
        rows.append(["after_resolution", g["node"], g["date"], g["name"], u, g["circuits"], cls,
                     "split=%s courts=%d,%d split_date=%d scotus_rows=%d" % (issue, c1, c2, sd, len(mine))])
with open(dst, "w", encoding="utf-8", newline="\n") as f:
    for r in rows:
        f.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")
print(json.dumps({"missed": dict(sorted(cnt.items())), "missed_total": sum(cnt.values()),
                  "after_resolution": dict(sorted(cnt2.items())), "after_total": sum(cnt2.values())}, indent=1))
