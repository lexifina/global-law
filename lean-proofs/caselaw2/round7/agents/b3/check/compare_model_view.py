"""Check: score_fresh7.py's model view == score_fresh.py (round 5) on the same inputs.

    python compare_model_view.py <ref_dir> <label> <r7_dir>

ref_dir holds score_fresh.py's <label>.json, .pairs.tsv, .unlisted_sample.tsv; r7_dir holds fresh7_dev.json etc.
"""
import json
import os
import sys

ref, label, r7 = sys.argv[1:4]
a = json.load(open(os.path.join(ref, label + ".json"), encoding="utf-8"))
b = json.load(open(os.path.join(r7, "fresh7_dev.json"), encoding="utf-8"))
ok = True
for key in ("recall", "precision_side"):
    same = a[key] == b["views"]["model"][key]
    ok &= same
    print(key, "identical" if same else "DIFFERENT")
for k in ("status_rows", "status_sha1", "findings", "treatments"):
    same = a["inputs"][k] == b["inputs"][k]
    ok &= same
    print("inputs." + k, "identical" if same else "DIFFERENT")
for suf, suf7 in ((".pairs.tsv", ".model.pairs.tsv"), (".unlisted_sample.tsv", ".model.unlisted_sample.tsv")):
    x = open(os.path.join(ref, label + suf), "rb").read()
    y = open(os.path.join(r7, "fresh7_dev" + suf7), "rb").read()
    print(suf, "byte-identical" if x == y else "DIFFERENT")
    ok &= x == y
s = b["views"]["model"]["recall"]["all"]["all"]
t = b["views"]["attributed"]["recall"]["all"]["all"] if "attributed" in b["views"] else None
print("model all: strict %d/%d lenient %d/%d" % (s["strict"]["k"], s["n"], s["lenient"]["k"], s["n"]))
if t:
    print("attributed all: strict %d/%d lenient %d/%d" % (t["strict"]["k"], t["n"], t["lenient"]["k"], t["n"]))
print("ALL IDENTICAL" if ok else "MISMATCH")
sys.exit(0 if ok else 1)
