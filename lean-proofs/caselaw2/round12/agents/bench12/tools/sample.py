import csv, random, sys, os
B = sys.argv[1]
key = [r for r in csv.DictReader(open(os.path.join(B, "key.tsv"), encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE) if r["status"] == "linked"]
resid = {}
dist = {}
for line in open(os.path.join(B, "work", "dist_nodes.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t"); dist[p[0]] = p
random.seed(12)
s = random.sample(key, 20) + random.sample([r for r in key if r["reviewed"] == "1"], 10)
need = {r["idb_idx"] for r in s}
for line in open(os.path.join(B, "work", "idb_resid.tsv"), encoding="latin-1"):
    p = line.split("\t", 6)
    if p[0] in need: resid[p[0]] = p
apps = {r["app_node"] for r in s if r["app_node"]}
an = {}
for i, line in enumerate(open(sys.argv[2], encoding="utf-8")):
    p = line.split("\t")
    if p[0] in apps: an[p[0]] = (p[4], p[6][:60])
for r in s:
    d = dist[r["dist_node"]]
    q = resid[r["idb_idx"]]
    print("%s %s rv=%s %s | IDB %s v %s dd=%s app=%s judg=%s | DIST %s %s [%s] %s | APP %s" % (
        r["class"], r["via"], r["reviewed"], r["dtype"], q[5], q[6].split("\t")[0], r["ddocket"], r["appdate"], r["judgdate"],
        d[5], d[6][:50], d[7][:40], d[2], an.get(r["app_node"], "-")))
