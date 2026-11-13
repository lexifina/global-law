"""Step 1: SCOTUS decision holdings -> candidate (node, family) pairs by keyword pre-filter (recall-oriented; the
extractor confirms). Writes data/factors_work/cands.jsonl and family_counts.tsv (frequency ranking of all candidate
families, from which the factor-based ones were chosen)."""
import collections, json, os, re
from families import FAM
W = os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/data")
OUT = os.path.join(W, "factors_work"); os.makedirs(OUT, exist_ok=True)
CHOSEN = ["fourth_search", "qualified_immunity", "personal_jurisdiction", "standing", "miranda", "agency_deference",
          "dormant_commerce", "takings", "due_process_procedural", "free_speech", "establishment_free_exercise",
          "confrontation", "ineffective_assistance", "preemption", "cruel_unusual"]
P = {k: re.compile(v, re.I) for k, v in FAM.items()}
SCOTUS = 2906
dates = {}
with open(os.path.join(W, "decisions2.tsv"), encoding="utf-8") as f:
    for line in f:
        a = line.split("\t", 4)
        if a[1] == "2906":
            dates[a[0]] = int(a[2])
hold = []
keys = set()
with open(os.path.join(W, "holdings.tsv"), encoding="utf-8") as f:
    for line in f:
        r = line.rstrip("\n").split("\t")
        if r[0].startswith("H") and r[1] in dates:
            hold.append(r); keys.add(r[2])
label = {}
with open(os.path.join(W, "issues.tsv"), encoding="utf-8") as f:
    for line in f:
        r = line.split("\t", 2)
        if r[0] in keys:
            label[r[0]] = r[1]
cand = collections.defaultdict(list)
cnt = collections.Counter()
for r in hold:
    txt = label.get(r[2], "") + " | " + r[3] + " | " + r[9]
    for k, p in P.items():
        if p.search(txt):
            cand[(r[1], k)].append({"id": r[0], "issue": label.get(r[2], ""), "prop": r[3], "quote": r[9][:600],
                                    "start": int(r[7]), "end": int(r[8]), "sha": r[6], "conf": float(r[13])})
fam_dec = collections.Counter(k for (_, k) in cand)
with open(os.path.join(OUT, "family_counts.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("family\tscotus_decisions\tchosen\n")
    for k, n in fam_dec.most_common():
        f.write(f"{k}\t{n}\t{int(k in CHOSEN)}\n")
n = 0
with open(os.path.join(OUT, "cands.jsonl"), "w", encoding="utf-8", newline="\n") as f:
    for (node, k), hs in sorted(cand.items(), key=lambda x: (x[0][1], int(x[0][0]))):
        if k in CHOSEN:
            f.write(json.dumps({"node": int(node), "family": k, "date": dates[node], "holdings": hs}) + "\n"); n += 1
print("scotus holdings", len(hold), "cands", n)
for k in CHOSEN:
    print(k, fam_dec[k])
