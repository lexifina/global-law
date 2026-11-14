"""shadow13 (round 13, item 4, exploratory): rule N = name form. The caption's full printed name (given name(s) +
surname) is in the candidate's head with up to two middle names / initials between the FIRST given name and the
surname ('John SMITH' ~ 'John A. Smith', 'John Allen Smith'), or with a hyphen / space variant of a compound surname.
Domain: orders whose caption gives a full name, with both-sides candidates of the court below, none of which holds the
exact compact full name (cap10 'c8_none_full0'). Pick = C6 / C8 v2 on the N-marked candidates.

    python -X utf8 round13/agents/shadow13/nf13.py agree      corpus GVR orders vs non-key truths; new vs v12a
    python -X utf8 round13/agents/shadow13/nf13.py nodes      order-list nodes (round12/data_orders): counts by year
No answer-key file is read.
"""
import collections
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d13 as D  # noqa: E402

C8, cap10, R, C2 = D.C8, D.cap10, D.R, D.C2
L = cap10.L
_HT = {}


def head_text(nodes):
    need = sorted(set(nodes) - set(_HT))
    for i in range(0, len(need), 4000):
        for n, (_s, t) in L.fetch_texts(need[i:i + 4000]).items():
            _HT[n] = " " + re.sub(r"[^a-z]+", " ", t[:4000].lower()) + " "
    return _HT


def name_parts(cap):
    """[(first given name, surname words)] of the caption's full-name sides (cap10.full_names' sides)."""
    out = []
    for side in re.split(r"\s+v\.\s+", cap):
        side = re.sub(r"^\s*In\s+re\s+", "", side.strip())
        if cap10.GOV.match(side):
            continue
        chunk = side.split(",")[0].strip()
        chunk = re.sub(r"\bet\s+(?:al|ux|vir)\b\.?", "", chunk, flags=re.I).strip()
        words = re.findall(r"[A-Za-z][A-Za-z'.\-]*", chunk)
        if len(words) < 2:
            continue
        caps = [i for i, w in enumerate(words) if w.isupper() and sum(ch.isalpha() for ch in w) >= 2]
        si = caps[0] if caps and caps[0] > 0 else len(words) - 1
        given, sur = words[0], words[si:]
        if len(given.rstrip(".")) < 2:
            continue
        out.append((re.sub(r"[^a-z]", "", given.lower()), [re.sub(r"[^a-z]", "", w.lower()) for w in
                                                           re.split(r"[-\s]", " ".join(sur)) if w.strip(".")]))
    return out


def nf_match(parts, ht):
    for given, sur in parts:
        if not given or not sur or len("".join(sur)) < 3:
            continue
        rx = r" %s(?: [a-z]+){0,2} %s " % (re.escape(given), r"[ ]?".join(re.escape(s) for s in sur))
        if re.search(rx, ht):
            return True
    return False


def domain(rec):
    if not rec.get("has_full"):
        return False
    return not any(rec["T"][t].get("full") for t in rec["T"])


def pick(rec, o_n, cap):
    parts = name_parts(cap)
    if not parts:
        return None
    ht = head_text(rec["T"])
    T = rec["T"]
    good = [t for t in T if t in ht and nf_match(parts, ht[t])]
    if not good:
        return None
    if len(good) == 1 and not T[good[0]]["sibs"]:
        return good[0]
    alls = set(good)
    if not all(set(T[t]["sibs"]) | {t} >= alls for t in good):
        return None
    C8.texts(good)
    rec["_o"] = o_n
    return C8.pick_v2(rec, good, o_n)


def agree():
    sys.path.insert(0, os.path.join(C2, "round9", "agents", "shadow9"))
    import agree as A
    tr = A.truths()
    cand = pickle.load(open(os.path.join(C2, "round10/agents/shadow10/work/cap_cand.pkl"), "rb"))
    base = D.base_hist()
    c = collections.Counter()
    for o, rec in cand.items():
        if not domain(rec):
            continue
        c["domain"] += 1
        t = pick(rec, o, R.one_caption(R.orders()[o], True) or "")
        if t is None:
            continue
        c["linked"] += 1
        if o in tr:
            c["right" if t in tr[o] else "wrong"] += 1
        if base.get(o):
            c["base_same" if t in base[o] else "base_other"] += 1
        else:
            c["new"] += 1
    print("corpus", dict(sorted(c.items())))


def nodes():
    nr = D.node_recs()
    base = D.base_hist()
    c = collections.Counter()
    for n, rec in nr.items():
        if not domain(rec):
            continue
        y = R.orders()[n]["date"] // 10000
        c["domain_%d" % y] += 1
        cap = R.orders()[n]["title"]
        t = pick(rec, n, cap)
        if t is None:
            continue
        c["linked_%d" % y] += 1
        if base.get(n):
            c["base_same" if t in base[n] else "base_other"] += 1
        else:
            c["new_%d" % y] += 1
    print("nodes", dict(sorted(c.items())))


if __name__ == "__main__":
    {"agree": agree, "nodes": nodes}[sys.argv[1]]()
