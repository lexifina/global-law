"""Scan every Supreme Court decision: opinion length, sections, and the form cues (plurality, per curiam, equally divided).

    python scan_scotus.py  ->  data/holdings_work/scotus_scan.tsv
    columns: node, date, opinion_chars, majority_chars, sections (|-joined titles), form_guess, plurality_cue
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text

OUT = os.path.join(text.WORK, "caselaw-lean-2", "data", "holdings_work")
SEC = re.compile(r"(?m)^## (.+)$")
PLUR = re.compile(r"announced the judgment of the Court|delivered an opinion(?:,)? in which|"
                  r"opinion of the Court (?:with respect to|as to) Parts?|judgment of the Court and (?:delivered|an opinion)|"
                  r"\bplurality opinion\b", re.I)
EQ = re.compile(r"(?:affirmed|judgment is affirmed) by an (?:equally|evenly) divided (?:Court|court)", re.I)
PC = re.compile(r"(?i)\bper curiam\b")


def sections(t):
    ms = list(SEC.finditer(t))
    out = []
    for i, m in enumerate(ms):
        e = ms[i + 1].start() if i + 1 < len(ms) else len(t)
        out.append((m.group(1).strip(), m.end(), e))
    return out


def work(nid, raw):
    t = text.norm_text(raw)
    secs = sections(t)
    op = [s for s in secs if not s[0].lower().startswith(("head matter", "cap head matter"))]
    opc = sum(e - b for _, b, e in op)
    maj = sum(e - b for n, b, e in op if n.lower().startswith(("majority", "combined", "lead", "plurality", "per curiam")))
    head = t[:6000]
    m = PLUR.search(t[:20000])
    form = "full"
    if opc < 1000:
        form = "memorandum"
    elif EQ.search(t[:8000]):
        form = "equallyDivided"
    elif m or any(n.lower().startswith(("lead", "plurality")) for n, _, _ in op):
        form = "plurality"
    elif PC.search(head) and not re.search(r"delivered the opinion of the Court", t[:20000]):
        form = "perCuriam"
    d = re.search(r'(?m)^decided: "(\d{4})-(\d\d)-(\d\d)"', t)
    date = int("".join(d.groups())) if d else 0
    return (nid, date, opc, maj, "|".join(n for n, _, _ in secs)[:200], form, (m.group(0) if m else "-"))


def main():
    os.makedirs(OUT, exist_ok=True)
    nids = [int(l.split("\t", 2)[0]) for l in open(text.NODES, encoding="utf-8") if l.split("\t", 2)[1] == "supreme-court"]
    print(len(nids), flush=True)
    with open(os.path.join(OUT, "scotus_scan.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for i, r in enumerate(text.map_nodes(nids, work, procs=8, chunk=5000)):
            f.write("\t".join(str(x) for x in r) + "\n")
            if i % 50000 == 0:
                print(i, flush=True)


if __name__ == "__main__":
    main()
