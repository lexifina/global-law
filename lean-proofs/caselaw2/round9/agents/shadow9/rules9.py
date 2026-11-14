"""shadow9 link rules over work/link.pkl (remand decision found by docket; signals from its text and the graph).
    python -X utf8 round9/agents/shadow9/rules9.py agree     agreement of every rule with non-key truths
Rules (all require: O a GVR order (vacated/reversed); T caption-tied to O, same court below, 1..1,095 days before O;
B same court + docket as T, 0..1,826 days after O):
  tie(B)   = B cites O (graph) or names the reason case or holds O's docket number or O's date
  K1  B: cue and tie(B)                                    (remand decision tied to this order)
  K2  K1 and capB                                          (caption ties on both sides)
  K3  K1 and (capB or citeBT)
  K4  K2 and a second O-tie or citeBT                      (two independent ties)
  T is linked when exactly one candidate T passes; T's of one docket: the latest one dated before O wins
  (variants *_L), else no link.
"""
import collections, os, pickle, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
WORK = os.path.join(HERE, "work")


import functools
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "memo"))
import r6lib as L  # noqa: E402
import memolib as M  # noqa: E402
_ORD = {}


def orders():
    if not _ORD:
        for o in pickle.load(open(os.path.join(C2, "round6/history/rules/memo/work/orders.pkl"), "rb"))["orders"]:
            _ORD[o["n"]] = o
    return _ORD


@functools.lru_cache(maxsize=None)
def title(n):
    return L.node_row(n)[6]


SURNAME = [False]   # K9s: a name-token tie must not rest on the side's first word alone (a given name)


def given_names(raw):
    """Name tokens printed before a capitalised surname in the same comma-separated chunk of a caption side
    ("Leon ESCOURSE-WESTBROOK" -> {"leon"}); the reporter's caption style prints the surname in capitals."""
    out = set()
    for chunk in M._PAREN.sub(" ", raw).split(","):
        words = re.findall(r"[A-Za-z][A-Za-z'.\-]*", chunk)
        caps = [k for k, w in enumerate(words) if sum(ch.isalpha() for ch in w) >= 3 and w.isupper()]
        if not caps:
            continue
        for w in words[:caps[0]]:
            if not w.isupper():
                out |= set(M.wlist(w))
    return out


def side_match_s(o, t):
    """memolib.side_match, except that a 'T' tie resting only on given names (name words printed before a
    capitalised surname in the order's caption) does not count."""
    if o.tk & t.ext:
        if (o.tk & t.ext) <= given_names(o.raw):
            return ""
        return "T"
    return M.side_match(o, t)


JOIN = [False]   # K9: one parsed caption; K9j: the parsed caption fragments joined hold exactly one " v. "


def one_caption(o, join):
    if len(o["caps"]) == 1:
        return o["caps"][0]
    if not join or not o["caps"]:
        return None
    cap = " ".join(o["caps"])
    return cap if len(M.V_RX.findall(cap)) == 1 else None


@functools.lru_cache(maxsize=None)
def both_sides(o_n, t):
    """The order's caption and the target's title tie on both sides (memo rule: 'T' shared name token or 'G' same
    generic government party), straight or crossed; the order has one caption."""
    o = orders()[o_n]
    cap = one_caption(o, JOIN[0])
    if cap is None:
        return False
    oa, ob = M.caption_sides(cap)
    ta, tb = M.caption_sides(title(t))
    if ob is None or tb is None:
        return False
    sm = side_match_s if SURNAME[0] else M.side_match
    st = (sm(oa, ta), sm(ob, tb))
    cr = (sm(oa, tb), sm(ob, ta))
    return any(x[0] and x[1] and "T" in x for x in (st, cr))


_META = {}


def sibs(o_n, t):
    """Other decisions of T's court on T's docket numbers dated 1..1,095 days before the order."""
    if not _META:
        _META.update(pickle.load(open(os.path.join(C2, "round8/agents/orderdock/work/meta.pkl"), "rb")))
        _META["F"] = L.Facts()
    F = _META["F"]
    o = orders()[o_n]
    oo = M.ordinal(o["date"])
    ct = int(F.court[t])
    out = set()
    for tk in _META["node_dk"].get(t, ()):
        for n in _META["idx"].get((ct, tk), ()):
            if n != t and int(F.date[n]) < o["date"] and oo - M.ordinal(int(F.date[n])) <= 1095:
                out.add(n)
    return out


def single_court(o_n):
    o = orders()[o_n]
    return len({k for k in o["courts"] if k is not None}) == 1


def ties(s):
    return [k for k in ("citeBO", "reason", "odocket", "odate") if s[k]]


STRONG = ("citeBO", "odocket", "odate")


def ok(rule, s):
    t = ties(s)
    if rule.startswith("K5") or rule.startswith("K9"):
        return s["cue"] and bool(t) and s["capB"]
    if rule.startswith("K6"):
        return s["cue"] and any(s[k] for k in STRONG)
    if rule.startswith("K7"):
        return s["cue"] and (any(s[k] for k in STRONG) or (s["reason"] and s["citeBT"]))
    if rule.startswith("K8"):
        return s["cue"] and (any(s[k] for k in STRONG) or s["reason"]) and s["capB"]
    if not (s["cue"] and t):
        return False
    if rule.startswith("K1"):
        return True
    if rule.startswith("K2"):
        return s["capB"]
    if rule.startswith("K3"):
        return s["capB"] or s["citeBT"]
    if rule.startswith("K4"):
        return s["capB"] and (len(t) >= 2 or s["citeBT"])
    raise ValueError(rule)


def pick(rec, rule, o_n=None):
    if rule[:2] in ("K5", "K6", "K7", "K8", "K9"):
        if not single_court(o_n):
            return None
        good = [t for t, r in rec["T"].items() if both_sides(o_n, t) and any(ok(rule, s) for s in r["B"].values())]
        if rule.startswith("K9") and len(good) == 1 and sibs(o_n, good[0]):
            return None
    else:
        good = [t for t, r in rec["T"].items() if any(ok(rule, s) for s in r["B"].values())]
    if len(good) == 1:
        return good[0]
    if rule.endswith("_L") and good:
        dks = [rec["T"][t]["dk"] for t in good]
        if all(d & dks[0] for d in dks):
            return max(good, key=lambda t: (rec["T"][t]["date"], t))
    return None


RULES = ["K2", "K5", "K9"]


def set_join(j, surname=False):
    JOIN[0] = j
    SURNAME[0] = surname
    both_sides.cache_clear()


def agree():
    import agree as A
    tr = A.truths()
    link = pickle.load(open(os.path.join(WORK, "link.pkl"), "rb"))
    for rule in RULES + ["K9j", "K9js"]:
        set_join(rule.startswith("K9j"), rule == "K9js")
        c = collections.Counter()
        for o, rec in link.items():
            t = pick(rec, rule, o)
            if t is None:
                continue
            c["linked"] += 1
            c["linked_post2013"] += rec["date"] >= 20130101
            if o in tr:
                c["right" if t in tr[o] else "wrong"] += 1
        print("%-6s linked %4d (post-2013 %4d) | vs truth right %3d wrong %2d" % (
            rule, c["linked"], c["linked_post2013"], c["right"], c["wrong"]))


if __name__ == "__main__":
    {"agree": agree}[sys.argv[1]]()
