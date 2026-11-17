"""Group the returns whose result changed between two releases into change clusters.
usage: hist_analyse.py diffs.jsonl summary.json [n_cases]
A cluster = the set of changed 'amount' variables (display LIG*/ZIG* flags and pure indicators are counted apart),
reported with counts per random/targeted tag and examples."""
import json, sys, collections, re
rows = [json.loads(l) for l in open(sys.argv[1])]
disp = lambda v: re.match(r"^(LIG|ZIG|IND|FLAG|NAT|V_|ZONE|DLMRN|ANCNAP|NBLIG)", v) is not None
fam = collections.defaultdict(list)
kinds = collections.Counter()
for r in rows:
    if r["old_refused"] != r["new_refused"]:
        fam[("REFUSAL", f"{r['old_refused']}->{r['new_refused']}")].append(r); continue
    amt = sorted(v for v in r["diff"] if not disp(v))
    if not amt: kinds["display/indicator only"] += 1; fam[("DISPLAY",)].append(r); continue
    kinds["amounts"] += 1
    fam[tuple(amt[:8])].append(r)
print("changed returns:", len(rows), dict(kinds))
for k, rs in sorted(fam.items(), key=lambda x: -len(x[1]))[:60]:
    tags = collections.Counter(t for r in rs for t in (r.get("tags") or []))
    ex = rs[0]
    print(f"\n[{len(rs)}] {k}\n   tags {tags.most_common(4)}\n   e.g. {ex['id']} {json.dumps(ex['boxes'])[:300]}\n   {json.dumps({v: ex['diff'][v] for v in list(ex['diff'])[:10]})[:400]}")
