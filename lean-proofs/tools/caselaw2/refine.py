"""Second look at the rare form labels (plurality, equallyDivided, certifiedAnswer): re-read only those decisions'
header and tail from git and apply stricter tests that the scan's 60-character evidence cannot support.

    python refine.py        -> work/courts/refine.tsv (node, form, src); decisions_build.py stage3 applies it

Tests (all on the body without front matter: head = first 5,000 characters, tail = last 1,000):
  plurality       'announced the judgment ... and delivered an opinion' / 'opinion announcing the judgment' / a
                  'PLURALITY OPINION' heading, and NO 'delivered the opinion of the Court' / 'opinion of the Court with
                  respect to Part(s)' / 'opinion for the Court' (those decisions have a majority for most parts).
  equallyDivided  this decision's own disposition 'X is affirmed by an equally/evenly divided court' in the first
                  600 characters of the opinion or the tail, and no 'court of appeals / below' in that sentence.
  certifiedAnswer a federal certifying court near 'certif…' AND an answering phrase ('we answer', 'question answered',
                  'answered in the affirmative/negative'), and no 'accept…' of the question.
A decision that fails gets perCuriam/full/unknown by the stage-2 fallback order (per curiam evidence, then length).
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from show import fetch  # noqa: E402

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
WD = os.path.join(WORK, "caselaw-lean-2", "work", "courts")

PLUR_OK = re.compile(r"announced the judgment of the [Cc]ourt,? and (?:delivered|filed) an opinion|delivered an opinion "
                     r"announcing the judgment|opinion announcing the judgment of the [Cc]ourt|^\s*PLURALITY OPINION|"
                     r"^\s*Plurality [Oo]pinion|announced the judgment of the [Cc]ourt in an opinion", re.M)
MAJ = re.compile(r"delivered the opinion of the [Cc]ourt|opinion of the [Cc]ourt with respect to Parts?|opinion for the "
                 r"[Cc]ourt|opinion of the [Cc]ourt as to Parts?")
EQ = re.compile(r"(?:affirmed|affirms?|affirmance)(?: [\w,]+){0,6}? (?:by|because of|through) an? (?:equally|evenly) divided "
                r"(?:[Cc]ourt|vote|bench)|(?:equally|evenly) divided (?:[Cc]ourt|vote|bench)[^.]{0,60}(?:is|are|be|stands?) "
                r"affirmed", re.I)
CERT_ANS = re.compile(r"\bwe answer|answer(?:ing)? (?:the|both|each|all|these|this|those|that)? ?(?:certified )?questions?|"
                      r"questions? (?:certified )?(?:is |are )?answered|answered in the (?:affirmative|negative)|"
                      r"[Cc]ertified [Qq]uestions? [Aa]nswered", re.I)
CERT_ACC = re.compile(r"\baccept(?:s|ed|ing)? (?:the )?(?:certified |certification)|certification (?:is |was )?accepted|"
                      r"order accepting", re.I)
FEDCT = re.compile(r"United States (?:Court of Appeals|District Court|Bankruptcy Court|Supreme Court)|(?:First|Second|Third|"
                   r"Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Federal|D\.C\.) Circuit|\b\d{1,2}(?:st|nd|rd|"
                   r"th) Cir\.|U\.S\. District Court|federal (?:district )?court|Court of Appeals for the", re.I)


def body(t):
    if t.startswith("---"):
        e = t.find("\n---", 3)
        t = t[e + 4:]
    return t


def opinion_start(b):
    """offset of the first opinion section (after any head matter)."""
    for m in re.finditer(r"^## (.+)$", b, re.M):
        if not m.group(1).lower().startswith(("head matter", "cap head matter")):
            return m.end()
    return 0


def main():
    cand = {}
    for fn in os.listdir(os.path.join(WD, "dec")):
        if not fn.endswith(".tsv"):
            continue
        for line in open(os.path.join(WD, "dec", fn), encoding="utf-8"):
            r = line.rstrip("\n").split("\t")
            if r[6] in ("plurality", "equallyDivided", "certifiedAnswer"):
                cand[r[0]] = (r[6], r[8])
    want = {}
    with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 5)
            if p[0] in cand:
                want[p[0]] = (p[1], p[2], p[3], p[4])
    texts = fetch(want)
    out = []
    kept = {"plurality": 0, "equallyDivided": 0, "certifiedAnswer": 0}
    for n, (form, src) in cand.items():
        b = body(texts.get(n, ""))
        head, tail = b[:5000], b[-1000:]
        ok = False
        if form == "plurality":
            ok = bool(PLUR_OK.search(head)) and not MAJ.search(head)
        elif form == "equallyDivided":
            o = opinion_start(b)
            op = b[o:]
            zone = op if len(op) < 3000 else op[:600]
            for m in ([] if re.search(r"quorum|same effect as", zone, re.I) else EQ.finditer(zone)):
                st = max(zone.rfind(". ", 0, m.start()), zone.rfind("\n", 0, m.start()), m.start() - 200)
                sent = zone[st + 1:m.end() + 40]
                if not re.search(r"quorum|below|lower court|court of appeals|appellate division|previously|earlier|former|"
                                 r"aff'?d|\d{4}\)", sent, re.I):
                    ok = True
                    break
        else:
            m = re.search(r"certif", head, re.I)
            ok = bool(m and FEDCT.search(head[max(0, m.start() - 400):m.end() + 400]) and CERT_ANS.search(b[:8000] +
                      tail) and not CERT_ACC.search(head))
        if ok:
            kept[form] += 1
            continue
        pc = ";f:pc" in src or "pc" in src.split(";f:")[-1]
        nv = "perCuriam" if re.search(r"PER CURIAM|Per Curiam", b[:1500]) else ("full" if len(b) >= 600 else "unknown")
        out.append((n, nv, "refine:" + form + "-rejected"))
    with open(os.path.join(WD, "refine.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for r in out:
            f.write("\t".join(r) + "\n")
    print("candidates", len(cand), "kept", kept, "rejected", len(out))


if __name__ == "__main__":
    main()
