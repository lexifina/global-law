"""shadow10: caption links without a remand decision (cap10.py rules) -> round-7 JSON rows for round10/certify10.py.

    python -X utf8 round10/agents/shadow10/build10.py RULE [RULE ...] --tag NAME
        -> rows_<NAME>.jsonl, work/build10_<NAME>_stats.json, work/build10_<NAME>_links.tsv

Rules (cap10.pick): C2_unique_nosib (the order's caption ties exactly one decision of its one court below on both
sides, 1..1,095 days before the order, no other decision of that court on its docket in the window);
C6_fullname_unique_nosib (among the both-sides candidates exactly one whose text head holds the caption party's
full printed name, no sibling); C7_fullname_latest (as C6; candidates of one docket -> the latest).
Several rules: the first that links wins (they never disagree: an order links one T per rule; disagreement ->
no row, counted).
Row terms as round-9 build9.py (round-8 class remandcap): acting order = the memo parse (kind, scope, disposition
span, part); claim orderHead for head-matter orders >= 2013; head-matter orders before 2013 are not rows;
evidence name:<tokens> = party-name tokens the order's caption shares with the target's title, whole words within
400 characters of the quote (none -> no row); scope "unknown" when the target carries more docket numbers than the
order has captions. An order the base (round9/stage/v9c history.tsv) already links (any target) is not a row.
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
import cap10  # noqa: E402

R, M, L, C2 = cap10.R, cap10.M, cap10.L, cap10.C2
WORK = os.path.join(HERE, "work")
NL = chr(10)
PARTS_OK = ("majority", "perCuriam", "plurality")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rules", nargs="+")
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    orders = R.orders()
    cand = pickle.load(open(os.path.join(WORK, "cap_cand.pkl"), "rb"))
    node_dk = pickle.load(open(os.path.join(C2, "round8/agents/orderdock/work/meta.pkl"), "rb"))["node_dk"]
    base = collections.defaultdict(set)
    with open(os.path.join(C2, "round9/stage/v9c/history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 3)
            base[int(p[2])].add(int(p[1]))
    st = collections.Counter()
    rows, links = [], []
    for o_n, rec in sorted(cand.items()):
        picks = [(r, cap10.pick(rec, r, o_n)) for r in a.rules]
        got = {t for _r, t in picks if t is not None}
        if not got:
            continue
        if len(got) > 1:
            st["rules_disagree"] += 1
            continue
        t = got.pop()
        rule = next(r for r, x in picks if x == t)
        o = orders[o_n]
        st["linked"] += 1
        links.append((o_n, t, o["date"], o["kind"], o["part"], rule))
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
        r = rec["T"][t]
        rows.append({"rule": "shadow10:cap-" + rule.split("_")[0], "table": "history", "by": o_n, "target": int(t),
                     "kind": o["kind"], "scope": scope, "main": [q0, q1], "part": o["part"],
                     "ev": "name:" + " ".join(ev[:3]), "anchor": None, "anchor_part": "", "text": "by",
                     "claim": claim,
                     "note": "caption link (%s): %d both-sides candidate(s) of the court below, target %d days before "
                             "the order" % (rule, len(rec["T"]), r["days"])})
        st["rows_" + rule] += 1
        st["rows_" + o["kind"]] += 1
        st["rows_post2013" if o["date"] >= 20130101 else "rows_pre2013"] += 1
    with open(os.path.join(HERE, "rows_%s.jsonl" % a.tag), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r) + NL)
    with open(os.path.join(WORK, "build10_%s_links.tsv" % a.tag), "w", encoding="utf-8", newline=NL) as f:
        for r in links:
            f.write("\t".join(map(str, r)) + NL)
    st["rows"] = len(rows)
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "build10_%s_stats.json" % a.tag), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
