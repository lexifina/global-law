"""shadow12 (round 12, brief item 1): rule C8 for GVR orders with SEVERAL full-name candidates.

    python -X utf8 round12/agents/shadow12/c8_12.py agree     corpus GVR orders (shadow10 work/cap_cand.pkl, full marks)
        -> variants vs non-key truths (round-9 agree.truths: Reported below / bridge strings / list rows), new vs v11d

C8 (stated rule; no key read):
  domain   : the order's caption gives a full printed name (cap10.full_names) and C6 does not link (several full-name
             candidates, or one with siblings on its docket);
  identity : every full-name candidate of the court below (both caption sides + the full name in the head) lies on ONE
             docket of that court (each is a sibling of every other: same lower docket = same case);
  judgment : candidates whose own text is a rehearing / rehearing-en-banc denial or an order on a petition for rehearing
             are not the judgment (JUDG test below, on the candidate's own text);
  date     : dated before the end of the order's docket-term year (1 July after the docket number's year: cap10.term_end);
  pick     : the latest such candidate (date, then node id).
Variants measured: C8r10 (round 10's: also orders without a full name), C8f (full name only), C8fj (+ judgment test),
C8fj1 (C8fj also when only one full-name candidate has siblings: the siblings without the name stay out).
"""
import collections
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round10", "agents", "shadow10"))
import cap10  # noqa: E402

R, M, L = cap10.R, cap10.M, cap10.L
WORK = os.path.join(HERE, "work")
NL = chr(10)

RX_REH = re.compile(r"petition(?:s)?\s+for\s+(?:panel\s+)?rehearing|rehearing\s+en\s+banc|suggestion\s+for\s+rehearing|"
                    r"motion\s+for\s+rehearing|application\s+for\s+rehearing", re.I)
RX_DEN = re.compile(r"\b(?:is|are|be|was|were|hereby)\s+(?:hereby\s+)?denied|\bdenied\b|\boverruled\b", re.I)
RX_MERITS = re.compile(r"\b(?:we|the\s+court)\s+(?:affirm|reverse|vacate|hold|conclude)|\bAFFIRMED\b|\bREVERSED\b|"
                       r"\bVACATED\b", re.I)

_TX = {}


def texts(nodes):
    need = sorted(set(nodes) - set(_TX))
    for i in range(0, len(need), 4000):
        for n, (_s, t) in L.fetch_texts(need[i:i + 4000]).items():
            _TX[n] = t
    return _TX


RX_POST = re.compile(
    r"petitions?\s+for\s+(?:panel\s+)?rehearing|rehearing\s+(?:en\s+banc|by\s+the\s+panel)|suggestions?\s+for\s+"
    r"rehearing|motions?\s+(?:for\s+(?:a\s+)?rehearing|for\s+(?:a\s+)?stay|to\s+stay)|applications?\s+for\s+"
    r"rehearing|stay\s+(?:of\s+(?:the\s+)?mandate|pending)|\bto\s+stay\b|pending\s+(?:supreme\s+court\s+)?"
    r"(?:review|appeal)", re.I)
RX_ONPET = re.compile(r"\bON\s+(?:PETITIONS?|SUGGESTIONS?|MOTIONS?)\s+FOR\s+(?:PANEL\s+)?REHEARING", re.I)


def not_judgment(t):
    """JUDG: the candidate's own text is an order on a post-judgment petition or motion (rehearing, rehearing en banc,
    stay): its head matter prints "On petition for rehearing", or the opening of its majority / per curiam part
    (first 400 characters after the part heading) names such a petition or motion."""
    tx = _TX.get(t, "")
    j = tx.find("## Majority")
    hm = tx[:j] if j >= 0 else tx[:3000]
    if RX_ONPET.search(hm):
        return True
    if j < 0:
        return False
    k = tx.find(NL, j)
    opening = tx[k:k + 400] if k >= 0 else ""
    return bool(RX_POST.search(tx[j:j + 60]) or RX_POST.search(opening))


RX_STRONG = re.compile(
    r"(?:den(?:y|ied|ying)|voted\s+to\s+deny)[^.]{0,120}?(?:petitions?|suggestions?)\s+for\s+(?:panel\s+)?rehearing|"
    r"(?:petitions?|suggestions?)\s+for\s+(?:panel\s+)?rehearing[^.]{0,160}?\b(?:is|are|was|were|be|been)\s+"
    r"(?:also\s+)?(?:hereby\s+)?denied|rehearing\s+en\s+banc\s+(?:is|be|was)\s+(?:hereby\s+)?denied|"
    r"ORDERED\s+that\s+[^.]{0,160}?(?:opinion|chapter)[^.]{0,120}?\bis\s+(?:hereby\s+)?amended", re.I)


def opening_part(t, n=3000):
    """The first n characters of the text's first part after the head matter (Majority / Combined / Dissent ...)."""
    tx = _TX.get(t, "")
    for m in re.finditer(r"(?m)^## (.*)$", tx):
        if not m.group(1).lower().startswith("head matter"):
            return tx[m.start():m.start() + n]
    return ""


def not_judgment2(t):
    """JUDG v2 = JUDG, or the opening of the text's first part after the head matter denies a
    petition for rehearing / rehearing en banc, or orders an amendment of an opinion (6,000 characters: CourtListener
    slip texts print the caption, counsel and line numbers first)."""
    if not_judgment(t):
        return True
    return bool(RX_STRONG.search(re.sub(r"\s+", " ", opening_part(t, 6000))))


def has_cite(t):
    tx = _TX.get(t, "")[:1500]
    m = re.search(r'citations:\s*\[([^\]]*)\]', tx)
    return bool(m and m.group(1).strip())


def pick(rec, rule, o_n):
    T = rec["T"]
    if rule == "C8r10":
        return cap10.pick(rec, "C8", o_n)
    if not rec.get("has_full"):
        return None
    good = [t for t in T if T[t].get("full")]
    if not good:
        return None
    if len(good) == 1 and not T[good[0]]["sibs"]:
        return None                       # C6's case
    if len(good) == 1 and rule != "C8fj1":
        return None
    alls = set(good)
    if not all(set(T[t]["sibs"]) | {t} >= alls for t in good):
        return None
    if rule == "C8v2":
        return pick_v2(rec, good, o_n)
    if rule in ("C8fj", "C8fj1"):
        good = [t for t in good if not not_judgment(t)]
    te = cap10.term_end(o_n)
    if te is None:
        return None
    good = [t for t in good if T[t]["date"] < te]
    if not good:
        return None
    if rule in ("C8fj", "C8fj1"):
        # one decision printed twice (same date): the reported copy (with a reporter citation) first
        return max(good, key=lambda t: (T[t]["date"], has_cite(t), t))
    return max(good, key=lambda t: (T[t]["date"], t))


MIN_DAYS = 60     # a petition, its docketing, the response time and distribution precede any order


def copies(good, T):
    """Candidates on one docket dated within 3 days of one another are one decision printed more than once."""
    out = []
    for t in sorted(good, key=lambda x: -T[x]["days"]):
        if out and T[out[-1][-1]]["days"] - T[t]["days"] <= 3:
            out[-1].append(t)
        else:
            out.append([t])
    return out


def pick_v2(rec, good, o_n):
    T = rec["T"]
    te = cap10.term_end(o_n)
    if te is None:
        return None
    groups = []
    for g in copies(good, T):
        if any(not_judgment2(t) for t in g):
            continue
        rep = max(g, key=lambda t: (has_cite(t), len(_TX.get(t, "")), t))
        if T[rep]["date"] < te and T[rep]["days"] >= MIN_DAYS:
            groups.append(rep)
    if not groups:
        return None
    return max(groups, key=lambda t: (T[t]["date"], -T[t]["days"], t))


def base_hist():
    base = collections.defaultdict(set)
    with open(os.path.join(C2, "round11/stage/v11d/history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 3)
            base[int(p[2])].add(int(p[1]))
    return base


def agree():
    sys.path.insert(0, os.path.join(C2, "round9", "agents", "shadow9"))
    import agree as A
    tr = A.truths()
    cand = pickle.load(open(os.path.join(C2, "round10/agents/shadow10/work/cap_cand.pkl"), "rb"))
    need = set()
    for o, rec in cand.items():
        if rec.get("has_full"):
            g = [t for t in rec["T"] if rec["T"][t].get("full")]
            if len(g) > 1 or (len(g) == 1 and rec["T"][g[0]]["sibs"]):
                need |= set(g)
    texts(need)
    base = base_hist()
    rows = []
    for rule in ("C8r10", "C8f", "C8fj", "C8fj1", "C8v2"):
        c = collections.Counter()
        for o, rec in cand.items():
            t = pick(rec, rule, o)
            if t is None:
                continue
            c6 = cap10.pick(rec, "C6_fullname_unique_nosib")
            if c6 is not None:
                continue           # C6 already links it (installed)
            c["linked"] += 1
            post = rec["date"] >= 20130101
            if o in tr:
                k = "right" if t in tr[o] else "wrong"
                c[k] += 1
                c[k + ("_post" if post else "_pre")] += 1
                if rule == "C8fj1":
                    rows.append((o, t, k, rec["date"], len(rec["T"])))
            if base.get(o):
                c["base_same" if t in base[o] else "base_other"] += 1
            else:
                c["new"] += 1
                c["new_post2013" if post else "new_pre2013"] += 1
        r, w = c["right"], c["wrong"]
        print("%-8s %s  prec %.3f" % (rule, dict(sorted(c.items())), r / max(1, r + w)), flush=True)
    # judgment test alone: how many full-name candidates it removes
    nj = sum(1 for t in need if not_judgment(t))
    print("full-name candidates in the C8 domain", len(need), "rehearing-order texts", nj)
    os.makedirs(WORK, exist_ok=True)
    with open(os.path.join(WORK, "c8_agree_truths.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write("\t".join(map(str, r)) + NL)


if __name__ == "__main__":
    {"agree": agree}[sys.argv[1]]()
