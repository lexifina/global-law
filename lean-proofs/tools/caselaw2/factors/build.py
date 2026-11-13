"""Step 4: accepted extractions -> data/factors.tsv (SCHEMA D9), data/factor_vocab.tsv, data/factor_cases.tsv, and the
Horty run overlay work/horty_real/data (hard links to data/ plus: family issues `horty:<family>` with the question, the
chosen holdings re-keyed onto them with the extracted answer, one Second Circuit anchor holding per family so that a
SCOTUS-bound court is examined, and treatment scopes naming a chosen holding's original issue extended to the family)."""
import json, os, shutil, collections
from common import W, WORK, FAMILIES
LEAN2 = os.path.dirname(W)
OV = os.path.join(LEAN2, "work", "horty_real")
vocab = json.load(open(os.path.join(WORK, "vocab.json"), encoding="utf-8"))
cands = {(c["node"], c["family"]): c for c in map(json.loads, open(os.path.join(WORK, "cands.jsonl"), encoding="utf-8"))}
fid = {}  # factor id -> (family, side, name, definition)
for fam, v in vocab.items():
    for i, f in enumerate(v["factors"]):
        fid[FAMILIES[fam][0] * 100 + i + 1] = (fam, f["side"], f["name"], f["definition"])
stats = collections.Counter()
used = set()
cases = []
recs = [json.loads(l) for l in open(os.path.join(WORK, "extract.jsonl"), encoding="utf-8")]
recs.sort(key=lambda r: (r["node"], list(FAMILIES).index(r["family"])))
seen = set()
for r in recs:
    k = (r["node"], r["family"])
    if k in seen:
        continue
    seen.add(k)
    o = r.get("out") or {}
    stats["read"] += 1
    if "error" in o or not o:
        stats["error"] += 1; continue
    if not o.get("decides"):
        stats["notDecides"] += 1; continue
    if o.get("outcome") not in ("yes", "no"):
        stats["unclear"] += 1; continue
    ids = [h["id"] for h in cands[k]["holdings"]]
    hid = o.get("holding_id") if o.get("holding_id") in ids else None
    if hid is None or hid in used:
        alt = [i for i in ids if i not in used]
        if not alt:
            stats["noHolding"] += 1; continue
        stats["holdingSubstituted"] += 1
        hid = alt[0]
    win = "pi" if o["outcome"] == "yes" else "delta"
    fs = {}
    for f in o.get("factors", []):
        i = f.get("id")
        if i not in fid or fid[i][0] != r["family"]:
            stats["factorBadId"] += 1; continue
        inr = bool(f.get("in_reason"))
        if inr and fid[i][1] != win:
            stats["reasonWrongSideDropped"] += 1; inr = False
        fs[i] = fs.get(i, False) or inr
    if not fs:
        stats["noFactors"] += 1; continue
    used.add(hid)
    stats["accepted"] += 1
    cases.append({"hid": hid, "node": r["node"], "family": r["family"], "date": cands[k]["date"], "outcome": o["outcome"],
                  "factors": fs, "conf": o.get("confidence", 0), "model": r.get("model")})
cases.sort(key=lambda c: (c["family"], c["date"], c["hid"]))
def w(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write("\t".join(str(x) for x in row) + "\n")
w(os.path.join(W, "factors.tsv"), [(c["hid"], i, fid[i][1], int(inr)) for c in cases for i, inr in sorted(c["factors"].items())])
w(os.path.join(W, "factor_vocab.tsv"), [(i, fam, side, name, d.replace("\t", " "), "gpt-6.1-sol:factor_vocab")
                                       for i, (fam, side, name, d) in sorted(fid.items())])
w(os.path.join(W, "factor_cases.tsv"),
  [(c["hid"], c["node"], c["family"], "horty:" + c["family"], c["outcome"], c["date"], len(c["factors"]),
    ",".join(str(i) for i, x in sorted(c["factors"].items()) if x) or "-", c["conf"], c["model"]) for c in cases])
json.dump({"stats": stats, "by_family": collections.Counter(c["family"] for c in cases)},
          open(os.path.join(WORK, "build_stats.json"), "w"), indent=1)
print(dict(stats))
# ---- overlay
os.makedirs(os.path.join(OV, "data"), exist_ok=True); os.makedirs(os.path.join(OV, "edges"), exist_ok=True)
open(os.path.join(OV, "edges", "edges-00.tsv"), "w").close()
D = os.path.join(OV, "data")
for name in ["courts2.tsv", "succession.tsv", "adoption.tsv", "system_rules.tsv", "decisions2.tsv", "history.tsv",
             "cert_text.tsv", "holdings_cert_text.tsv", "marks.tsv", "lawchanges.tsv", "supersessions.tsv"]:
    dst = os.path.join(D, name)
    if os.path.exists(dst):
        os.remove(dst)
    os.link(os.path.join(W, name), dst)
shutil.copyfile(os.path.join(W, "factors.tsv"), os.path.join(D, "factors.tsv"))
chosen = {c["hid"]: c for c in cases}
orig_issue = {}
anchor = None
ca2 = set()
with open(os.path.join(W, "decisions2.tsv"), encoding="utf-8") as f:
    for line in f:
        a = line.split("\t", 6)
        if a[1] == "272" and a[5] == "published":
            ca2.add(a[0])
targets = set()
for fn in ("history.tsv", "treatments.tsv"):
    with open(os.path.join(W, fn), encoding="utf-8") as f:
        for line in f:
            targets.add(line.split("\t", 3)[1 if fn == "history.tsv" else 2])
with open(os.path.join(W, "holdings.tsv"), encoding="utf-8") as f, open(os.path.join(D, "holdings.tsv"), "w", encoding="utf-8", newline="\n") as g:
    for line in f:
        r = line.rstrip("\n").split("\t")
        if r[0] in chosen:
            c = chosen[r[0]]
            orig_issue[r[2]] = "horty:" + c["family"]
            r[2] = "horty:" + c["family"]; r[4] = c["outcome"]
        elif anchor is None and r[0].startswith("H") and r[1] in ca2 and r[1] not in targets and r[5] == "majority":
            anchor = list(r)
        g.write("\t".join(r) + "\n")
    for fam in vocab:
        a = list(anchor); a[0] = "A." + fam; a[2] = "horty:" + fam; a[4] = "yes"
        g.write("\t".join(a) + "\n")
with open(os.path.join(W, "issues.tsv"), encoding="utf-8") as f, open(os.path.join(D, "issues.tsv"), "w", encoding="utf-8", newline="\n") as g:
    for line in f:
        g.write(line)
    for fam, v in vocab.items():
        g.write("\t".join(["horty:" + fam, "Horty family: " + fam, "federalGeneral", "-", v["question"].replace("\t", " "),
                           "factors:gpt-6.1-sol"]) + "\n")
nsc = 0
with open(os.path.join(W, "treatments.tsv"), encoding="utf-8") as f, open(os.path.join(D, "treatments.tsv"), "w", encoding="utf-8", newline="\n") as g:
    for line in f:
        r = line.rstrip("\n").split("\t")
        if r[5].startswith("issues:"):
            ks = r[5][7:].split(",")
            add = [orig_issue[k] for k in ks if k in orig_issue]
            if add:
                r[5] = "issues:" + ",".join(ks + sorted(set(add))); nsc += 1
        g.write("\t".join(r) + "\n")
print("cases", len(cases), "anchor from", anchor[0], "scoped treatments extended", nsc)
