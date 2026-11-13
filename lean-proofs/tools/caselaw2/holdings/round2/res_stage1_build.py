"""Stage-1 screen batches for resolution candidates (Claude subagents read these). No gold.
Selection: lexical score >= 0.2, or the Supreme Court decision cites a decision on each side, or cites one side and
score >= 0.1.  -> work/res1/batch_XX.md, work/res1/pairs.tsv (pid, issue, scotus_node)"""
import os, collections
import common as C
iss = C.load_issues()
TAG = os.environ.get("RES_TAG", "")
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(C.PRIV, "work", "res_cand_scored%s.tsv" % TAG), encoding="utf-8")]
sel = [r for r in rows if float(r[7]) >= 0.2 or (int(r[4]) and int(r[5])) or (int(r[4]) + int(r[5]) > 0 and float(r[7]) >= 0.1)]
keys = {r[0] for r in sel}; scn = {int(r[1]) for r in sel}
names = C.node_names(scn)
H = C.load_holdings(pred=lambda f: int(f[1]) in scn or f[2] in keys)
meta = C.node_meta({int(f[1]) for f in H}); cs = C.courts()
sc_h = collections.defaultdict(list); side = collections.defaultdict(lambda: {"yes": [], "no": []})
for f in H:
    n = int(f[1])
    if n in scn:
        q = iss[f[2]][4]
        sc_h[n].append(f[3] + (" [question: %s -> %s]" % (q, f[4]) if q != "-" and f[4] in ("yes", "no") else ""))
    if f[2] in keys and f[4] in ("yes", "no") and C.court_kind(cs.get(meta[n][0])) != "scotus":
        side[f[2]][f[4]].append((-float(f[13]), meta[n][1], f[3], cs[meta[n][0]][2]))
by = collections.defaultdict(list)
for r in sel: by[int(r[1])].append(r)
od = os.path.join(C.PRIV, "work", "res1" + TAG); os.makedirs(od, exist_ok=True)
pairs = []; blocks = []
for n in sorted(by):
    nm = names.get(n, ("?", "", ""))
    b = ["## Decision D%d: %s, %s (decided %s)" % (n, nm[0], nm[1].split("|")[0], by[n][0][2]), "Recorded holdings of this decision:"]
    for p in sc_h[n][:10]: b.append("- " + p)
    b.append("Candidate questions:")
    for r in by[n]:
        pid = "P%s%04d" % (TAG, len(pairs)); pairs.append((pid, r[0], n))
        y = sorted(side[r[0]]["yes"])[:1]; no = sorted(side[r[0]]["no"])[:1]
        b.append("- %s: %s" % (pid, iss[r[0]][4]))
        if y: b.append("    yes-side (Cir. %d, %d): %s" % (y[0][3], y[0][1], y[0][2]))
        if no: b.append("    no-side (Cir. %d, %d): %s" % (no[0][3], no[0][1], no[0][2]))
    blocks.append("\n".join(b))
with open(os.path.join(od, "pairs.tsv"), "w", encoding="utf-8", newline="\n") as f:
    for p in pairs: f.write("%s\t%s\t%d\n" % p)
NB = int(os.environ.get("RES_NB", "5")); per = (len(blocks) + NB - 1) // NB
for i in range(NB):
    with open(os.path.join(od, "batch_%02d.md" % i), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n\n".join(blocks[i * per:(i + 1) * per]) + "\n")
print("pairs", len(pairs), "decisions", len(blocks), [os.path.getsize(os.path.join(od, "batch_%02d.md" % i)) for i in range(NB)])
