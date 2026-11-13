"""Step 7: 30 accepted cases (2 per family) for blind reading: excerpt, question, vocabulary, and the claimed outcome
and factors (no model, confidence or ids of the reader). -> factors_work/val/batch{1,2,3}.md + key.json"""
import json, os, random, collections
from common import W, WORK, FAMILIES
from verify2 import SUBS, SIDX
vocab = {s["key"]: s for s in SUBS}
ex = {(j["node"], j["family"]): j["excerpt"] for j in map(json.loads, open(os.path.join(WORK, "excerpts.jsonl"), encoding="utf-8"))}
cases = [l.rstrip("\n").split("\t") for l in open(os.path.join(W, "factor_cases.tsv"), encoding="utf-8")]
fac = collections.defaultdict(list)
for l in open(os.path.join(W, "factors.tsv"), encoding="utf-8"):
    h, f, s, r = l.rstrip("\n").split("\t"); fac[h].append((int(f), s, r == "1"))
fname = {}
for k, v in vocab.items():
    for i, f in enumerate(v["factors"]):
        fname[SIDX[k] * 100 + i + 1] = (f["name"], f["definition"], f["side"])
cases = [c for c in cases if c[8] == "1"]
rnd = random.Random(23)
sel = []
for fam in FAMILIES:
    cs = [c for c in cases if c[10] == fam]; rnd.shuffle(cs); sel += cs[:2]
rnd.shuffle(sel)
os.makedirs(os.path.join(WORK, "val2"), exist_ok=True)
key = []
for b in range(3):
    out = ["# Blind check of factor extractions (batch %d)\n" % (b + 1),
           "For each item: read the excerpt and judge each CLAIMED factor: is it present in this case's facts as the Court "
           "describes them (definition given)? If marked REASON, did the Court rely on it as a reason for its answer? "
           "Also judge the claimed outcome (the Court's answer to the question, polarity as phrased) and whether the Court "
           "actually decides that question here.\n"]
    for k, c in enumerate(sel[b * 10:(b + 1) * 10]):
        item = f"{b + 1}.{k + 1}"
        v = vocab[c[2]]
        fl = []
        for j, (f, s, r) in enumerate(sorted(fac[c[0]])):
            n, d, sd = fname[f]
            fl.append(f"  - F{j + 1}: **{n}** ({'favours yes' if sd == 'pi' else 'favours no'}): {d}{'  — claimed REASON' if r else ''}")
        key.append({"item": item, "hid": c[0], "family": c[2], "factors": [[f, r] for f, s, r in sorted(fac[c[0]])]})
        out += [f"\n## Item {item}\n", f"Question: {v['question']}\n", f"Claimed: the Court decides it, answer **{c[4].upper()}**.\n",
                "Claimed factors:\n" + "\n".join(fl) + "\n", "Excerpt:\n\n```text\n" + ex[(int(c[1]), c[10])] + "\n```\n"]
    open(os.path.join(WORK, "val2", f"batch{b + 1}.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out))
json.dump(key, open(os.path.join(WORK, "val2", "key.json"), "w"), indent=1)
print(len(key))
