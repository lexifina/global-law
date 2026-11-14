"""Sample reader-rejected candidate sentences of one repo that name a case and use an explicit own-act form.

    python -X utf8 peek_rejects.py <repo> [n]
"""
import gzip, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common8 import RW  # noqa: E402

repo = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
rej = {}
with gzip.open(os.path.join(RW, "res", repo + ".rejects.tsv.gz"), "rt", encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        rej[p[0]] = p[1]
CASE = re.compile(r"\b[A-Z][A-Za-z.'’]+\s+(?:v\.|vs\.?)\s+[A-Z]|\b\d{1,4}\s+[A-Z][A-Za-z. ]{1,20}\s\d{1,5}\b")
ACT = re.compile(r"\b(?:is|are|be|was)\b[^.]{0,60}?\b(?:overruled|disapproved)\b", re.I)
pool = {}
with gzip.open(os.path.join(RW, "cand", repo + ".jsonl.gz"), "rt", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r["t"] != "c":
            continue
        cid = "%d:%d" % (r["n"], r["s0"])
        why = rej.get(cid)
        if not why:
            continue
        s = r["w"][r["s0"] - r["w0"]:r["s1"] - r["w0"]]
        if CASE.search(s) and ACT.search(s):
            pool.setdefault(why, []).append((cid, s))
for k, v in sorted(pool.items(), key=lambda kv: -len(kv[1])):
    print("==", k, len(v))
    random.seed(1)
    for cid, s in random.sample(v, min(n, len(v))):
        print(" ", cid, "|", s[:400].replace("\n", " "))
