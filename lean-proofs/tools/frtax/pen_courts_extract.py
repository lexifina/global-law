"""Penalty study: structured extraction from the income-tax penalty decisions (data/pen/courts/*.jsonl.gz).
Writes data/pen/court_decisions.jsonl (one row per decision: court, date, number, years, penalties discussed,
outcome on penalties, reason) and data/pen/court_figures.jsonl (stated figures: majoration rate + base + amount,
interest base + period + amount, interest rate + months), each with the sentence it came from.
Decisions are referred to by court, date and number only.
Usage: python3 -I harness/pen_courts_extract.py"""
import glob, gzip, json, re
from datetime import date
AMT = r"\d{1,3}(?:[   .]\d{3})+(?:,\d{1,2})?|\d+(?:,\d{1,2})?"
EUR = r"\s*(?:euros?|€)"
def num(s): return float(re.sub(r"[   .]", "", s).replace(",", "."))
MONTHS = {m: i + 1 for i, m in enumerate(["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                                          "septembre", "octobre", "novembre", "décembre"])}
DATE = r"(1er|\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+((?:19|20)\d\d)"
def pdate(d, m, y): return date(int(y), MONTHS[m], 1 if d == "1er" else int(d))
KINDS = {
    "1729_a_deliberate": r"manquement\s+délibéré|majoration\s+de\s+40\s*%\s+(prévue\s+)?(au\s+a\s+de|par\s+le\s+a\s+de)",
    "1729_b_abuse": r"abus\s+de\s+droit",
    "1729_c_fraud": r"man(?:œ|oe)uvres?\s+frauduleuses?",
    "1728_late": r"article\s+1728|défaut\s+de\s+(dépôt|déclaration)|dépôt\s+tardif|mise\s+en\s+demeure",
    "1728_occult": r"activité\s+occulte",
    "1758A": r"1758\s*A",
    "1732_opposition": r"opposition\s+(au|à\s+(un\s+)?)\s*contrôle|1732",
    "1730_late_payment": r"1730|majoration\s+de\s+10\s*%\s+pour\s+(retard\s+de\s+)?paiement",
    "1727_interest": r"intérêts?\s+de\s+retard|1727",
    "1758_foreign": r"article\s+1758\b(?!\s*A)|1729-0\s*A",
    "L62_regularisation": r"L\.?\s*62\b|procédure\s+de\s+régularisation",
    "droit_erreur": r"droit\s+à\s+l'erreur|1727,?\s*V\b|déclaration\s+rectificative\s+spontan",
}
KINDS = {k: re.compile(v, re.I) for k, v in KINDS.items()}
PENSEC = re.compile(r"(Sur|En ce qui concerne|S'agissant de?s?|Quant aux)\s+(les\s+|la\s+)?(pénalités|majorations?|intérêts de retard|amendes?)", re.I)
DISP = re.compile(r"D\s*[EÉ]\s*C\s*I\s*D\s*E\s*:|DÉCIDE\s*:|décide\s*:", re.I)
DISCH = re.compile(r"(décharg\w*|dégrèvement|réduction)[^.;]{0,160}(pénalités|majoration|intérêts de retard)|"
                   r"(pénalités|majorations?)[^.;]{0,80}(sont|est)\s+(déchargé|supprimé|remplacé|substitué|ramené)", re.I)
REJECT = re.compile(r"(requête|demande|conclusions|appel|pourvoi)[^.;]{0,80}(est|sont)\s+rejeté", re.I)
REASONS = [
    ("burden_not_met", r"n'(établit|apporte)\s+pas|ne\s+justifie\s+pas|ne\s+démontre\s+pas|pas\s+(établi|démontré)\s+(l'intention|le\s+caractère\s+délibéré)"),
    ("motivation_L80D", r"motiv\w+[^.;]{0,80}(insuffisan|irréguli)|L\.?\s*80\s*D"),
    ("rights_discharged", r"(par\s+voie\s+de\s+conséquence|en\s+conséquence\s+de\s+la\s+décharge|accessoires?)"),
    ("substitution", r"substitu\w+[^.;]{0,120}(majoration|pénalité)|ramen\w+\s+à\s+40\s*%"),
    ("proportionality", r"proportionnalit|principe\s+de\s+nécessité|non\s+bis\s+in\s+idem|individualisation"),
    ("good_faith", r"bonne\s+foi"),
    ("tolerance_1727", r"vingtième|tolérance\s+légale"),
]
REASONS = [(k, re.compile(v, re.I)) for k, v in REASONS]
UPHELD = re.compile(r"(l'administration|le\s+service|le\s+ministre)\s+(doit\s+être\s+regardée?\s+comme\s+établissant|établit|justifie|apporte\s+la\s+preuve)|"
                    r"c'est\s+à\s+bon\s+droit\s+que[^.;]{0,120}(majoration|pénalité)|"
                    r"(bien-fondé\s+des\s+(pénalités|majorations))[^.;]{0,200}(écarté|rejeté)", re.I)
def court_of(meta, src):
    j = meta.get("JURIDICTION") or meta.get("Nom_Juridiction") or ""
    n = meta.get("NUMERO") or meta.get("Numero_Dossier") or ""
    d = meta.get("DATE_DEC") or meta.get("Date_Lecture") or ""
    return j.strip(), d.strip()[:10], n.strip()
FIG_MAJO = re.compile(r"(?:majoration|pénalité)s?\s+(?:de\s+|au\s+taux\s+de\s+)?(10|20|40|80|100)\s*%", re.I)
FIG_AMTS = re.compile("(" + AMT + ")" + EUR, re.I)
INT_PERIOD = re.compile(r"(du|à\s+compter\s+du|depuis\s+le)\s+" + DATE + r"\s+(?:au|jusqu'au)\s+" + DATE, re.I)
INT_RATE = re.compile(r"0,([24])0?\s*%", re.I)
def sentences(t):
    return re.split(r"(?<=[a-zé\)\"»])[.;]\s+(?=[A-ZÉ0-9«\"])", t)
def main():
    fd = open("data/pen/court_decisions.jsonl", "w", encoding="utf-8")
    ff = open("data/pen/court_figures.jsonl", "w", encoding="utf-8")
    seen = set(); n = nd = nf = 0
    for f in sorted(glob.glob("data/pen/courts/*.jsonl.gz")):
        for line in gzip.open(f, "rt", encoding="utf-8"):
            r = json.loads(line); t = r["text"]; meta = r["meta"]
            court, dd, no = court_of(meta, r["src"])
            key = (court.lower()[:30], dd, no)
            if key in seen: continue
            seen.add(key); n += 1
            head = t[:6000]
            if not re.search(r"impôt\s+sur\s+le\s+revenu", head, re.I): continue
            nd += 1
            years = sorted(set(int(y) for y in re.findall(r"au\s+titre\s+(?:des\s+années|de\s+l'année)\s+((?:19|20)\d\d)", head)))
            kinds = [k for k, p in KINDS.items() if p.search(t)]
            m = DISP.search(t); disp = t[m.end():] if m else t[-2500:]
            # penalty section: from a heading to the next heading or the dispositif
            sec = ""
            for ms in PENSEC.finditer(t):
                sec += t[ms.start(): ms.start() + 4000] + "\n"
            outcome = "discharged" if DISCH.search(disp) else ("rejected" if REJECT.search(disp) else "other")
            reasons = [k for k, p in REASONS if p.search(sec)] if sec else []
            row = {"court": court, "date": dd, "number": no, "years": years, "kinds": kinds, "outcome_disp": outcome,
                   "has_pen_section": bool(sec), "upheld_phrase": bool(UPHELD.search(sec)), "reasons": reasons,
                   "src": r["src"]}
            fd.write(json.dumps(row, ensure_ascii=False) + "\n")
            # figures
            for s in sentences(t):
                if len(s) > 1500: continue
                rates = FIG_MAJO.findall(s)
                amts = [num(a) for a in FIG_AMTS.findall(s)]
                per = INT_PERIOD.search(s)
                irate = INT_RATE.findall(s)
                kind = None
                if rates and len(amts) >= 2: kind = "majo"
                if re.search(r"intérêts?\s+de\s+retard", s, re.I) and (per or irate) and amts: kind = "interest"
                if re.search(r"intérêts?\s+de\s+retard", s, re.I) and re.search(r"\d+\s+mois", s) and irate: kind = "interest"
                if not kind: continue
                fig = {"court": court, "date": dd, "number": no, "kind": kind, "rates": sorted(set(int(x) for x in rates)),
                       "amounts": amts, "irate": irate, "sentence": s.strip()[:1500]}
                if per:
                    a = per.groups()
                    fig["period"] = [str(pdate(a[1], a[2], a[3])), str(pdate(a[4], a[5], a[6]))]
                ff.write(json.dumps(fig, ensure_ascii=False) + "\n"); nf += 1
    print(n, "unique decisions;", nd, "income tax;", nf, "figure sentences")
main()
