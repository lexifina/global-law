import glob, gzip, json, random, re, sys
AMT = r"\d{1,3}(?:[  .]\d{3})+(?:,\d{1,2})?|\d+(?:,\d{1,2})?"
PATS = {
 "int_rate": re.compile(r"0,[24]0?\s*%\s*par mois|taux (mensuel )?de 0,[24]", re.I),
 "int_months": re.compile(r"intérêts? de retard[^.;]{0,200}?\b(\d{1,3})\s*mois", re.I),
 "int_amount": re.compile(r"intérêts? de retard[^.;]{0,120}?(" + AMT + r")\s*(?:euros|€)", re.I),
 "majo_soit": re.compile(r"majoration[^.;]{0,200}?(10|40|80|100)\s*%[^.;]{0,200}?(?:soit|s'élevant à|d'un montant de|pour un montant de|à hauteur de)\s*(" + AMT + r")\s*(?:euros|€)", re.I),
}
N = {k: 0 for k in PATS}; S = {k: [] for k in PATS}; tot = ir = 0
for f in glob.glob("data/pen/courts/*.jsonl.gz"):
    for line in gzip.open(f, "rt", encoding="utf-8"):
        r = json.loads(line); tot += 1; t = r["text"]
        if not re.search(r"impôt sur le revenu", t[:6000], re.I): continue
        ir += 1
        for k, p in PATS.items():
            m = p.search(t)
            if m:
                N[k] += 1; a = max(0, m.start() - 150); S[k].append((r["meta"].get("ID") or r["src"], t[a:m.end() + 150].replace("\n", " ")))
print(tot, "decisions;", ir, "income-tax in the first 6000 chars;", N)
random.seed(2)
for k in ["int_rate", "int_months", "majo_soit"]:
    print("=====", k)
    for i, s in random.sample(S[k], min(8, len(S[k]))): print("--", i, s[:550])
