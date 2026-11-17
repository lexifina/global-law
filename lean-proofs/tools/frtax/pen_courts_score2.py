"""Penalty study, step 3b: candidate court statements of penalty figures, scored against the statute, for review.
Majorations: a rate R, a labelled majoration amount Y and the nearest labelled base X before it in the same paragraph
(Y != X, 0 < Y/X <= 1.05). Interest: a labelled interest amount I, the nearest labelled base X before it, the income
year N (one year named in the paragraph or the decision) and the proposition de rectification date P (one date named):
statute = X x sum of monthly rates from 1 July N+1 to the month of P (art. 1727, IV, 1 and 4; 0,75 % to 2005,
0,40 % 2006-2017, 0,20 % from 2018). Writes data/pen/court_candidates.jsonl.
Usage: python3 -I harness/pen_courts_score2.py"""
import glob, gzip, json, re, sys
sys.path.insert(0, "harness")
from datetime import date
AMT = r"\d{1,3}(?:[   .]\d{3})+(?:,\d{1,2})?|\d+(?:,\d{1,2})?"
EUR = r"\s*(?:euros?|€|EUR)\b"
def num(s): return float(re.sub(r"[   .]", "", s).replace(",", "."))
MONTHS = {m: i + 1 for i, m in enumerate(["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                                          "septembre", "octobre", "novembre", "décembre"])}
DATE = r"(1er|\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+((?:19|20)\d\d)"
LAB = r"(?:soit|d'un\s+montant\s+(?:total\s+)?de|s'élevant\s+à|pour\s+un\s+montant\s+(?:total\s+)?de|à\s+hauteur\s+de|représentant|égale?\s+à|de\s+la\s+somme\s+de)"
MAJO = re.compile(r"(?:majorations?|pénalités?)\s+(?:de\s+|au\s+taux\s+de\s+)(10|20|40|80|100)\s*%[^€;]{0,160}?" + LAB + r"\s+(?P<y>" + AMT + ")" + EUR, re.I)
BASE = re.compile(r"(?:droits(?:\s+(?:simples|éludés|rappelés|supplémentaires|en\s+principal))?|rappels?(?:\s+d'impôt(?:\s+sur\s+le\s+revenu)?)?|suppléments?\s+d'impôt|"
                  r"impositions?\s+supplémentaires?|cotisations?\s+supplémentaires?(?:\s+d'impôt\s+sur\s+le\s+revenu)?|"
                  r"montant\s+des\s+droits|impôt\s+(?:sur\s+le\s+revenu\s+)?(?:éludé|dû|supplémentaire))"
                  r"[^€;]{0,60}?(?:de|à|s'élevant\s+à|d'un\s+montant\s+de|pour\s+un\s+montant\s+de|soit)\s+(?P<x>" + AMT + ")" + EUR, re.I)
INTAMT = re.compile(r"intérêts?\s+de\s+retard[^€;]{0,100}?(?:" + LAB + r"|de)\s+(?P<i>" + AMT + ")" + EUR, re.I)
PROP = re.compile(r"propositions?\s+de\s+rectification\s+(?:du|en\s+date\s+du|datée\s+du|adressée\s+le|notifiée\s+le)\s+" + DATE, re.I)
YEAR = re.compile(r"au\s+titre\s+de\s+l'année\s+((?:19|20)\d\d)", re.I)
def pdate(d, m, y): return date(int(y), MONTHS[m], 1 if d == "1er" else int(d))
def monthly(y): return 0.75 if y < 2006 else (0.40 if y < 2018 else 0.20)
def rate_sum(a, b):
    s = 0.0; y, m = a.year, a.month; n = 0
    while (y, m) <= (b.year, b.month):
        s += monthly(y); n += 1; m += 1
        if m == 13: y, m = y + 1, 1
    return s, n
def nearest_base(p, pos, exclude):
    best = None
    for b in BASE.finditer(p[:pos]):
        x = num(b.group("x"))
        if x != exclude: best = x
    return best
out = open("data/pen/court_candidates.jsonl", "w", encoding="utf-8")
seen = set(); n_m = n_i = 0
for f in sorted(glob.glob("data/pen/courts/*.jsonl.gz")):
    for line in gzip.open(f, "rt", encoding="utf-8"):
        r = json.loads(line); meta = r["meta"]; t = r["text"]
        court = (meta.get("JURIDICTION") or meta.get("Nom_Juridiction") or "").strip()
        dd = (meta.get("DATE_DEC") or meta.get("Date_Lecture") or "").strip()[:10]
        no = (meta.get("NUMERO") or meta.get("Numero_Dossier") or "").strip()
        if (court.lower()[:30], dd, no) in seen: continue
        seen.add((court.lower()[:30], dd, no))
        if not re.search(r"impôt\s+sur\s+le\s+revenu", t[:6000], re.I): continue
        dyears = sorted(set(YEAR.findall(t))); dprops = sorted(set(PROP.findall(t)))
        for p in re.split(r"\n+", t):
            if not (40 < len(p) < 3000): continue
            for m in MAJO.finditer(p):
                R = int(m.group(1)); y = num(m.group("y")); x = nearest_base(p, m.start(), y)
                if not x or not (0 < y / x <= 1.05): continue
                exp = round(R / 100 * x + 1e-9)
                out.write(json.dumps({"kind": "majoration", "court": court, "date": dd, "number": no, "rate": R, "base": x,
                                      "stated": y, "computed": exp, "diff": round(y - exp, 2), "implied_rate": round(100 * y / x, 2),
                                      "text": p[max(0, m.start() - 500): m.end() + 200]}, ensure_ascii=False) + "\n"); n_m += 1
            for m in INTAMT.finditer(p):
                i = num(m.group("i")); x = nearest_base(p, m.start(), i)
                if not x or not (0 < i / x <= 0.6): continue
                ys = sorted(set(YEAR.findall(p))) or dyears
                ps = sorted(set(PROP.findall(p))) or dprops
                rec = {"kind": "interest", "court": court, "date": dd, "number": no, "base": x, "stated": i,
                       "implied_pct": round(100 * i / x, 3), "years": ys, "props": [str(pdate(*q)) for q in ps]}
                if len(ys) == 1 and len(ps) == 1:
                    N = int(ys[0]); P = pdate(*ps[0]); s, nmo = rate_sum(date(N + 1, 7, 1), P)
                    rec.update(months=nmo, rate_sum=round(s, 2), computed=round(x * s / 100 + 1e-9), diff=round(i - round(x * s / 100 + 1e-9), 2))
                rec["text"] = p[max(0, m.start() - 500): m.end() + 200]
                out.write(json.dumps(rec, ensure_ascii=False) + "\n"); n_i += 1
print(n_m, "majoration candidates;", n_i, "interest candidates")
