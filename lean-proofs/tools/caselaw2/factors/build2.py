"""v2 step 3: verified readings -> data/factors.tsv (atomic replace; v1 kept as factors.v1.tsv), factor_vocab.tsv,
factor_cases.tsv, and the overlay work/horty_real (sub-family issues horty:<subfamily>, anchors per sub-family).
A factor is kept only if marked present with a quote that is an exact substring of the decision text (checked inside
one excerpt segment, each of which is text[s:e] of the normalised decision text). A case enters factors.tsv only if it
has at least one reason factor (Horty: every precedent has a reason)."""
import collections, json, os, shutil
from common import W, WORK, FAMILIES
from verify2 import V2, SUBS, SIDX
LEAN2 = os.path.dirname(W); OV = os.path.join(LEAN2, "work", "horty_real"); D = os.path.join(OV, "data")
fid = {}
for s in SUBS:
    fam = next(f for f in FAMILIES if s in V2[f])
    for i, f in enumerate(s["factors"]):
        fid[SIDX[s["key"]] * 100 + i + 1] = (s["key"], fam, f["side"], f["name"], f["definition"])
ex = {(j["node"], j["family"]): j["excerpt"] for j in map(json.loads, open(os.path.join(WORK, "excerpts.jsonl"), encoding="utf-8"))}
date = {(int(r[1]), r[2]): int(r[5]) for r in (l.rstrip("\n").split("\t") for l in open(os.path.join(W, "factor_cases.v1.tsv"), encoding="utf-8"))}
st = collections.Counter(); cases = []; seen = set()
for l in open(os.path.join(WORK, "verify2.jsonl"), encoding="utf-8"):
    try:
        j = json.loads(l)
    except json.JSONDecodeError:
        continue
    k = (j["node"], j["family"]); o = j.get("out") or {}
    if k in seen or "error" in o or not o:
        continue
    seen.add(k); st["read"] += 1
    sub = o.get("subfamily")
    if sub not in SIDX or sub not in [s["key"] for s in V2[j["family"]]]:
        st["subfamilyNone"] += 1; continue
    if not o.get("decides") or o.get("outcome") not in ("yes", "no"):
        st["notDecidedOrUnclear"] += 1; continue
    win = "pi" if o["outcome"] == "yes" else "delta"
    segs = ex[k].split("\n[...]\n")
    fs = {}
    for f in o.get("factors", []):
        i = f.get("id")
        if i not in fid or fid[i][0] != sub:
            st["factorBadId"] += 1; continue
        if not f.get("present"):
            st["factorAbsent"] += 1; continue
        q = (f.get("quote") or "").strip().strip('"“”').strip()
        if len(q) < 8 or not any(q in s for s in segs):
            st["factorQuoteNotExact"] += 1; continue
        inr = bool(f.get("in_reason"))
        if inr and fid[i][2] != win:
            st["reasonWrongSideCleared"] += 1; inr = False
        st["factorKept"] += 1
        fs[i] = (inr, q)
    if not fs:
        st["noFactors"] += 1; continue
    has_r = any(r for r, _ in fs.values())
    st["withReason" if has_r else "noReason"] += 1
    cases.append({"hid": j["v1_hid"], "node": j["node"], "family": j["family"], "sub": sub, "outcome": o["outcome"],
                  "date": date[k], "factors": fs, "inF": int(has_r), "model": j.get("model")})
cases.sort(key=lambda c: (SIDX[c["sub"]], c["date"], c["hid"]))
def wr(path, rows):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    os.replace(tmp, path)
wr(os.path.join(W, "factors.tsv"), [(c["hid"], i, fid[i][2], int(r)) for c in cases if c["inF"] for i, (r, _) in sorted(c["factors"].items())])
wr(os.path.join(W, "factor_vocab.tsv"), [(i, s, fam, side, n, d.replace("\t", " "), "gpt-6.1-sol:factor_vocab2") for i, (s, fam, side, n, d) in sorted(fid.items())])
wr(os.path.join(W, "factor_cases.tsv"), [(c["hid"], c["node"], c["sub"], "horty:" + c["sub"], c["outcome"], c["date"], len(c["factors"]),
    ",".join(str(i) for i, (r, _) in sorted(c["factors"].items()) if r) or "-", c["inF"], c["model"], c["family"]) for c in cases])
wr(os.path.join(WORK, "factor_quotes.tsv"), [(c["hid"], i, int(r), q.replace("\t", " ").replace("\n", " ")) for c in cases for i, (r, q) in sorted(c["factors"].items())])
bysub = collections.Counter(c["sub"] for c in cases if c["inF"])
json.dump({"stats": st, "by_subfamily": bysub}, open(os.path.join(WORK, "build2_stats.json"), "w"), indent=1)
print(dict(st)); print("in factors.tsv:", sum(c["inF"] for c in cases), "subfamilies with >=2 cases:", sum(1 for v in bysub.values() if v >= 2))
# ---- overlay (Lean run pending WDAC)
chosen = {c["hid"]: c for c in cases if c["inF"]}
shutil.copyfile(os.path.join(W, "factors.tsv"), os.path.join(D, "factors.tsv"))
anchor = None
with open(os.path.join(W, "holdings.tsv"), encoding="utf-8") as f, open(os.path.join(D, "holdings.tsv"), "w", encoding="utf-8", newline="\n") as g:
    for line in f:
        r = line.rstrip("\n").split("\t")
        if r[0] in chosen:
            r[2] = "horty:" + chosen[r[0]]["sub"]; r[4] = chosen[r[0]]["outcome"]
        if r[0] == "H517902.0":
            anchor = list(r)
        g.write("\t".join(r) + "\n")
    for s in SUBS:
        a = list(anchor); a[0] = "A." + s["key"]; a[2] = "horty:" + s["key"]; a[4] = "yes"; g.write("\t".join(a) + "\n")
with open(os.path.join(W, "issues.tsv"), encoding="utf-8") as f, open(os.path.join(D, "issues.tsv"), "w", encoding="utf-8", newline="\n") as g:
    for line in f:
        g.write(line)
    for s in SUBS:
        g.write("\t".join(["horty:" + s["key"], "Horty sub-family: " + s["key"], "federalGeneral", "-", s["question"].replace("\t", " "), "factors:gpt-6.1-sol"]) + "\n")
print("overlay written", D)
