"""Draw a stratified random sample of decisions and materialise them (from git objects) into a scratch dir.
python sample.py <work-dir> <repos-dir> <out-dir> <per-stratum>"""
import os, random, subprocess, sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
work, repos, out, per = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
courts = {}
for line in open(os.path.join(work, "lean-in-v3/courts_named.tsv"), encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    courts[f[0]] = (f[1], int(f[4]), f[5], f[7])
def stratum(c):
    if c not in courts: return "unmapped"
    name, sysid, tier, rule = courts[c]
    if rule == "scotus" and "District of Columbia" not in name: return "scotus"
    if sysid == 0: return "fed_app" if tier == "A" else "fed_trial_special"
    return {"L": "state_last", "A": "state_app"}.get(tier, "state_trial_special")
pools = defaultdict(list)
with open(os.path.join(work, "graph/nodes.tsv"), encoding="utf-8") as fn, open(os.path.join(work, "lean-in-v3/decisions.tsv"), encoding="utf-8") as fd:
    for a, b in zip(fn, fd):
        n = a.rstrip("\n").split("\t"); d = b.rstrip("\n").split("\t")
        pools[stratum(d[1])].append((n[0], n[1], n[2], d[1], n[4]))
random.seed(20261112)
rows = []
for s, p in sorted(pools.items()):
    print(s, len(p), file=sys.stderr)
    for r in random.sample(p, min(per, len(p))):
        rows.append((s,) + r)
byrepo = defaultdict(list)
for r in rows: byrepo[r[2]].append(r)
os.makedirs(out, exist_ok=True)
man = open(os.path.join(out, "manifest.tsv"), "w", encoding="utf-8", newline="\n")
def fetch(repo):
    items = byrepo[repo]
    inp = "".join("HEAD:%s\n" % r[3] for r in items).encode()
    res = subprocess.run(["git", "-C", os.path.join(repos, repo), "cat-file", "--batch"], input=inp, capture_output=True).stdout
    i = 0; got = []
    for r in items:
        nl = res.index(b"\n", i); hdr = res[i:nl].split(); i = nl + 1
        if len(hdr) < 3 or hdr[1] == b"missing":
            got.append((r, None)); continue
        size = int(hdr[2]); data = res[i:i + size]; i += size + 1
        fn = os.path.join(out, r[0], r[1] + ".md"); os.makedirs(os.path.dirname(fn), exist_ok=True)
        open(fn, "wb").write(data); got.append((r, fn))
    return got
with ThreadPoolExecutor(8) as ex:
    for got in ex.map(fetch, sorted(byrepo)):
        for r, fn in got:
            man.write("\t".join([r[0], r[1], r[2], r[3], r[4], courts.get(r[4], ("?",))[0], r[5], "1" if fn else "0"]) + "\n")
man.close()
