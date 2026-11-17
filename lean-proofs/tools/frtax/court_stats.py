"""Courts as test cases: funnel and scoreboard tables for COURTS.md (Markdown on stdout).
usage: python3 -I harness/court_stats.py"""
import collections, glob, json, os

H = os.path.expanduser("~/fr")
D, R = f"{H}/data/court", f"{H}/runs/court"
sc = [json.loads(l) for l in open(f"{D}/scan_counts.jsonl")]
jade = [s for s in sc if s["archive"].startswith("Freemium")]
ja = [s for s in sc if not s["archive"].startswith("Freemium")]
print("| Corpus | Scanned | Mention income tax | Stage A kept |\n|---|---|---|---|")
for name, s in (("DILA JADE dump (2026-11-08)", jade), ("Justice administrative open data (CE/CAA/TA 2021-2026)", ja)):
    print(f"| {name} | {sum(x['scanned'] for x in s):,} | {sum(x['ir'] for x in s):,} | {sum(x['kept'] for x in s):,} |")
print(f"| **Total** | {sum(x['scanned'] for x in sc):,} | {sum(x['ir'] for x in sc):,} | {sum(x['kept'] for x in sc):,} |")
cass = [json.loads(l) for l in open(f"{D}/cass_scan.jsonl")]
print("\n| Cour de cassation dump | Scanned | Mention income tax | + tax fraud | + computation words |\n|---|---|---|---|---|")
for c in cass:
    print(f"| {c['archive']} | {c['scanned']:,} | {c['ir']:,} | {c['fraud_ir']:,} | {c['with_figures']} |")
fb = json.load(open(f"{D}/funnel_stage_b.json"))
print("\nStage B:", json.dumps(fb))
cand = [json.loads(l) for l in open(f"{D}/candidates.jsonl")]
print("stage B candidates", len(cand), "2015+", sum(any(2015 <= y <= 2025 for y in c["years"]) for c in cand),
      "2020+", sum(any(2020 <= y <= 2025 for y in c["years"]) for c in cand))
liq = sum(1 for _ in open(f"{D}/features_liq.jsonl"))
print("liquidation second pass kept", liq)
tri = collections.Counter()
per = {}
for f in sorted(glob.glob(f"{D}/triage_b*.tsv")):
    b = os.path.basename(f)[7:-4]
    cnt = collections.Counter(l.split("\t")[1].strip() for l in open(f) if l.strip())
    per[b] = cnt
    tri.update(cnt)
keys = ["usable_full", "usable_partial", "no_program_figure", "facts_insufficient", "other_tax", "procedural", "duplicate"]
print("\n| Batch | Read | " + " | ".join(keys) + " |\n|---|---|" + "---|" * len(keys))
for b, cnt in per.items():
    print(f"| {b} | {sum(cnt.values())} | " + " | ".join(str(cnt.get(k, 0)) for k in keys) + " |")
print(f"| **all** | {sum(tri.values())} | " + " | ".join(str(tri.get(k, 0)) for k in keys) + " |")
cases = [json.loads(l) for l in open(f"{D}/cases.jsonl")]
scored = [c for c in cases if c.get("court_figures")]
print("\ncases", len(cases), "from decisions", len({c["source_id"] for c in cases}), "with scorable figures", len(scored),
      "from decisions", len({c["source_id"] for c in scored}), "excluded", sum(1 for c in cases if c.get("excluded")))
print("completeness", collections.Counter(c.get("completeness") for c in scored))
print("years", sorted(collections.Counter(c["income_year"] for c in scored).items()))
print("topics", collections.Counter(c.get("topic") for c in scored).most_common())
rows = json.load(open(f"{R}/scores.json"))
print("figures scored", len(rows))
for prog in ("lean", "m", "prod"):
    st = collections.Counter(r.get(prog, {}).get("status") for r in rows if prog in r)
    pr = collections.Counter(r.get(prog, {}).get("status") for r in rows if prog in r and r.get("proxy"))
    print(prog, dict(st), "of which on a proxy year:", dict(pr))
print("\n| Figure | n | Lean | M | Production |\n|---|---|---|---|---|")
by = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
for r in rows:
    for p in ("lean", "m", "prod"):
        s = r.get(p, {}).get("status")
        if s in ("match", "mismatch"):
            by[r["key"]][p][s] += 1
n_by = collections.Counter(r["key"] for r in rows)
for k in sorted(by, key=lambda k: -n_by[k]):
    cell = lambda p: (f"{by[k][p]['match']}/{by[k][p]['match'] + by[k][p]['mismatch']}" if by[k][p] else "—")  # noqa: E731
    print(f"| {k} | {n_by[k]} | {cell('lean')} | {cell('m')} | {cell('prod')} |")
tot = {p: (sum(by[k][p]["match"] for k in by), sum(sum(by[k][p].values()) for k in by)) for p in ("lean", "m", "prod")}
print("| **all** | %d | %d/%d | %d/%d | %d/%d |" % (len(rows), *tot["lean"], *tot["m"], *tot["prod"]))
