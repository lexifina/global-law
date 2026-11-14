"""shadow10: C6 widened (rule C9) -- the full-name caption link with a wider candidate generator.

    python -X utf8 round10/agents/shadow10/wide10.py cand    -> work/wide_cand.pkl
    python -X utf8 round10/agents/shadow10/wide10.py rows    -> rows_wide.jsonl, work/wide_stats.json

C6 needed the target's title to tie the order's caption on BOTH sides (memo side_match), and its candidates came from
shared caption tokens. That misses (a) respondents printed differently below ("Eric SELLERS, Warden" -> "Warden,
Georgia Diagnostic Prison"; "ALABAMA" -> "State"; "UNITED STATES" -> "U.S."), (b) compound surnames swamped by their
halves ("RENTERIA-MARTINEZ" among hundreds of "Martinez" titles).
C9 (corpus-wide; no key read):
  O = a GVR order of the memo parse (vacated / reversed), one court below, one caption (fragments joined when they
      hold exactly one " v. ");
  full names = the caption's non-government sides, first comma chunk, >= 2 name words (cap10.full_names);
  surname = the chunk's last word (Jr. / Sr. / II / III / IV dropped), compact, >= 4 chars, kept whole when
      hyphenated ("renteriamartinez");
  candidates = decisions of a court O names, dated 1..1,095 days before O, whose title (compact) holds a surname;
  link = exactly ONE candidate whose text head (first 4,000 characters, compact) holds a full name (the C6 test),
      and that candidate has no other decision of its court on its docket in the window (round-9 sibs).
Rows: only orders that round9/stage/v9c history and cert_cap_b (C6) do not link; row terms as build10.py.
"""
import collections
import json
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cap10  # noqa: E402

R, M, L, C2 = cap10.R, cap10.M, cap10.L, cap10.C2
WORK = os.path.join(HERE, "work")
NL = chr(10)
SUFFIX = {"jr", "sr", "ii", "iii", "iv"}
PARTS_OK = ("majority", "perCuriam", "plurality")


def surnames(cap):
    out = []
    for side in re.split(r"\s+v\.\s+", cap):
        side = re.sub(r"^\s*In\s+re\s+", "", side.strip())
        if cap10.GOV.match(side):
            continue
        chunk = side.split(",")[0].strip()
        words = re.findall(r"[A-Za-z][A-Za-z'.\-]*", chunk)
        words = [w for w in words if re.sub(r"[^a-z]", "", w.lower()) not in SUFFIX]
        if len(words) >= 2:
            k = re.sub(r"[^a-z0-9]", "", words[-1].lower())
            if len(k) >= 4:
                out.append(k)
    return out


def stage_cand():
    courts = M.Courts()
    F = L.Facts()
    st = collections.Counter()
    want = {}
    for o in R.orders().values():
        if o["kind"] not in ("vacated", "reversed"):
            continue
        ks = {k for k in o["courts"] if k is not None}
        if len(ks) != 1:
            continue
        cap = R.one_caption(o, True)
        if not cap:
            continue
        fn = cap10.full_names(cap)
        sn = surnames(cap)
        if not fn or not sn:
            continue
        ids = set(courts.group.get(next(iter(ks)), ()))
        want[o["n"]] = (ids, fn, sn, o["date"])
    st["orders"] = len(want)
    # titles of every node of the wanted courts (one pass over nodes.tsv), compact
    allc = set().union(*(v[0] for v in want.values()))
    bycourt = collections.defaultdict(list)   # court -> [(date, node, compact title)]
    with open(L.NODES, "rb") as f:
        for n, line in enumerate(f):
            c = int(F.court[n]) if n < len(F.court) else -1
            if c not in allc:
                continue
            p = line.decode("utf-8", "replace").rstrip("\r\n").split("\t")
            if len(p) > 6:
                bycourt[c].append((int(F.date[n]), n, re.sub(r"[^a-z0-9]", "", p[6].lower())))
    for c in bycourt:
        bycourt[c].sort()
    print("courts", len(bycourt), "titles", sum(len(v) for v in bycourt.values()), flush=True)
    import bisect
    cand = {}
    for o_n, (ids, fn, sn, od) in want.items():
        oo = M.ordinal(od)
        cs = set()
        for c in ids:
            arr = bycourt.get(c, [])
            lo = bisect.bisect_left(arr, (od - 40000, -1, ""))
            for d, n, tt in arr[lo:bisect.bisect_left(arr, (od, -1, ""))]:
                if d < od and 0 < oo - M.ordinal(d) <= 1095 and any(s in tt for s in sn):
                    cs.add(n)
        if cs:
            cand[o_n] = {"T": {n: {} for n in cs}, "fn": fn, "date": od}
    st["with_cand"] = len(cand)
    need = sorted({n for r in cand.values() for n in r["T"]})
    st["texts"] = len(need)
    print(dict(st), flush=True)
    heads = {}
    for i in range(0, len(need), 5000):
        for n, (_s, t) in L.fetch_texts(need[i:i + 5000]).items():
            heads[n] = re.sub(r"[^a-z0-9]", "", t[:4000].lower())
        print(i, flush=True)
    for o_n, r in cand.items():
        for n in r["T"]:
            r["T"][n] = {"full": n in heads and any(k in heads[n] for k in r["fn"]), "date": int(F.date[n]),
                         "days": M.ordinal(r["date"]) - M.ordinal(int(F.date[n]))}
    pickle.dump(cand, open(os.path.join(WORK, "wide_cand.pkl"), "wb"), protocol=4)
    print(dict(st))


def pick(o_n, r):
    good = [t for t, x in r["T"].items() if x["full"]]
    if len(good) != 1:
        return None
    t = good[0]
    if R.sibs(o_n, t):
        return None
    return t


def stage_rows():
    orders = R.orders()
    cand = pickle.load(open(os.path.join(WORK, "wide_cand.pkl"), "rb"))
    node_dk = pickle.load(open(os.path.join(C2, "round8/agents/orderdock/work/meta.pkl"), "rb"))["node_dk"]
    base = collections.defaultdict(set)
    for path, oc, tc in ((os.path.join(C2, "round9/stage/v9c/history.tsv"), 2, 1),
                         (os.path.join(HERE, "cert_cap_b/history_delta.tsv"), 2, 1)):
        with open(path, encoding="utf-8") as f:
            for line in f:
                p = line.split("\t", 3)
                base[int(p[oc])].add(int(p[tc]))
    st = collections.Counter()
    rows, links = [], []
    for o_n, r in sorted(cand.items()):
        t = pick(o_n, r)
        if t is None:
            continue
        o = orders[o_n]
        st["linked"] += 1
        links.append((o_n, t))
        if base.get(o_n):
            st["in_base_same" if t in base[o_n] else "in_base_other"] += 1
            continue
        if o["part"] == "headmatter":
            if o["date"] < 20130101:
                st["refused_headmatter_pre2013"] += 1
                continue
            claim = "orderHead"
        elif o["part"] in PARTS_OK:
            claim = "-"
        else:
            st["refused_part_" + o["part"]] += 1
            continue
        cap = R.one_caption(o, True) or ""
        ocap = M.toks(cap)
        ttk = M.toks(R.title(t))
        shared = [x for x in ocap if x in ttk]
        T, off = o["T"], o["off"]
        q0, q1 = o["disp"]
        w = M.words_str(T[max(0, q0 - 400 - off):max(0, q1 + 400 - off)])
        ev = []
        for x in shared:
            if (" " + x + " ") in w and x not in ev:
                ev.append(x)
        if not ev:
            st["refused_no_name_evidence"] += 1
            continue
        scope = o["scope"]
        if scope == "all" and len(node_dk.get(t, ())) > max(1, len(o["caps"])):
            scope = "unknown"
            st["scope_unknown_consolidated"] += 1
        rows.append({"rule": "shadow10:cap-C9", "table": "history", "by": o_n, "target": int(t),
                     "kind": o["kind"], "scope": scope, "main": [q0, q1], "part": o["part"],
                     "ev": "name:" + " ".join(ev[:3]), "anchor": None, "anchor_part": "", "text": "by",
                     "claim": claim,
                     "note": "caption link (C9 full name, wide candidates): %d candidate(s) by surname, target %d days "
                             "before the order" % (len(r["T"]), r["T"][t]["days"])})
        st["rows"] += 1
        st["rows_post2013" if o["date"] >= 20130101 else "rows_pre2013"] += 1
    with open(os.path.join(HERE, "rows_wide.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r) + NL)
    with open(os.path.join(WORK, "wide_links.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for o_n, t in links:
            f.write("%d\t%d%s" % (o_n, t, NL))
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "wide_stats.json"), "w"), indent=1)
    print(dict(sorted(st.items())))


if __name__ == "__main__":
    {"cand": stage_cand, "rows": stage_rows}[sys.argv[1]]()
