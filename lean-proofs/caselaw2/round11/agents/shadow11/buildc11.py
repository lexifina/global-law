"""shadow11 part B: rows of the narrower caption sub-rule C11 (narrow11.pick) over corpus GVR orders, round-7 JSON
for round11/certify11.py. Row terms exactly as round-10 build10.py (class cap-C6): acting order = the memo parse
(kind, scope, disposition span, part); claim orderHead for head-matter orders >= 2013; head-matter orders before 2013
are not rows; evidence name:<tokens> = party-name tokens the order's caption shares with the target's title, whole
words within 400 characters of the quote (none -> no row); scope "unknown" when the target carries more docket numbers
than the order has captions. An order the base (round10/stage/v10d history.tsv) already links is not a row.

    python -X utf8 round11/agents/shadow11/buildc11.py --tag c11  -> rows_c11.jsonl, work/buildc11_c11_stats.json
No answer-key file is read.
"""
import argparse
import collections
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import narrow11 as N  # noqa: E402

R, M, L, C2 = N.R, N.M, N.L, N.C2
WORK = N.WORK
NL = chr(10)
PARTS_OK = ("majority", "perCuriam", "plurality")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="c11")
    ap.add_argument("--rule", default="C11")
    a = ap.parse_args()
    orders = R.orders()
    cand = pickle.load(open(os.path.join(WORK, "c10_cand.pkl"), "rb"))
    node_dk = pickle.load(open(os.path.join(C2, "round8/agents/orderdock/work/meta.pkl"), "rb"))["node_dk"]
    base = N.base_links(os.path.join(C2, "round10/stage/v10d/history.tsv"))
    F = N.X._idx()[1]
    st = collections.Counter()
    rows = []
    for o_n, rec in sorted(cand.items()):
        t, why = N.pick(o_n, rec, a.rule)
        if t is None:
            continue
        o = orders[o_n]
        st["linked"] += 1
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
        days = M.ordinal(o["date"]) - M.ordinal(int(F.date[t]))
        rows.append({"rule": "shadow11:cap-C11", "table": "history", "by": o_n, "target": int(t),
                     "kind": o["kind"], "scope": scope, "main": [q0, q1], "part": o["part"],
                     "ev": "name:" + " ".join(ev[:3]), "anchor": None, "anchor_part": "", "text": "by",
                     "claim": claim,
                     "note": "caption link (C11 natural-person name, unique in the court's %d surname decisions): "
                             "target %d days before the order" % (len(rec["pool"]), days)})
        st["rows"] += 1
        st["rows_" + o["kind"]] += 1
        st["rows_post2013" if o["date"] >= 20130101 else "rows_pre2013"] += 1
    with open(os.path.join(HERE, "rows_%s.jsonl" % a.tag), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r) + NL)
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "buildc11_%s_stats.json" % a.tag), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
