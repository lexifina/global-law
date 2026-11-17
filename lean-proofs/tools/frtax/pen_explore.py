import glob, gzip, json, random, re, sys
AMT = re.compile(r"(\d{1,3}(?:[  .]\d{3})+|\d+)(?:,(\d{1,2}))?\s*(?:euros?|€)", re.I)
PEN = re.compile(r"intérêts? de retard|majoration", re.I)
n = k = 0; S = []
for f in glob.glob("data/pen/courts/*.jsonl.gz"):
    for line in gzip.open(f, "rt", encoding="utf-8"):
        r = json.loads(line); n += 1
        sents = re.split(r"(?<=[^\d\s][.;])\s+", r["text"])
        hit = [s for s in sents if PEN.search(s) and len(AMT.findall(s)) >= 2 and re.search(r"\d+\s*%", s)]
        if hit:
            k += 1; S += [(r["meta"].get("ID") or r["src"], s) for s in hit]
print(n, "decisions;", k, "with a penalty sentence holding a rate and two amounts;", len(S), "sentences")
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
for i, s in random.sample(S, 25): print("--", i, s[:600].replace("\n", " "))
