"""Penalty study: decisions whose operative part (dispositif) discharges a majoration on its own (not "droits et
pénalités" following a reduction of the base), by penalty kind and year, with the reason found in the penalty section.
Writes data/pen/court_penalty_discharges.jsonl. Usage: python3 -I harness/pen_courts_outcomes.py"""
import glob, gzip, json, re, collections
DISP = re.compile(r"D\s*[EÉ]\s*C\s*I\s*D\s*E\s*:|DÉCIDE\s*:|décide\s*:", re.I)
ONLY = re.compile(r"(?:décharg\w*|dégrèvement|déchargés?)\s+(?:de\s+la|des|de)\s+(?:majorations?|pénalités?|amendes?)(?:\s+(?:de|pour|prévues?|au\s+titre|dont|appliquées?|mises?))", re.I)
NOTRIGHTS = re.compile(r"droits\s+et\s+(?:des\s+)?(?:pénalités|majorations)|pénalités\s+correspondant", re.I)
SUBST = re.compile(r"substitu\w+[^.]{0,200}(?:majoration|pénalité|intérêts?\s+de\s+retard)|ramen\w+\s+(?:au\s+taux\s+de\s+|à\s+)40\s*%|(?:limitée?|réduite?)\s+à\s+(?:la\s+majoration\s+de\s+)?40\s*%", re.I)
KIND = {"1729a_deliberate": r"manquement\s+délibéré", "1729c_fraud": r"man(?:œ|oe)uvres?\s+frauduleuses?", "1729b_abuse": r"abus\s+de\s+droit",
        "1728_late": r"1728|défaut\s+de\s+déclaration|dépôt\s+tardif|mise\s+en\s+demeure", "1728c_occult": r"activité\s+occulte",
        "1758A": r"1758\s*A", "1732": r"opposition|1732", "1730": r"1730|recouvrement", "1727_interest": r"intérêts?\s+de\s+retard",
        "art1729": r"1729\b", "rate10": r"\b10\s*%", "rate40": r"\b40\s*%", "rate80": r"\b80\s*%", "rate100": r"\b100\s*%"}
REASON = {"burden_not_met": r"n'(?:établit|apporte)\s+pas|ne\s+justifie\s+pas|ne\s+démontre\s+pas|n'est\s+pas\s+établi",
          "motivation": r"motiv\w+[^.;]{0,80}(?:insuffisan|irréguli)|L\.?\s*80\s*D|n'est\s+pas\s+(?:suffisamment\s+)?motivée?",
          "substitution": SUBST.pattern, "procedure": r"procédure\s+contradictoire|irrégularité\s+de\s+la\s+procédure",
          "remise_or_degrevement": r"remise|dégrèvement\s+(?:a\s+été\s+)?prononcé"}
REASON = {k: re.compile(v, re.I) for k, v in REASON.items()}
PENSEC = re.compile(r"(?:Sur|En ce qui concerne|S'agissant de?s?|Quant aux)\s+(?:les\s+|la\s+)?(?:pénalités|majorations?|amendes?)", re.I)
out = open("data/pen/court_penalty_discharges.jsonl", "w", encoding="utf-8")
seen = set(); tot = 0; C = collections.Counter(); R = collections.Counter(); Y = collections.Counter(); S = 0
for f in sorted(glob.glob("data/pen/courts/*.jsonl.gz")):
    for line in gzip.open(f, "rt", encoding="utf-8"):
        r = json.loads(line); meta = r["meta"]; t = r["text"]
        court = (meta.get("JURIDICTION") or meta.get("Nom_Juridiction") or "").strip()
        dd = (meta.get("DATE_DEC") or meta.get("Date_Lecture") or "").strip()[:10]
        no = (meta.get("NUMERO") or meta.get("Numero_Dossier") or "").strip()
        if (court.lower()[:30], dd, no) in seen: continue
        seen.add((court.lower()[:30], dd, no))
        if not re.search(r"impôt\s+sur\s+le\s+revenu", t[:6000], re.I): continue
        m = DISP.search(t)
        if not m: continue
        tot += 1
        disp = t[m.end(): m.end() + 2500]
        hits = [x for x in ONLY.finditer(disp) if not NOTRIGHTS.search(disp[max(0, x.start() - 60): x.end() + 60])]
        sub = bool(SUBST.search(disp))
        if not hits and not sub: continue
        ctx = " ".join(disp[max(0, x.start() - 40): x.end() + 250] for x in hits) or disp[:600]
        kinds = [k for k, p in KIND.items() if re.search(p, ctx, re.I)]
        sec = "".join(t[s.start(): s.start() + 5000] for s in PENSEC.finditer(t))
        reasons = [k for k, p in REASON.items() if p.search(sec)]
        row = {"court": court, "date": dd, "number": no, "kinds": kinds, "substitution_in_disp": sub, "reasons": reasons, "disp": ctx[:700]}
        out.write(json.dumps(row, ensure_ascii=False) + "\n")
        S += 1; C.update(kinds or ["unspecified"]); R.update(reasons or ["none found"]); Y[dd[:4]] += 1
print(tot, "IR decisions with a dispositif;", S, "discharge or reduce a penalty on its own")
print("kinds:", C.most_common()); print("reasons:", R.most_common()); print("years:", sorted(Y.items())[-10:])
