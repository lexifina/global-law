"""shadow13 (round 13, item 1): rule D = same person, second docket.

    python -X utf8 round13/agents/shadow13/d13.py agree     corpus GVR orders (shadow10 cap_cand.pkl, full marks)
        -> variants vs non-key truths (round-9 agree.truths: Reported below / bridge strings / list rows), new vs v12a

Domain: the order's caption gives a full printed name; C6 does not link; C8 refuses because the full-name candidates
(decisions of the one court below 1..1,095 days before the order whose title ties the caption on both sides and whose
head holds the full name) lie on MORE THAN ONE docket of that court (the same person's several appeals).
D (stated rule; no key read):
  judgment : C8 v2's judgment test (copies within 3 days = one decision; post-judgment orders on rehearing / stay /
             opinion amendment set aside), dated >= 60 days before the order and before the order's docket-term bound
             (1 July after the docket number's year, cap10.term_end);
  window   : the decision must fall in the filing window of the order's docket number: on or after 1 July of the
             year BEFORE the docket year (a petition docketed in that year reviews a judgment of at most ~1 year
             earlier: 90 days to petition, 60 days' extension, rehearing time);
  docket   : exactly ONE docket group (candidates linked as same-docket siblings) holds an eligible decision in the
             window -> the latest such decision; several dockets in the window -> no link.
Variants: Dlatest (no window; the latest eligible decision of any docket), Dwin (window, one docket), Dwin1 (window,
latest of all dockets in the window even when several).
"""
import collections
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round12", "agents", "shadow12"))
import c8_12 as C8  # noqa: E402

cap10 = C8.cap10
R = cap10.R
WORK = os.path.join(HERE, "work")
NL = chr(10)


def groups_of(good, T):
    """docket groups: union of candidates that are same-docket siblings of one another."""
    par = {t: t for t in good}

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for t in good:
        for s in T[t]["sibs"]:
            if s in par:
                par[f(s)] = f(t)
    g = collections.defaultdict(list)
    for t in good:
        g[f(t)].append(t)
    return list(g.values())


def eligible(grp, T, te):
    """C8 v2's judgment + date tests inside one docket group -> representative decisions."""
    out = []
    for g in C8.copies(grp, T):
        if any(C8.not_judgment2(t) for t in g):
            continue
        rep = max(g, key=lambda t: (C8.has_cite(t), len(C8._TX.get(t, "")), t))
        if T[rep]["date"] < te and T[rep]["days"] >= C8.MIN_DAYS:
            out.append(rep)
    return out


def domain(rec):
    """full-name candidates on more than one docket (C6 / C8 refuse) -> their docket groups, else None."""
    if not rec.get("has_full"):
        return None
    T = rec["T"]
    good = [t for t in T if T[t].get("full")]
    if not good:
        return None
    if len(good) == 1 and not T[good[0]]["sibs"]:
        return None                      # C6
    alls = set(good)
    if all(set(T[t]["sibs"]) | {t} >= alls for t in good):
        return None                      # C8's domain (one docket)
    gs = groups_of(good, T)
    return gs if len(gs) >= 2 else None


def pick(rec, o_n, rule="Dwin"):
    gs = domain(rec)
    if gs is None:
        return None
    T = rec["T"]
    te = cap10.term_end(o_n)
    if te is None:
        return None
    ws = te - 20000                      # 1 July of the year before the docket year
    el = []
    for g in gs:
        e = eligible(g, T, te)
        if rule != "Dlatest":
            e = [t for t in e if T[t]["date"] >= ws]
        if e:
            el.append(max(e, key=lambda t: (T[t]["date"], -T[t]["days"], t)))
    if not el:
        return None
    if rule == "Dwin" and len(el) != 1:
        return None
    return max(el, key=lambda t: (T[t]["date"], -T[t]["days"], t))


def base_hist(p="round12/stage/v12a/history.tsv"):
    base = collections.defaultdict(set)
    with open(os.path.join(C2, p), encoding="utf-8") as f:
        for line in f:
            q = line.split("\t", 3)
            base[int(q[2])].add(int(q[1]))
    return base


def agree():
    sys.path.insert(0, os.path.join(C2, "round9", "agents", "shadow9"))
    import agree as A
    tr = A.truths()
    cand = pickle.load(open(os.path.join(C2, "round10/agents/shadow10/work/cap_cand.pkl"), "rb"))
    need = set()
    dom = {}
    for o, rec in cand.items():
        gs = domain(rec)
        if gs:
            dom[o] = gs
            need |= {t for g in gs for t in g}
    C8.texts(need)
    base = base_hist()
    print("domain (corpus GVR orders, full-name candidates on >= 2 dockets):", len(dom))
    for rule in ("Dlatest", "Dwin1", "Dwin"):
        c = collections.Counter()
        for o in dom:
            rec = cand[o]
            t = pick(rec, o, rule)
            if t is None:
                c["none"] += 1
                continue
            c["linked"] += 1
            if o in tr:
                c["right" if t in tr[o] else "wrong"] += 1
            if base.get(o):
                c["base_same" if t in base[o] else "base_other"] += 1
            else:
                c["new"] += 1
        r, w = c["right"], c["wrong"]
        print("%-8s %s  prec %.3f" % (rule, dict(sorted(c.items())), r / max(1, r + w)), flush=True)
    # where do truths sit relative to the window
    c = collections.Counter()
    for o in dom:
        te = cap10.term_end(o)
        for t in tr.get(o, ()):
            if t in cand[o]["T"] and te:
                d = cand[o]["T"][t]["date"]
                c["truth_in_window" if te - 20000 <= d < te else "truth_before_window" if d < te - 20000 else
                  "truth_after_te"] += 1
    print("truths vs window:", dict(c))


NODE_RECS = os.path.join(C2, "round12/agents/shadow12/work/c8_recs_r12sub.pkl")  # build12 nodes on round12/data_orders


def node_recs():
    """order-list nodes (round12/data_orders, 1,871): {node: rec} with the order injected for term_end."""
    recs = pickle.load(open(NODE_RECS, "rb"))
    out = {}
    for lid, (n, rec, date, docket, title) in recs.items():
        if n not in R.orders():
            R.orders()[n] = {"n": n, "date": int(date), "docket": docket or "", "title": title}
        out[n] = rec
    return out


def nodes_check():
    nr = node_recs()
    dom = {n: domain(r) for n, r in nr.items()}
    dom = {n: g for n, g in dom.items() if g}
    C8.texts({t for g in dom.values() for x in g for t in x})
    base = base_hist()
    c = collections.Counter()
    for n in dom:
        t = pick(nr[n], n, "Dwin")
        if t is None:
            c["none"] += 1
            continue
        c["linked"] += 1
        if base.get(n):
            c["base_same" if t in base[n] else "base_other"] += 1
        else:
            c["new"] += 1
    print("order-list nodes: domain", len(dom), dict(sorted(c.items())))


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    {"agree": agree, "nodes": nodes_check}[sys.argv[1]]()
