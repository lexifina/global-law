"""Round 5: verification packs for the loose Supreme Court tier (T1f).

The T1f packs were pre-screened by a smaller Claude model (answers in ans_prescreen/). Only the items it marked
`states: true` are re-read here by the main model: this script copies those items, unchanged, into
packs/pack_T1v_<nnn>.md. The verification answers go to ans/ans_pack_T1v_<nnn>.jsonl and are the only T1f answers
that are certified (the pre-screen answers are never certified).
"""
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
items = {}
for p in sorted(glob.glob(os.path.join(HERE, "packs", "pack_T1f_*.md"))):
    t = open(p, encoding="utf-8").read()
    parts = re.split(r"(?m)^### ITEM ", t)
    for b in parts[1:]:
        i = b.split("\n", 1)[0].strip()
        items[i] = "### ITEM " + b.rstrip() + "\n"
pos, seen, nfiles, nans = [], set(), 0, 0
for p in sorted(glob.glob(os.path.join(HERE, "ans_prescreen", "ans_pack_T1f_*.jsonl"))):
    nfiles += 1
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            a = json.loads(l)
        except ValueError:
            continue
        nans += 1
        if a.get("states") is True and a.get("id") in items and a["id"] not in seen:
            seen.add(a["id"])
            pos.append(a["id"])
head = open(sorted(glob.glob(os.path.join(HERE, "packs", "pack_T1f_*.md")))[0], encoding="utf-8").read().split("### ITEM ", 1)[0]
n = 0
for k in range(0, len(pos), 45):
    n += 1
    with open(os.path.join(HERE, "packs", "pack_T1v_%03d.md" % n), "w", encoding="utf-8", newline="\n") as f:
        f.write(head)
        for i in pos[k:k + 45]:
            f.write(items[i] + "\n")
print("prescreen files %d, answers %d, positives %d, verification packs %d" % (nfiles, nans, len(pos), n))
