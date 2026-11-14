"""Round 8 `orderdock`: link files -> round-7 JSON rows (input of round8/certify8.py).

    python -X utf8 round8/agents/orderdock/build_rows.py   -> rows_bridge.jsonl, rows_remandcap.jsonl,
                                                              rows_lists.jsonl, work/build_stats.json,
                                                              work/build_refused.tsv

Classes (each its own rows file, certified into its own delta folder):
  bridge     (dres.py)  later text's subsequent-history string names the decision below and the order (page / docket)
  remandcap  (dock.py remand + memo caption rows)  the caption link (round-6 memo rule or round-7 orderHead row) and
             the remand-docket bridge give the same decision below, and no history string disagrees
  lists      (listcite.py + listorder.py)  every "Reported below" entry of an order list (deduplicated)
Common row terms:
  - acting order = the memo parse (orders.pkl): kind, scope, disposition quote span, part; claim orderHead for
    head-matter orders dated >= 2013 (certify8 checks court / date / kind / order_line / length); head-matter orders
    before 2013 are not rows (no claim allows them);
  - evidence name:<tokens>: party-name tokens (memolib.toks) the order's caption shares with the target's title,
    each a whole word within 400 characters of the quote (as the memo rule); none -> no row;
  - scope: the order's scope; for vacated / reversed, "unknown" when the target carries more docket numbers than the
    order has captions (a consolidated decision of several appeals: the order reaches only its own petitioner).
No answer-key file is read.
"""
import collections
import json
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HIST = os.path.join(C2, "round6", "history")
MEMO = os.path.join(HIST, "rules", "memo")
sys.path.insert(0, HIST)
sys.path.insert(0, MEMO)
import r6lib as L  # noqa: E402
import memolib as M  # noqa: E402

WORK = os.path.join(HERE, "work")
NL = chr(10)
KINDS = ("certDenied", "vacated", "reversed", "affirmed", "reviewDismissed")
STATUS = ("vacated", "reversed")
PARTS_OK = ("majority", "perCuriam", "plurality")


def read_links(path, cols):
    out = {}
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip(NL).split("\t")
            out[int(p[0])] = tuple(p[1:1 + cols])
    return out


def main():
    orders = {o["n"]: o for o in pickle.load(open(os.path.join(MEMO, "work", "orders.pkl"), "rb"))["orders"]}
    node_dk = pickle.load(open(os.path.join(WORK, "meta.pkl"), "rb"))["node_dk"]
    st = collections.Counter()
    refused = []
    tt = {}

    def ttoks(n):
        if n not in tt:
            tt[n] = set(M.toks(L.node_row(n)[6]))
        return tt[n]

    def make(o, t, rule, note):
        kind = o["kind"]
        if kind not in KINDS:
            return None, "kind_" + kind
        if o["part"] == "headmatter":
            if o["date"] < 20130101:
                return None, "headmatter_pre2013"
            claim = "orderHead"
        elif o["part"] in PARTS_OK:
            claim = "-"
        else:
            return None, "part_" + o["part"]
        ocap = M.toks(" ".join(o["caps"]) or o["title"])
        shared = [x for x in ocap if x in ttoks(t)]
        T, off = o["T"], o["off"]
        q0, q1 = o["disp"]
        w = M.words_str(T[max(0, q0 - 400 - off):max(0, q1 + 400 - off)])
        ev = []
        for x in shared:
            if (" " + x + " ") in w and x not in ev:
                ev.append(x)
        if not ev:
            return None, "no_name_evidence"
        scope = o["scope"]
        if kind in STATUS and scope == "all" and len(node_dk.get(t, ())) > max(1, len(o["caps"])):
            scope = "unknown"
            st["scope_unknown_consolidated"] += 1
        return {"rule": rule, "table": "history", "by": o["n"], "target": int(t), "kind": kind, "scope": scope,
                "main": [q0, q1], "part": o["part"], "ev": "name:" + " ".join(ev[:3]), "anchor": None,
                "anchor_part": "", "text": "by", "claim": claim, "note": note}, ""

    bridge = read_links(os.path.join(WORK, "bridge_links.tsv"), 3)
    remand = read_links(os.path.join(WORK, "remand_links.tsv"), 3)
    # caption links: round-6 memo caption rows (all parts) and round-7 orderHead v2 rows
    cap = collections.defaultdict(set)
    for p in (os.path.join(MEMO, "rows.jsonl"), os.path.join(C2, "round7", "agents", "orderhead", "v2", "rows.jsonl")):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            if ":cap-" in r["rule"]:
                cap[r["by"]].add(r["target"])
    out_b, out_r = [], []
    for o_n, (t, nb, br) in sorted(bridge.items()):
        o = orders.get(o_n)
        t = int(t)
        row, why = make(o, t, "orderdock:bridge", "history string in %s later text(s): %s" % (nb, br[:200]))
        if row is None:
            st["bridge_refused_" + why] += 1
            refused.append(("bridge", o_n, t, why))
            continue
        if cap.get(o_n) and t not in cap[o_n]:
            row["note"] += "; caption rule gave %s" % ",".join(map(str, sorted(cap[o_n])))
            st["bridge_vs_caption_disagree"] += 1
        out_b.append(row)
        st["bridge_rows_" + row["kind"]] += 1
        st["bridge_rows_" + ("orderHead" if row["claim"] == "orderHead" else "other")] += 1
    for o_n, (t, nb, br) in sorted(remand.items()):
        t = int(t)
        o = orders.get(o_n)
        if o_n in bridge:
            continue
        if t not in cap.get(o_n, ()):
            st["remand_without_caption_agreement"] += 1
            continue
        row, why = make(o, t, "orderdock:remand+cap", "remand-docket bridge (%s later decision(s) of the court "
                                                      "below in the same docket: %s) agrees with the caption link"
                        % (nb, br))
        if row is None:
            st["remand_refused_" + why] += 1
            refused.append(("remandcap", o_n, t, why))
            continue
        out_r.append(row)
        st["remandcap_rows_" + row["kind"]] += 1
        st["remandcap_rows_" + ("orderHead" if row["claim"] == "orderHead" else "other")] += 1
    # lists: listcite + listorder, one row per (by, target, kind); listorder (long lists) first.
    # v2 (after audit r8k02): (i) caption tie-check: the target's title shares a party-name token with the
    # order's captions (meta parties of the order; a page of an unpublished reporter holds several decisions and the
    # index keys one of them); (ii) scope unknown for vacated / reversed when the target carries more docket numbers
    # than the order has entries citing it (a consolidated decision of several appellants: the order reaches its
    # petitioners only).
    sc_parties = {}
    lrows = []
    for p in ("rows_listorder.jsonl", "rows_listcite.jsonl"):
        for line in open(os.path.join(HERE, p), encoding="utf-8"):
            lrows.append(json.loads(line))
    want = {r["by"] for r in lrows}
    for pth in L.shards(".meta.tsv.gz"):
        if os.path.basename(pth).startswith("supreme-court"):
            for q in L.meta_rows(pth):
                if int(q[0]) in want:
                    sc_parties[int(q[0])] = q[7] + " " + q[8]
    n_entries = collections.Counter((r["by"], r["target"]) for r in lrows)
    seen = set()
    out_l = []
    for r in lrows:
        k = (r["by"], r["target"], r["kind"])
        if k in seen:
            continue
        if r["claim"] == "orderHead" and r["kind"] not in KINDS:
            continue
        seen.add(k)
        ocap = set(M.toks(sc_parties.get(r["by"], "")))
        if not (ocap & ttoks(r["target"])):
            st["lists_refused_caption"] += 1
            refused.append(("lists", r["by"], r["target"], "caption"))
            continue
        if r["kind"] in STATUS and r["scope"] == "all" and                 len(node_dk.get(r["target"], ())) > n_entries[(r["by"], r["target"])]:
            r["scope"] = "unknown"
            st["lists_scope_unknown_consolidated"] += 1
        r["rule"] = r["rule"] + "-v2"
        out_l.append(r)
        st["lists_rows_" + r["kind"]] += 1
    for name, rows in (("rows_bridge.jsonl", out_b), ("rows_remandcap.jsonl", out_r), ("rows_lists.jsonl", out_l)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline=NL) as f:
            for r in rows:
                f.write(json.dumps(r) + NL)
        st[name] = len(rows)
    with open(os.path.join(WORK, "build_refused.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for r in refused:
            f.write("\t".join(map(str, r)) + NL)
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "build_stats.json"), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
