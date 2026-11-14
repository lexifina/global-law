"""shadow11 part B: a narrower caption sub-rule (C10) for GVR orders that round-10 C6 leaves unlinked.

    python -X utf8 round11/agents/shadow11/narrow11.py cand    -> work/c10_cand.pkl (wide pools + person matches)
    python -X utf8 round11/agents/shadow11/narrow11.py agree   rule variants vs non-key truths (+ counts)

Designed from round-10 shadow10 NOTES failure descriptions of C2 / C9 (same-surname people, other suits of a
frequent litigant -- union, official, diocese --, earlier judgments of the same case) and corpus text; no audit item of
r10k01-03 is read. No answer-key file is read (truths = the order's own "Reported below", round-8 bridge strings and
list rows: shadow9 agree.truths()).

C10 (all must hold):
  O       a GVR order of the memo parse (vacated / reversed), one court below, one caption (rules9 JOIN);
  person  a caption side whose first comma chunk is a natural person's name: a given name of >= 2 letters + a surname;
          no organisation / office word in the chunk; no office designation in the side's later chunks (", Warden",
          ", Attorney General", ", Secretary of ..." mark an official sued for an office: a frequent litigant);
  match   a decision's text head (first 4,000 characters) prints that person: "Given [<= 3 words] Surname" or
          "Surname, Given" (whole words, lower-cased, punctuation as spaces);
  pool    every decision of the court below dated 1..1,095 days before O whose title holds a person side's surname
          token (wide: not only the both-sides candidates) -- exactly one pool member matches;
  T       that one is a both-sides caption candidate (round-10 cap_cand.pkl), has no sibling on its docket in the
          window, and is dated before the end of the term year that O's own docket number gives (cap10.term_end).
"""
import collections
import json
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import olink11 as X  # noqa: E402

R, M, L, cap10 = X.R, X.M, X.L, X.cap10
WORK = os.path.join(HERE, "work")
S10W = X.S10W
NL = chr(10)

OFFICE = set("""
    warden secretary director commissioner superintendent sheriff attorney governor president judge clerk chief
    administrator executor executrix guardian trustee mayor chairman chairperson commissioners officer acting
    """.split())
TAIL_OK = re.compile(r"^(?:jr|sr|ii|iii|iv|et al|petitioners?|respondents?|appellants?|appellees?|individually|"
                     r"aka .*|a k a .*|deceased)$")


def _words(s):
    return re.findall(r"[A-Za-z][A-Za-z'\-]*", s)


def person(side):
    """-> (given, surname words) of a natural person's side, else None. Reporter style 'Brian Keith STOREY,
    petitioner' or 'Donald Ray Harris, Petitioner'; order-list style is normalised first (olink11.norm_side)."""
    side = X.norm_side(side)
    side = re.sub(r"^\s*In\s+re\s+", "", side.strip())
    chunks = [c.strip() for c in M._PAREN.sub(" ", side).split(",")]
    head = chunks[0]
    ws = _words(head)
    if len(ws) < 2 or len(ws) > 6:
        return None
    lw = [w.lower() for w in ws]
    if set(lw) & (X.ORG_WORDS | OFFICE) or set(lw) & M.GOV_STATE_WORDS or "united" in lw:
        return None
    for c in chunks[1:]:
        cl = " ".join(w.lower() for w in _words(c))
        if not cl:
            continue
        if set(cl.split()) & (OFFICE | X.ORG_WORDS - {"et", "al"}):
            return None
        if not TAIL_OK.match(cl):
            return None
    caps = [i for i, w in enumerate(ws) if sum(ch.isalpha() for ch in w) >= 2 and w.isupper()]
    if caps and caps[0] > 0:
        given, sur = ws[:caps[0]], ws[caps[0]:]
    elif not caps:
        given, sur = ws[:-1], ws[-1:]
    else:
        return None
    sur = [w for w in sur if w.lower().rstrip(".") not in ("jr", "sr", "ii", "iii", "iv")]
    g = [w for w in given if len(w.rstrip(".")) >= 2]
    if not g or not sur:
        return None
    gv = g[0].lower()
    sn = " ".join(re.sub(r"[^a-z]+", " ", w.lower()).strip() for w in sur)
    if len(gv) < 2 or len(sn.replace(" ", "")) < 3:
        return None
    return gv, sn


def sides_of(cap):
    p = M.split_v(cap)
    return [p[0], p[1]] if p else [cap]


def name_rx(gv, sn):
    s = re.escape(sn).replace("\\ ", " ")
    return re.compile(r"\b" + re.escape(gv) + r"(?: [a-z]+){0,3} " + s + r"\b|\b" + s + r" " + re.escape(gv) + r"\b")


def norm_head(t):
    return " " + re.sub(r"[^a-z0-9]+", " ", t[:4000].lower()) + " "


def stage_cand():
    cand = pickle.load(open(os.path.join(S10W, "cap_cand.pkl"), "rb"))
    tokidx, F = X._idx()
    cts = X.courts()
    out, need = {}, set()
    st = collections.Counter()
    for o in R.orders().values():
        if o["kind"] not in ("vacated", "reversed"):
            continue
        ks = {k for k in o["courts"] if k is not None}
        if len(ks) != 1:
            continue
        cap = R.one_caption(o, True)
        if cap is None:
            continue
        ps = [p for p in (person(s) for s in sides_of(cap)) if p]
        if not ps:
            st["no_person"] += 1
            continue
        ids = set(cts.group.get(next(iter(ks)), ()))
        od, oo = o["date"], M.ordinal(o["date"])
        pool = set()
        for gv, sn in ps:
            for w in sn.split():
                if len(w) < 3:
                    continue
                for c in ids:
                    for n in tokidx.get((c, w), ()):
                        dn = int(F.date[n])
                        if dn < od and 0 < oo - M.ordinal(dn) <= 1095:
                            pool.add(n)
        st["with_person"] += 1
        if not pool:
            st["empty_pool"] += 1
            continue
        out[o["n"]] = {"persons": ps, "pool": sorted(pool), "both": cand.get(o["n"], {}).get("T", {})}
        need |= pool
    print(dict(st), "orders", len(out), "texts", len(need), flush=True)
    hd = {}
    items = sorted(need)
    for i in range(0, len(items), 5000):
        for n, (_s, t) in L.fetch_texts(items[i:i + 5000]).items():
            hd[n] = norm_head(t)
        print(i, flush=True)
    for o_n, rec in out.items():
        rxs = [name_rx(gv, sn) for gv, sn in rec["persons"]]
        rec["match"] = [n for n in rec["pool"] if n in hd and any(rx.search(hd[n]) for rx in rxs)]
    pickle.dump(out, open(os.path.join(WORK, "c10_cand.pkl"), "wb"), protocol=4)
    print("done")


def pick(o_n, rec, rule="C10"):
    m = rec["match"]
    if rule.startswith("V2"):
        m = [t for t in m if t in rec["both"]]
    if rule.startswith("V3") and len(m) > 1:
        # several matches, all on one docket (siblings of one another): the latest before the docket's term end
        te = cap10.term_end(o_n)
        allm = set(m)
        if te is not None and all(t in rec["both"] for t in m) and \
                all(set(rec["both"][t]["sibs"]) | {t} >= allm for t in m):
            ok = [t for t in m if rec["both"][t]["date"] < te]
            if ok:
                t = max(ok, key=lambda x: (rec["both"][x]["date"], x))
                return t, "linked"
    if len(m) != 1:
        return None, "pool_matches_%s" % ("0" if not m else "2+")
    t = m[0]
    if rule.startswith("V4"):
        return t, "linked"
    if rule.startswith("C11"):
        # the pool-unique person match (no both-sides requirement: the title holds the person's surname), no other
        # decision of its court on its docket in the window, dated before the end of the order's docket term year
        if R.sibs(o_n, t):
            return None, "sibling"
        te = cap10.term_end(o_n)
        if te is None:
            return None, "no_docket_year"
        F = X._idx()[1]
        if int(F.date[t]) >= te:
            return None, "after_term"
        return t, "linked"
    if t not in rec["both"]:
        return None, "not_both_sides"
    if rec["both"][t]["sibs"]:
        return None, "sibling"
    if rule.startswith("V"):
        return t, "linked"
    if rule in ("C10", "C10_nodate"):
        if rule == "C10":
            te = cap10.term_end(o_n)
            if te is None:
                return None, "no_docket_year"
            if rec["both"][t]["date"] >= te:
                return None, "after_term"
    return t, "linked"


def base_links(path):
    base = collections.defaultdict(set)
    with open(path, encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 3)
            base[int(p[2])].add(int(p[1]))
    return base


def agree():
    sys.path.insert(0, os.path.join(C2, "round9", "agents", "shadow9"))
    import agree as A
    tr = A.truths()
    cand = pickle.load(open(os.path.join(WORK, "c10_cand.pkl"), "rb"))
    c6 = pickle.load(open(os.path.join(S10W, "cap_cand.pkl"), "rb"))
    base = base_links(os.path.join(C2, "round10/stage/v10d/history.tsv"))
    for rule in ("C10", "V4", "C11"):
        c = collections.Counter()
        for o_n, rec in cand.items():
            t, why = pick(o_n, rec, rule)
            c["why_" + why] += 1
            if t is None:
                continue
            c6t = cap10.pick(c6[o_n], "C6_fullname_unique_nosib") if o_n in c6 else None
            if c6t is not None:
                c["c6_same" if c6t == t else "c6_other"] += 1
            post = R.orders()[o_n]["date"] >= 20130101
            if o_n in tr:
                k = "right" if t in tr[o_n] else "wrong"
                c[k] += 1
                if c6t is None:
                    c[k + "_notC6"] += 1
            if base.get(o_n):
                c["base_same" if t in base[o_n] else "base_other"] += 1
            else:
                c["new"] += 1
                c["new_post2013" if post else "new_pre2013"] += 1
        r, w = c["right"], c["wrong"]
        print("%-12s prec %.3f %s" % (rule, r / max(1, r + w), dict(sorted(c.items()))))


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    {"cand": stage_cand, "agree": agree}[sys.argv[1]]()
