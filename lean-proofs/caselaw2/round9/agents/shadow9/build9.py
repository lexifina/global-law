"""shadow9: K9 links (rules9.py) -> round-7 JSON rows for round9/certify9.py.

    python -X utf8 round9/agents/shadow9/build9.py [v1|v2]   -> rows_remandtext.jsonl, work/build9_stats.json,
                                                        work/build9_refused.tsv, work/k9_links.tsv

Row terms (as round-8 orderdock build_rows.py, class remandcap):
  acting order = the memo parse (orders.pkl): kind, scope, disposition quote span, part; claim orderHead for
  head-matter orders dated >= 2013; head-matter orders before 2013 are not rows;
  evidence name:<tokens>: party-name tokens the order's caption shares with the target's title, each a whole word
  within 400 characters of the quote; none -> no row;
  scope: the order's scope; for vacated / reversed, "unknown" when the target carries more docket numbers than the
  order has captions (consolidated appeals: the order reaches its petitioner only).
  An order the base (round8/stage/v8e history.tsv) already links to a different decision is not a row (counted).
No answer-key file is read.
"""
import collections
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules9 as R  # noqa: E402

L, M = R.L, R.M
C2 = R.C2
WORK = os.path.join(HERE, "work")
NL = chr(10)
KINDS = ("vacated", "reversed")
PARTS_OK = ("majority", "perCuriam", "plurality")
RULE = "K9"
V = sys.argv[1] if len(sys.argv) > 1 else "v2"
# v1: K9 as audited in r9k01; v2 (after r9k01): caption fragments joined (one " v. ") + given-name guard
R.set_join(V == "v2", V == "v2")
SUF = "" if V == "v1" else "_v2"


def main():
    orders = R.orders()
    link = pickle.load(open(os.path.join(WORK, "link.pkl"), "rb"))
    node_dk = pickle.load(open(os.path.join(C2, "round8/agents/orderdock/work/meta.pkl"), "rb"))["node_dk"]
    base = collections.defaultdict(set)
    with open(os.path.join(C2, "round8/stage/v8e/history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 3)
            base[int(p[2])].add(int(p[1]))
    st = collections.Counter()
    rows, refused, links = [], [], []
    for o_n, rec in sorted(link.items()):
        t = R.pick(rec, RULE, o_n)
        if t is None:
            continue
        o = orders[o_n]
        st["linked"] += 1
        bs = sorted(b for b, s in rec["T"][t]["B"].items() if R.ok(RULE, s))
        sigs = sorted({k for b in bs for k, v in rec["T"][t]["B"][b].items() if v is True})
        links.append((o_n, t, o["date"], o["kind"], o["part"], ";".join(map(str, bs)), ",".join(sigs)))
        if base.get(o_n):
            if t in base[o_n]:
                st["in_base_same_target"] += 1
                refused.append((o_n, t, "in_base"))
            else:
                st["base_other_target"] += 1
                refused.append((o_n, t, "base_other:" + ",".join(map(str, sorted(base[o_n])))))
            continue
        if o["part"] == "headmatter":
            if o["date"] < 20130101:
                st["refused_headmatter_pre2013"] += 1
                refused.append((o_n, t, "headmatter_pre2013"))
                continue
            claim = "orderHead"
        elif o["part"] in PARTS_OK:
            claim = "-"
        else:
            st["refused_part_" + o["part"]] += 1
            refused.append((o_n, t, "part_" + o["part"]))
            continue
        ocap = M.toks(" ".join(o["caps"]) or o["title"])
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
            refused.append((o_n, t, "no_name_evidence"))
            continue
        scope = o["scope"]
        if scope == "all" and len(node_dk.get(t, ())) > max(1, len(o["caps"])):
            scope = "unknown"
            st["scope_unknown_consolidated"] += 1
        rows.append({"rule": "shadow9:remandtext-K9" + ("" if V == "v1" else "-v2"), "table": "history", "by": o_n, "target": int(t),
                     "kind": o["kind"], "scope": scope, "main": [q0, q1], "part": o["part"],
                     "ev": "name:" + " ".join(ev[:3]), "anchor": None, "anchor_part": "", "text": "by",
                     "claim": claim,
                     "note": "remand decision(s) of the court below on the same docket: %s (signals %s)"
                             % (";".join(map(str, bs[:6])), ",".join(sigs))})
        st["rows_" + o["kind"]] += 1
        st["rows_" + ("orderHead" if claim == "orderHead" else "other")] += 1
        st["rows_post2013" if o["date"] >= 20130101 else "rows_pre2013"] += 1
    with open(os.path.join(HERE, "rows_remandtext%s.jsonl" % SUF), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r) + NL)
    with open(os.path.join(WORK, "build9_refused%s.tsv" % SUF), "w", encoding="utf-8", newline=NL) as f:
        for r in refused:
            f.write("\t".join(map(str, r)) + NL)
    with open(os.path.join(WORK, "k9_links%s.tsv" % SUF), "w", encoding="utf-8", newline=NL) as f:
        f.write("order\ttarget\torder_date\tkind\tpart\tbridges\tsignals" + NL)
        for r in links:
            f.write("\t".join(map(str, r)) + NL)
    st["rows"] = len(rows)
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "build9_stats%s.json" % SUF), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
