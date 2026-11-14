"""shadow13 (round 13, items 2 and 3): caption ties where one side is an OFFICE or an AGENCY ACRONYM.

Orders whose caption ties no decision of the court below on both sides (olink11 / cap10 'no_both_sides').
Two separate rules, each its own audit:

  S  officer successor. A public officer sued in an official capacity is a party by office, and a successor in office
     is substituted automatically (FRAP 43(c)(2); Sup. Ct. R. 35.3), so the order may print the successor's name where
     the decision below printed the predecessor's. Tie: one side pair ties by a shared name token (memo side_match 'T',
     given-name guard), and the order's other side and the decision's other side both name the SAME office (office()
     below: attorney general, secretary, commissioner, warden, director, superintendent, sheriff, administrator,
     governor, chief of police) with different holder names. The tied side must be the natural person whose full printed
     name (cap10.full_names) is in the decision's head.
  A  agency acronym. One side of the order is an agency acronym (3-6 capitals, e.g. NLRB) and the decision's side spells
     it out ('National Labor Relations Board': the initials of its words other than of / the / and / for / on / &), or
     the reverse; the other side pair ties as memo side_match does ('T' or 'G').

Candidates: decisions of the order's one court below dated 1..1,095 days before the order, from the caption-token index
(as olink11.candidates). Pick (both rules): the full-name candidates when the caption gives a full name (else all);
exactly one with no same-docket sibling (C6), else all on one docket -> C8 v2 (judgment test, >= 60 days, before the
docket-term bound). No answer-key file is read.

    python -X utf8 round13/agents/shadow13/alt13.py run --tag NAME     -> work/alt13_<tag>.pkl + links tsv + stats
"""
import argparse
import collections
import json
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round12", "agents", "shadow12"))
import build12 as B12  # noqa: E402

X, C8 = B12.X, B12.C8
R, M, L, cap10 = X.R, X.M, X.L, X.cap10
B11 = B12.B11
WORK = os.path.join(HERE, "work")
X.TOK11 = os.path.join(WORK, "tokidx13.pkl")   # = shadow12 tokidx12.pkl (caption tokens of the 1,871 nodes), copied
NL = chr(10)
DATA = os.path.join(C2, "round12", "data_orders")

OFFICES = [
    ("attorney general", r"\batt(?:orne)?y\.?\s*gen(?:eral|\.)?|\batt'y\.?\s*gen\b|\ba\.\s*g\.(?=\W)"),
    ("secretary", r"\bsec(?:retary|'y|y)?\b\.?"),
    ("commissioner", r"\bcomm(?:issione)?r\b|\bcomm'r\b"),
    ("warden", r"\bwarden\b"),
    ("director", r"\bdir(?:ector)?\b\.?"),
    ("superintendent", r"\bsupt\b\.?|\bsuperintendent\b"),
    ("sheriff", r"\bsheriff\b"),
    ("administrator", r"\badm(?:inistrato)?r\b|\badm'r\b"),
    ("governor", r"\bgov(?:ernor)?\b\.?"),
]
OFF_RX = [(k, re.compile(rx, re.I)) for k, rx in OFFICES]


def office(raw):
    """The office a caption side names ('Merrick B. Garland, Attorney General' -> 'attorney general'), else None.
    Only the text after the holder's name counts (the side's comma chunks after the first, or the whole side
    when it is the office alone)."""
    s = M._PAREN.sub(" ", raw or "")
    parts = [p.strip() for p in s.split(",")]
    tail = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
    got = [k for k, rx in OFF_RX if rx.search(tail)]
    return got[0] if len(got) == 1 else None


SKIPW = {"of", "the", "and", "for", "on", "&", "u.s.", "us"}


def acronym(side):
    """The acronym a side is, when it is one word of 3-6 capitals (dots allowed: 'N.L.R.B.'), else None."""
    w = re.sub(r"[.\s]", "", M._PAREN.sub(" ", side.raw)).strip(" ,;")
    w = re.sub(r",?(?:petitioners?|respondents?|appellants?|appellees?)$", "", w, flags=re.I)
    return w if re.fullmatch(r"[A-Z]{3,6}", w) else None


def initials(side):
    words = [x for x in re.findall(r"[A-Za-z][A-Za-z'.\-]*", M._PAREN.sub(" ", side.raw.split(",")[0]))
             if x.lower() not in SKIPW]
    return "".join(x[0].upper() for x in words)


def acr_tie(x, y):
    a = acronym(x)
    if a and len(initials(y)) == len(a) and initials(y) == a and acronym(y) is None:
        return True
    b = acronym(y)
    return bool(b and initials(x) == b and acronym(x) is None)


def person_full(side_raw):
    return cap10.full_names(side_raw) if not M.GOV_STATE_WORDS & set(M.wlist(side_raw)) else []


def alt_tie(o, t, rule):
    """-> the order-side raw text of the tied person side (S) / True (A), or None."""
    cap = R.one_caption(o, True)
    if cap is None:
        return None
    oa, ob = M.caption_sides(cap)
    ta, tb = M.caption_sides(R.title(t))
    if ob is None or tb is None:
        return None
    for (p, q), (r, s) in ((((oa, ta), (ob, tb))), (((oa, tb), (ob, ta)))):
        for (x1, y1), (x2, y2) in (((p, q), (r, s)), ((r, s), (p, q))):
            # (x1, y1) = the pair that ties by name; (x2, y2) = the office / acronym pair
            if rule == "S":
                if R.side_match_s(x1, y1) != "T":
                    continue
                o1, o2 = office(x2.raw), office(y2.raw)
                if o1 and o1 == o2 and not (x2.tk & y2.ext) and office(x1.raw) is None:
                    return x1.raw
            else:
                if R.side_match_s(x1, y1) and acr_tie(x2, y2):
                    return True
    return None


def alt_candidates(o, rule):
    tokidx, F = X._idx()
    ks = {k for k in o["courts"] if k is not None}
    if len(ks) != 1:
        return None, "not_one_court"
    cap = R.one_caption(o, True)
    if cap is None:
        return None, "not_one_caption"
    ids = set(X.courts().group.get(next(iter(ks)), ()))
    ocap = M.toks(cap)
    od, oo = o["date"], M.ordinal(o["date"])
    Ts = set()
    for c in ids:
        for w in ocap:
            for n in tokidx.get((c, w), ()):
                dn = int(F.date[n])
                if dn < od and 0 < oo - M.ordinal(dn) <= 1095:
                    Ts.add(n)
    good, person = [], set()
    for t in sorted(Ts):
        r = alt_tie(o, t, rule)
        if r:
            good.append(t)
            if rule == "S":
                person.add(r)
    if not good:
        return None, "no_alt_tie"
    rec = {}
    for t in good:
        rec[t] = {"date": int(F.date[t]), "days": oo - M.ordinal(int(F.date[t])), "court": int(F.court[t]),
                  "sibs": sorted(R.sibs(o["n"], t))}
    rec = {"date": od, "kind": o["kind"], "part": o["part"], "T": rec, "_o": o["n"]}
    if rule == "S":
        fn = sorted({k for p in person for k in person_full(p)})
    else:
        fn = cap10.full_names(cap)
    rec["has_full"], rec["fn"] = bool(fn), fn
    hd = X.heads(rec["T"])
    for t, r in rec["T"].items():
        r["full"] = bool(fn and t in hd and any(k in hd[t] for k in fn))
    return rec, ""


def pick(rec, rule):
    T = rec["T"]
    if rec["has_full"]:
        good = [t for t in T if T[t]["full"]]
    elif rule == "S":
        return None, "S_no_person_full_name"
    else:
        good = list(T)
    if not good:
        return None, "no_full_cand"
    if len(good) == 1 and not T[good[0]]["sibs"]:
        return good[0], "C6"
    alls = set(good)
    if not all(set(T[t]["sibs"]) | {t} >= alls for t in good):
        return None, "several_dockets"
    C8.texts(good)
    t = C8.pick_v2(rec, good, rec["_o"])
    return (t, "C8") if t is not None else (None, "c8_none")


def node_orders():
    """order-list nodes of round12/data_orders (file order ids from 6,892,454) with no corpus order node on their
    docket and date -> injected order dicts (build12.make_order12)."""
    rows_in = B11.read_nodes(DATA)
    corpus_dk = set()
    for o in R.orders().values():
        for d in re.split(r"[;,&]|\band\b", o.get("docket") or ""):
            if B11.dk_compact(d):
                corpus_dk.add((B11.dk_compact(d), o["date"]))
    out = []
    for i, r in enumerate(rows_in):
        n = B11.N0 + i
        p = os.path.join(DATA, "text", r["local_id"] + ".txt")
        dks = [d for d in r["docket"].split(";") if d and d != "-"]
        if not os.path.exists(p) or any((B11.dk_compact(d), int(r["date"])) in corpus_dk for d in dks):
            continue
        sp = {"n": n, "docket": r["docket"], "caption": r["caption"], "date": int(r["date"]),
              "text": open(p, encoding="utf-8", newline="").read(), "part": "majority"}
        o, why = B12.make_order12(sp)
        if o is None:
            continue
        o["lid"], o["ndk"] = r["local_id"], dks
        X.inject(o)
        out.append(o)
    return out


def corpus_orders():
    cand = pickle.load(open(os.path.join(C2, "round10/agents/shadow10/work/cap_cand.pkl"), "rb"))
    out = []
    for o in R.orders().values():
        if o["kind"] not in ("vacated", "reversed") or o["n"] in cand or o["n"] >= B11.N0:
            continue                     # (order-list nodes injected into R.orders() are not corpus orders)
        out.append(o)
    return out


def run(a):
    os.makedirs(WORK, exist_ok=True)
    base = C8_base()
    st = collections.Counter()
    res = []
    corp = corpus_orders()
    nodes = node_orders()
    for src, objs in (("corpus", corp), ("node", nodes)):
        for o in objs:
            if base.get(o["n"]):
                st[src + "_has_v12a_row"] += 1
                continue
            if src == "node":
                rec0, why0 = X.candidates(o)
                if rec0 is not None:
                    st["node_has_both_sides"] += 1
                    continue
            for rule in ("S", "A"):
                rec, why = alt_candidates(o, rule)
                if rec is None:
                    st["%s_%s_%s" % (src, rule, why)] += 1
                    continue
                t, how = pick(rec, rule)
                st["%s_%s_%s" % (src, rule, how if t is not None else how)] += 1
                res.append((src, rule, o["n"], t, how, rec))
    pickle.dump(res, open(os.path.join(WORK, "alt13_%s.pkl" % a.tag), "wb"))
    with open(os.path.join(WORK, "alt13_%s_links.tsv" % a.tag), "w", encoding="utf-8", newline=NL) as f:
        for src, rule, n, t, how, rec in res:
            o = R.orders()[n]
            f.write("\t".join(map(str, (src, rule, n, t if t is not None else "-", how, o["date"], o.get("docket", ""),
                                        R.one_caption(o, True), R.title(t) if t is not None else "-",
                                        len(rec["T"])))) + NL)
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "alt13_%s_stats.json" % a.tag), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


def C8_base():
    base = collections.defaultdict(set)
    with open(os.path.join(C2, "round12/stage/v12a/history.tsv"), encoding="utf-8") as f:
        for line in f:
            q = line.split("\t", 3)
            base[int(q[2])].add(int(q[1]))
    return base


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run",))
    ap.add_argument("--tag", required=True)
    run(ap.parse_args())
