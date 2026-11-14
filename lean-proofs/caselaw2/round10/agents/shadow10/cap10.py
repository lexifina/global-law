"""shadow10: GVR order -> decision below WITHOUT a remand decision B (move 5, part 2).

    python -X utf8 round10/agents/shadow10/cap10.py cand    -> work/cap_cand.pkl  per GVR order: caption-tied T's
    python -X utf8 round10/agents/shadow10/cap10.py agree   rule variants vs non-key truths (+ h0 misses diagnosis)

Candidates (corpus-wide, no key read): O = a GVR order of the round-6 memo parse (kind vacated / reversed) with one
court below (memo courts) and one caption (fragments joined when they hold exactly one " v. "); T = a decision of
that court dated 1..1,095 days before O whose title ties O's caption on both sides (memo side_match, straight or
crossed, given-name guard: round-9 rules9.both_sides with JOIN and SURNAME on).
Per T recorded: date, days before O, docket tokens, siblings (other decisions of the court on T's docket in the
window), whether T is the latest both-sides candidate, how many both-sides candidates the order has.
"""
import collections
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round9", "agents", "shadow9"))
import rules9 as R  # noqa: E402

L, M = R.L, R.M
WORK = os.path.join(HERE, "work")
S9W = os.path.join(C2, "round9", "agents", "shadow9", "work")
R.set_join(True, True)


def stage_cand():
    courts = M.Courts()
    F = L.Facts()
    tokidx = pickle.load(open(os.path.join(S9W, "tokidx.pkl"), "rb"))
    out = {}
    st = collections.Counter()
    for o in R.orders().values():
        if o["kind"] not in ("vacated", "reversed"):
            continue
        st["gvr"] += 1
        ks = {k for k in o["courts"] if k is not None}
        if len(ks) != 1:
            st["not_one_court"] += 1
            continue
        cap = R.one_caption(o, True)
        if cap is None:
            st["not_one_caption"] += 1
            continue
        ids = set(courts.group.get(next(iter(ks)), ()))
        ocap = M.toks(cap)
        od, oo = o["date"], M.ordinal(o["date"])
        Ts = set()
        for c in ids:
            for w in ocap:
                for n in tokidx.get((c, w), ()):
                    dn = int(F.date[n])
                    if dn < od and 0 < oo - M.ordinal(dn) <= 1095:
                        Ts.add(n)
        good = [t for t in sorted(Ts) if R.both_sides(o["n"], t)]
        if not good:
            st["no_both_sides"] += 1
            continue
        rec = {}
        for t in good:
            rec[t] = {"date": int(F.date[t]), "days": oo - M.ordinal(int(F.date[t])), "court": int(F.court[t]),
                      "sibs": sorted(R.sibs(o["n"], t))}
        out[o["n"]] = {"date": od, "kind": o["kind"], "part": o["part"], "T": rec}
        st["with_cand"] += 1
    pickle.dump(out, open(os.path.join(WORK, "cap_cand.pkl"), "wb"), protocol=4)
    print(dict(st))


GOV = re.compile(r"^(?:the\s+)?(?:united\s+states|people|state|commonwealth)\b", re.I)


def full_names(cap):
    """Compact full names of the caption's non-government sides: the side's first comma chunk, with at least two
    name words (given name(s) + surname), e.g. 'Hector VILLARREAL, petitioner' -> 'hectorvillarreal'."""
    out = []
    for side in re.split(r"\s+v\.\s+", cap):
        side = re.sub(r"^\s*In\s+re\s+", "", side.strip())
        if GOV.match(side):
            continue
        chunk = side.split(",")[0].strip()
        words = re.findall(r"[A-Za-z][A-Za-z'.\-]*", chunk)
        if len(words) >= 2:
            k = re.sub(r"[^a-z0-9]", "", chunk.lower())
            if len(k) >= 8:
                out.append(k)
    return out


def stage_full():
    """Per (O, T) candidate: does T's text head (first 4,000 characters) hold O's full party name (compact)?"""
    cand = pickle.load(open(os.path.join(WORK, "cap_cand.pkl"), "rb"))
    need, fn = set(), {}
    for o, rec in cand.items():
        f = full_names(R.one_caption(R.orders()[o], True) or "")
        if f:
            fn[o] = f
            need |= set(rec["T"])
    print("orders with full names", len(fn), "texts", len(need), flush=True)
    heads = {}
    items = sorted(need)
    for i in range(0, len(items), 5000):
        tx = L.fetch_texts(items[i:i + 5000])
        for n, (_s, t) in tx.items():
            heads[n] = re.sub(r"[^a-z0-9]", "", t[:4000].lower())
        print(i, flush=True)
    for o, rec in cand.items():
        for t, r in rec["T"].items():
            r["full"] = bool(o in fn and t in heads and any(k in heads[t] for k in fn[o]))
        rec["has_full"] = o in fn
    pickle.dump(cand, open(os.path.join(WORK, "cap_cand.pkl"), "wb"), protocol=4)
    print("done")


def term_end(o_n):
    """The end of the filing window the order's own docket number gives: 'YY-NNNN' -> 1 July of 20YY+1 (19YY+1)."""
    dk = (R.orders()[o_n].get("docket") or "").strip()
    m = re.match(r"(?:No\.\s*)?(\d{2})\s*[-–—]\s*\d{1,5}\b", dk)
    if not m:
        return None
    yy = int(m.group(1))
    od = R.orders()[o_n]["date"] // 10000
    y = 1900 + yy if 1900 + yy <= od and od - (1900 + yy) < 10 else 2000 + yy
    if not (0 <= od - y <= 3):
        return None
    return (y + 1) * 10000 + 701


def pick(rec, rule, o_n=None):
    T = rec["T"]
    if rule.startswith("C8"):
        # full-name candidates when the caption gives a full name, else the both-sides candidates; all on one docket;
        # the latest dated before the end of the filing window of the order's docket number
        if rec.get("has_full"):
            good = [t for t in T if T[t].get("full")]
        else:
            good = list(T)
        if not good or o_n is None:
            return None
        te = term_end(o_n)
        if te is None:
            return None
        alls = set(good)
        if not all(set(T[t]["sibs"]) | {t} >= alls for t in good):
            return None
        good = [t for t in good if T[t]["date"] < te]
        if not good:
            return None
        return max(good, key=lambda t: (T[t]["date"], t))
    if rule.startswith("C6") or rule.startswith("C7"):
        if not rec.get("has_full"):
            return None
        good = [t for t in T if T[t].get("full")]
        if rule.startswith("C7") and len(good) > 1:
            # all on one docket (siblings of one another): the latest
            alls = set(good)
            if all(set(T[t]["sibs"]) | {t} >= alls for t in good):
                good = [max(good, key=lambda t: (T[t]["date"], t))]
        if len(good) != 1:
            return None
        t = good[0]
        if rule.startswith("C6") and T[t]["sibs"]:
            return None
        return t
    if rule == "C1_unique":
        c = list(T)
    elif rule == "C2_unique_nosib":
        c = [t for t in T if not T[t]["sibs"]] if len(T) == 1 else []
    elif rule == "C3_latest_sameDocket":
        # several candidates all on one docket (T and its siblings): the latest one
        if len(T) == 1:
            c = list(T)
        else:
            alls = set(T)
            if all(set(T[t]["sibs"]) | {t} >= alls for t in T):
                c = [max(T, key=lambda t: (T[t]["date"], t))]
            else:
                c = []
    elif rule == "C4_unique_nosib_365":
        c = [t for t in T if not T[t]["sibs"] and T[t]["days"] <= 365] if len(T) == 1 else []
    elif rule == "C5_unique_nosib_540":
        c = [t for t in T if not T[t]["sibs"] and T[t]["days"] <= 540] if len(T) == 1 else []
    else:
        raise ValueError(rule)
    return c[0] if len(c) == 1 else None


RULES = ["C1_unique", "C2_unique_nosib", "C3_latest_sameDocket", "C4_unique_nosib_365", "C5_unique_nosib_540",
         "C6_fullname_unique_nosib", "C7_fullname_latest", "C8_latest_docketyear"]


def agree():
    sys.path.insert(0, os.path.join(C2, "round9", "agents", "shadow9"))
    import agree as A
    tr = A.truths()
    cand = pickle.load(open(os.path.join(WORK, "cap_cand.pkl"), "rb"))
    base = collections.defaultdict(set)
    with open(os.path.join(C2, "round9/stage/v9c/history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 3)
            base[int(p[2])].add(int(p[1]))
    for rule in RULES:
        c = collections.Counter()
        for o, rec in cand.items():
            t = pick(rec, rule, o)
            if t is None:
                continue
            c["linked"] += 1
            post = rec["date"] >= 20130101
            if o in tr:
                k = "right" if t in tr[o] else "wrong"
                c[k] += 1
                c[k + ("_post" if post else "_pre")] += 1
            if base.get(o):
                c["base_same" if t in base[o] else "base_other"] += 1
            else:
                c["new"] += 1
                c["new_post2013" if post else "new_pre2013"] += 1
        r, w = c["right"], c["wrong"]
        print("%-24s %s  prec %.3f" % (rule, dict(sorted(c.items())), r / max(1, r + w)))


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    {"cand": stage_cand, "full": stage_full, "agree": agree}[sys.argv[1]]()
