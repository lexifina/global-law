"""Run the same returns through two releases of the M code (Mlang C builds) and record every output that changes.

usage: hist_pair.py OLD_CAL NEW_CAL YEAR cases.jsonl TGV_NEW outdir [jobs]
cases.jsonl: {"id","boxes":{...}} (+ any tags). Writes outdir/diffs.jsonl (one line per return whose result differs:
restituted variables that differ, refusal on either side) and outdir/summary.json. Scratch output files are deleted
chunk by chunk."""
import json, os, re, subprocess, sys, shutil, tempfile, collections, concurrent.futures as cf
old, new, year, cases_p, tgv, out = sys.argv[1:7]
jobs = int(sys.argv[7]) if len(sys.argv) > 7 else 14
os.makedirs(out, exist_ok=True)
rest = set()
for m in re.finditer(r"^([A-Z0-9_]+)\s*:[^;]*?\brestituee\b", open(tgv, encoding="latin1").read(), re.M | re.S):
    rest.add(m.group(1))
cases = [json.loads(l) for l in open(cases_p)]
def irj(c):
    b = dict(c["boxes"]); b.setdefault("REGCO", 1); b.setdefault("ANREV", int(year))
    return "\n".join(["#NOM", c["id"], "#ENTREES-PRIMITIF"] + [f"{k}/{v}" for k, v in b.items()] +
                     ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
                      "#RESULTATS-CORRECTIF", "##"]) + "\n"
def parse(p):
    v = {}; sec = None
    for line in open(p, errors="replace"):
        line = line.rstrip("\n")
        if line.startswith("#"): sec = line; continue
        if sec == "#RESULTATS-PRIMITIF" and "/" in line:
            k, x = line.split("/", 1)
            if k in rest: v[k] = x
    return v
def ko(stdout):
    r = {}
    cur = None
    for line in stdout.splitlines():
        m = re.search(r"Traitement du fichier (\S+)", line) or re.search(r"(\S+\.irj)", line)
        if m: cur = os.path.basename(m.group(1))[:-4] if m.group(1).endswith(".irj") else cur
        k = re.search(r"KO \| (\S+)", line)
        if k and cur: r.setdefault(cur, k.group(1))
    return r
def chunk(cs):
    d = tempfile.mkdtemp(dir=os.path.expanduser("~/fr/hist/scratch"))
    os.makedirs(f"{d}/in"); os.makedirs(f"{d}/a"); os.makedirs(f"{d}/b")
    fs = []
    for c in cs:
        p = f"{d}/in/{c['id']}.irj"; open(p, "w").write(irj(c)); fs.append(p)
    ra = subprocess.run([old, "-completion", "-m", "p", "-a", year, "-dst", f"{d}/a"] + fs, capture_output=True, text=True)
    rb = subprocess.run([new, "-completion", "-m", "p", "-a", year, "-dst", f"{d}/b"] + fs, capture_output=True, text=True)
    res = []
    for c in cs:
        pa, pb = f"{d}/a/{c['id']}.irj", f"{d}/b/{c['id']}.irj"
        va = parse(pa) if os.path.exists(pa) else None
        vb = parse(pb) if os.path.exists(pb) else None
        ea = None if va and va.get("NBPT") else "refused"
        eb = None if vb and vb.get("NBPT") else "refused"
        diff = {}
        if va is not None and vb is not None:
            for k in set(va) & set(vb):  # variables both releases restitute (new/removed variables are not a change)
                if va[k] != vb[k]: diff[k] = [va[k], vb[k]]
        res.append({"id": c["id"], "old_refused": ea, "new_refused": eb, "diff": diff})
    shutil.rmtree(d)
    return res
os.makedirs(os.path.expanduser("~/fr/hist/scratch"), exist_ok=True)
k = 200
parts = [cases[i:i + k] for i in range(0, len(cases), k)]
byid = {c["id"]: c for c in cases}
n = changed = 0; varc = collections.Counter(); ref = collections.Counter()
with open(f"{out}/diffs.jsonl", "w") as f, cf.ProcessPoolExecutor(jobs) as ex:
    for res in ex.map(chunk, parts):
        for r in res:
            n += 1
            if r["old_refused"] != r["new_refused"]: ref[(r["old_refused"], r["new_refused"])] += 1
            if r["diff"] or r["old_refused"] != r["new_refused"]:
                changed += 1
                for v in r["diff"]: varc[v] += 1
                c = byid[r["id"]]
                f.write(json.dumps({**r, "boxes": c["boxes"], "tags": c.get("tags")}) + "\n")
s = {"returns": n, "changed": changed, "refusal_changes": {f"{a}->{b}": v for (a, b), v in ref.items()},
     "vars": varc.most_common()}
json.dump(s, open(f"{out}/summary.json", "w"), indent=1)
print(f"{n} returns, {changed} with a changed restituted result; top vars {varc.most_common(15)}; refusals {dict(ref)}")
