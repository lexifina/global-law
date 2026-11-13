"""Step 5: recompute Spec.Horty.consistent per family base in Python (mirror of the Lean definitions), using the
runner's status.tsv for good law at asOf, and compare with the runner's inconsistentBindingBase findings.
Writes factors_work/horty_bases.tsv and factors_work/conflicts.jsonl (every conflicting pair)."""
import collections, json, os, sys
from common import W, WORK
OUT = sys.argv[1] if sys.argv[1:] else os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/work/horty_real/out")
ASOF = 20261112
side = {}
fac = collections.defaultdict(list)
for l in open(os.path.join(W, "factors.tsv"), encoding="utf-8"):
    h, f, s, r = l.rstrip("\n").split("\t")
    fac[h].append((int(f), s, r == "1"))
cases = {}
for l in open(os.path.join(W, "factor_cases.tsv"), encoding="utf-8"):
    r = l.rstrip("\n").split("\t")
    if r[0] not in fac:  # v2: cases without a reason factor are not in factors.tsv
        continue
    cases[r[0]] = {"hid": r[0], "node": int(r[1]), "family": r[2], "outcome": "pi" if r[4] == "yes" else "delta", "date": int(r[5])}
good = {}
if not os.path.exists(os.path.join(OUT, "status.tsv")):  # provisional (no Lean): explicit overrulings only
    nodes = {str(c["node"]): h for h, c in cases.items()}
    for l in open(os.path.join(W, "treatments.tsv"), encoding="utf-8"):
        r = l.split("	", 9)
        if r[2] in nodes and r[4] in ("overruled", "abrogated") and r[5] == "all" and r[7] == "1":
            good[nodes[r[2]]] = "neg:" + r[4]
for l in (open(os.path.join(OUT, "status.tsv"), encoding="utf-8") if os.path.exists(os.path.join(OUT, "status.tsv")) else []):
    r = l.rstrip("\n").split("\t")
    if len(r) > 6 and r[2] in cases and r[4] == str(ASOF):
        good[r[2]] = r[5]
def fc(c):
    X = {(f, s) for f, s, _ in fac[c["hid"]]}
    R = {(f, s) for f, s, r in fac[c["hid"]] if r}
    return X, R
def conflict(a, b):
    (Xa, Ra), (Xb, Rb) = fc(a), fc(b)
    return a["outcome"] != b["outcome"] and Rb <= Xa and Ra <= Xb
fams = collections.defaultdict(list)
for c in cases.values():
    if good.get(c["hid"], "good") == "good":
        fams[c["family"]].append(c)
    else:
        fams["_neg"].append(c)
runner = set()
fp = os.path.join(OUT, "findings.tsv")
for l in (open(fp, encoding="utf-8") if os.path.exists(fp) else []):
    r = l.rstrip("\n").split("\t")
    if r[0] == "inconsistentBindingBase":
        runner.add(r[3].replace("horty:", ""))
rows, confl = [], []
for fam in sorted(f for f in fams if f != "_neg"):
    cs = sorted(fams[fam], key=lambda c: c["date"])
    pairs = [(a, b) for i, a in enumerate(cs) for b in cs[i + 1:] if conflict(a, b)]
    involved = {c["hid"] for p in pairs for c in p}
    # largest consistent sub-base by greedy removal of the most-conflicted case
    live = set(c["hid"] for c in cs); deg = collections.Counter()
    for a, b in pairs: deg[a["hid"]] += 1; deg[b["hid"]] += 1
    P = [(a["hid"], b["hid"]) for a, b in pairs]; removed = 0
    while True:
        d = collections.Counter()
        for x, y in P:
            if x in live and y in live: d[x] += 1; d[y] += 1
        if not d: break
        live.discard(d.most_common(1)[0][0]); removed += 1
    nemp = sum(1 for c in cs if not any(r for _, _, r in fac[c["hid"]]))
    rows.append((fam, len(cs), sum(c["outcome"] == "pi" for c in cs), int(not pairs), len(pairs), len(involved), removed, nemp,
                 int(fam in runner), int((not pairs) == (fam not in runner))))
    for a, b in pairs:
        confl.append({"family": fam, "a": a["hid"], "b": b["hid"], "a_date": a["date"], "b_date": b["date"],
                      "a_out": a["outcome"], "b_out": b["outcome"]})
hdr = "family\tcases_good\tcases_yes\tconsistent\tconflicting_pairs\tcases_in_conflict\tremove_to_consistent\tcases_empty_reason\trunner_inconsistent\tagree"
with open(os.path.join(WORK, "horty_bases.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write(hdr + "\n"); [f.write("\t".join(map(str, r)) + "\n") for r in rows]
with open(os.path.join(WORK, "conflicts.jsonl"), "w", encoding="utf-8", newline="\n") as f:
    [f.write(json.dumps(c) + "\n") for c in confl]
print(hdr); [print("\t".join(map(str, r))) for r in rows]
print("not good law at asOf:", len(fams["_neg"]), collections.Counter(good[c["hid"]] for c in fams["_neg"]))
