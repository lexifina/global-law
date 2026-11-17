"""Penalty study: court decisions that state a penalty figure together with what it was computed from.
Reads the penalty decisions (data/pen/courts/*.jsonl.gz), splits each into paragraphs and keeps statements where
(a) a majoration rate, a labelled base (rights) and a labelled majoration amount appear together, or
(b) an interest amount appears with its base and its period (dates), or with its rate and number of months, or
(c) a total rate of interest is stated with its months (e.g. "0,40 % x 43 mois = 17,20 %").
Each statement is scored against the statute (the same arithmetic as lean/FrTax/Penalties.lean: majo = rnd(R x base),
interest = rnd(base x sum of monthly rates), months counted from the start month to the stop month inclusive).
Writes data/pen/court_scored.jsonl and prints a summary. Decisions are named by court, date and number only.
Usage: python3 -I harness/pen_courts_score.py"""
import glob, gzip, json, re
from datetime import date
AMT = r"\d{1,3}(?:[   .]\d{3})+(?:,\d{1,2})?|\d+(?:,\d{1,2})?"
EUR = r"\s*(?:euros?|€|EUR)"
def num(s): return float(re.sub(r"[   .]", "", s).replace(",", "."))
MONTHS = {m: i + 1 for i, m in enumerate(["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                                          "septembre", "octobre", "novembre", "décembre"])}
DATE = r"(1er|\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+((?:19|20)\d\d)"
MAJO = re.compile(r"(?:majorations?|pénalités?)\s+(?:de\s+|au\s+taux\s+de\s+)(10|20|40|80|100)\s*%"
                  r"(?P<mid>[^€]{0,260}?)(?:soit|d'un\s+montant\s+(?:total\s+)?de|s'élevant\s+à|pour\s+un\s+montant\s+(?:total\s+)?de|"
                  r"à\s+hauteur\s+de|représentant|égale?\s+à|de)\s+(?:la\s+somme\s+de\s+)?(?P<y>" + AMT + ")" + EUR, re.I)
BASE = re.compile(r"(?:droits(?:\s+(?:simples|éludés|rappelés|supplémentaires))?|rappels?(?:\s+d'impôt)?|suppléments?\s+d'impôt|"
                  r"impositions?\s+supplémentaires?|cotisations?\s+supplémentaires?(?:\s+d'impôt\s+sur\s+le\s+revenu)?|"
                  r"montant\s+des\s+droits|impôt\s+(?:sur\s+le\s+revenu\s+)?(?:éludé|dû|supplémentaire))"
                  r"[^€;]{0,80}?(?:de|à|s'élevant\s+à|d'un\s+montant\s+de|pour\s+un\s+montant\s+de|soit)\s+(?P<x>" + AMT + ")" + EUR, re.I)
INTAMT = re.compile(r"intérêts?\s+de\s+retard[^€;]{0,140}?(?:soit|d'un\s+montant\s+(?:total\s+)?de|s'élevant\s+à|pour\s+un\s+montant\s+(?:total\s+)?de|"
                    r"à\s+hauteur\s+de|de|représentant)\s+(?:la\s+somme\s+de\s+)?(?P<i>" + AMT + ")" + EUR, re.I)
PERIOD = re.compile(r"(?:du|à\s+compter\s+du|depuis\s+le|courant\s+du)\s+" + DATE + r"\s+(?:au|jusqu'au)\s+" + DATE, re.I)
RATEMONTHS = re.compile(r"(\d{1,3})\s+mois[^.;]{0,80}?0,([24]|75)0?\s*%|0,([24]|75)0?\s*%[^.;]{0,80}?(\d{1,3})\s+mois", re.I)
TOTRATE = re.compile(r"(?:soit|taux\s+(?:global|total|cumulé)\s+de|au\s+taux\s+de)\s+(\d{1,2},\d{1,2})\s*%", re.I)
def pdate(d, m, y): return date(int(y), MONTHS[m], 1 if d == "1er" else int(d))
def monthly(y, m):
    """art. 1727 III: 0,75 % until 2005, 0,40 % 2006-2017, 0,20 % from 2018 (percent)."""
    return 0.75 if y < 2006 else (0.40 if y < 2018 else 0.20)
def rate_sum(a, b):
    s = 0.0; y, m = a.year, a.month
    while (y, m) <= (b.year, b.month):
        s += monthly(y, m); m += 1
        if m == 13: y, m = y + 1, 1
    return s, (b.year - a.year) * 12 + b.month - a.month + 1
def paragraphs(t):
    return [p for p in re.split(r"\n+", t) if 40 < len(p) < 3000]
def main():
    out = open("data/pen/court_scored.jsonl", "w", encoding="utf-8")
    seen = set(); stats = {}
    for f in sorted(glob.glob("data/pen/courts/*.jsonl.gz")):
        for line in gzip.open(f, "rt", encoding="utf-8"):
            r = json.loads(line); meta = r["meta"]; t = r["text"]
            court = (meta.get("JURIDICTION") or meta.get("Nom_Juridiction") or "").strip()
            dd = (meta.get("DATE_DEC") or meta.get("Date_Lecture") or "").strip()[:10]
            no = (meta.get("NUMERO") or meta.get("Numero_Dossier") or "").strip()
            if (court.lower()[:30], dd, no) in seen: continue
            seen.add((court.lower()[:30], dd, no))
            if not re.search(r"impôt\s+sur\s+le\s+revenu", t[:6000], re.I): continue
            for p in paragraphs(t):
                recs = []
                for m in MAJO.finditer(p):
                    R = int(m.group(1)); y = num(m.group("y"))
                    bases = [num(b.group("x")) for b in BASE.finditer(p[:m.end()])]
                    bases += [num(b.group("x")) for b in BASE.finditer(m.group("mid") or "")]
                    if not bases or y <= 0: continue
                    x = bases[-1]
                    exp = round(R / 100 * x + 1e-9)
                    recs.append({"kind": "majoration", "rate": R, "base": x, "stated": y, "computed": exp,
                                 "match": abs(exp - y) <= 1, "ratio": round(y / x * 100, 3) if x else None})
                for m in INTAMT.finditer(p):
                    i = num(m.group("i"))
                    per = PERIOD.search(p)
                    bases = [num(b.group("x")) for b in BASE.finditer(p)]
                    rec = {"kind": "interest", "stated": i}
                    if per:
                        g = per.groups(); a = pdate(g[0], g[1], g[2]); b = pdate(g[3], g[4], g[5])
                        s, n = rate_sum(a, b); rec.update(period=[str(a), str(b)], months=n, rate_sum=round(s, 2))
                    rm = RATEMONTHS.search(p)
                    if rm and "months" not in rec:
                        n = int(rm.group(1) or rm.group(4)); rr = rm.group(2) or rm.group(3)
                        rr = 0.75 if rr == "75" else int(rr) / 10
                        rec.update(months=n, rate_sum=round(n * rr, 2))
                    if bases and "rate_sum" in rec:
                        x = bases[0]; exp = round(x * rec["rate_sum"] / 100 + 1e-9)
                        rec.update(base=x, computed=exp, match=abs(exp - i) <= 1, implied_months=round(i / x / 0.002, 2) if x else None)
                        recs.append(rec)
                for m in TOTRATE.finditer(p):
                    rm = RATEMONTHS.search(p)
                    if rm and re.search(r"intérêts?\s+de\s+retard", p, re.I):
                        n = int(rm.group(1) or rm.group(4)); rr = rm.group(2) or rm.group(3)
                        rr = 0.75 if rr == "75" else int(rr) / 10
                        tot = num(m.group(1))
                        recs.append({"kind": "interest_rate", "months": n, "monthly": rr, "stated": tot,
                                     "computed": round(n * rr, 2), "match": abs(n * rr - tot) < 0.006})
                for rec in recs:
                    rec.update(court=court, date=dd, number=no, text=p[:1500])
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    k = rec["kind"]; s = stats.setdefault(k, [0, 0]); s[0] += 1; s[1] += rec["match"]
    print({k: f"{v[1]}/{v[0]} match" for k, v in stats.items()})
main()
