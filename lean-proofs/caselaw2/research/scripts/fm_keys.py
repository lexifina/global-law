import os, sys, collections, json
S = sys.argv[1]
man = [l.rstrip("\n").split("\t") for l in open(os.path.join(S, "manifest.tsv"), encoding="utf-8")]
keys = collections.defaultdict(collections.Counter); tot = collections.Counter(); vals = collections.defaultdict(collections.Counter)
src = collections.defaultdict(collections.Counter)
for r in man:
    fn = os.path.join(S, r[0], r[1] + ".md")
    t = open(fn, encoding="utf-8", errors="replace").read()
    end = t.find("\n---", 3); fm = t[3:end]
    tot[r[0]] += 1
    ks = set()
    for line in fm.splitlines():
        if line[:1] in " -" or ":" not in line: continue
        k, _, v = line.partition(":"); ks.add(k)
        if k in ("precedential_status", "decision_type", "reporter", "source", "opinion_types", "type", "status", "per_curiam", "en_banc"):
            vals[k][v.strip()[:60]] += 1
    for k in ks: keys[r[0]][k] += 1
    src[r[0]]["CL" if "courtlistener" in t[:end].lower() else ("CAP" if "case.law" in t[:end].lower() or "Caselaw Access" in t[:end] else "other")] += 1
allk = collections.Counter()
for s in keys: allk.update(keys[s])
strata = sorted(tot)
print("key\t" + "\t".join(strata))
for k, _ in allk.most_common():
    print(k + "\t" + "\t".join("%.1f" % (100 * keys[s][k] / tot[s]) for s in strata))
print("N\t" + "\t".join(str(tot[s]) for s in strata))
for s in strata: print("SRC", s, dict(src[s]))
for k in vals: print("VAL", k, vals[k].most_common(25))
