"""Split block of eval/score.py on a private out/data dir, without writing eval/results.json.
    python score_splits.py <out dir> <data dir> [splits file name]   (default splits.tsv)
Also writes <out dir>/splits_recall.tsv (per gold row verdict)."""
import os, sys, json, types, shutil
sys.path.insert(0, os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/eval"))
import score
out, data = sys.argv[1], sys.argv[2]
name = sys.argv[3] if len(sys.argv) > 3 else "splits.tsv"
a = types.SimpleNamespace(out=out, data=data)
if name != "splits.tsv":
    tmp = os.path.join(out, "_score_tmp"); os.makedirs(tmp, exist_ok=True)
    shutil.copy(os.path.join(out, name), os.path.join(tmp, "splits.tsv")); a.out = tmp
meta = score.Meta(data)
tables = {}
res = score.score_splits(a, os.path.join(score.C2, "gold"), meta, tables)
with open(os.path.join(out, "splits_recall_%s" % name), "w", encoding="utf-8", newline="\n") as f:
    for r in tables.get("splits_recall", []):
        f.write("\t".join(str(c) for c in r) + "\n")
print(json.dumps(res, indent=1))
