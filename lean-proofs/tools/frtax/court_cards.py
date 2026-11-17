"""Courts as test cases, triage aid. For candidate decisions, print a compact card: citation, income years, the
sentences that carry a euro amount or a number of parts next to a computation word, and the operative part.

usage: python3 -I harness/court_cards.py IDFILE|- [MAXCHARS]   (ids one per line; '-' = stdin)
"""
import json, os, re, sys

D = os.path.expanduser("~/fr/data/court")
CW = re.compile(r"parts?\b|quotient|revenu\s+(?:net\s+)?(?:global\s+)?imposable|revenu\s+fiscal|imp[ôo]t\s+(?:brut|net|d[ûu])|droits|"
                r"d[ée]cote|abattement|d[ée]duction|frais\s+r[ée]els|pension|r[ée]duction\s+d|cr[ée]dit\s+d|contribution\s+exceptionnelle|"
                r"plus-value|micro|bar[èe]me|taux|salaires?|traitements?|retraites?|b[ée]n[ée]fices?|foncier|dividendes?|plafon", re.I)
AMT = re.compile(r"\d[\d  .]*(?:,\d+)?\s*(?:euros?|€)|\d(?:,\d{1,2})?\s+parts?\b|demi[- ]part", re.I)
SENT = re.compile(r"(?<=[.;:])\s+(?=[A-Z0-9«\"])")


def card(fid, maxc=2500):
    t = open(f"{D}/text/{fid}.txt", encoding="utf-8").read()
    head, body = t.split("\n\n", 1) if "\n\n" in t else ("", t)
    meta = dict(l.split(": ", 1) for l in head.splitlines() if ": " in l)
    cite = f"{meta.get('Nom_Juridiction') or meta.get('JURIDICTION')} | {meta.get('Date_Lecture') or meta.get('DATE_DEC')} | {meta.get('Numero_Dossier') or meta.get('NUMERO')}"
    # skip the parties' arguments where possible: start at the court's reasoning
    m = re.search(r"Considérant ce qui suit|Sur le bien-fondé|Sur le bien fondé|\n\s*1\.\s", body)
    reason = body[m.start():] if m else body
    sents = [s.strip() for s in SENT.split(reason)]
    keep = [s for s in sents if AMT.search(s) and CW.search(s) and "L. 761-1" not in s]
    disp = re.findall(r"Article\s+(?:1er|2|3)\s*:[^\n]{0,300}", body)
    out = " ¶ ".join(keep)
    if len(out) > maxc:
        out = out[:maxc] + " [...]"
    return f"### {fid}\n{cite}\n{out}\nDISP: {' | '.join(disp)[:600]}\n"


if __name__ == "__main__":
    src = sys.stdin if sys.argv[1] == "-" else open(sys.argv[1])
    maxc = int(sys.argv[2]) if len(sys.argv) > 2 else 2500
    for l in src:
        fid = l.strip().split()[0] if l.strip() else ""
        if fid:
            print(card(fid, maxc))
