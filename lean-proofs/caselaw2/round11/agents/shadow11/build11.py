"""shadow11 part A: history rows with `by` = a round-11 order-list node (round11/data_orders) -> the decision below,
by the round-10 C6 rule ported to order specs (olink11), as round-7 JSON rows for round11/certify11.py.

    python -X utf8 round11/agents/shadow11/build11.py [--data round11/data_orders] [--tag NAME] [--rules C6[,C10]]
        -> rows_<NAME>.jsonl, work/build11_<NAME>_stats.json, work/build11_<NAME>_links.tsv (every node: why)

Node ids: round11/nodes11.py when present, else N + file order (FORMAT.md: N = graph/nodes.count).
A node whose docket number and date are those of a corpus Supreme Court order (memo parse) is skipped (the corpus
order is the node; no duplicate).
Row terms as round-10 build10.py (class cap-C6): kind / scope / quote from the node's own text (memolib.classify on
the words after the printed caption); evidence name:<tokens> = party-name tokens the normalised caption shares with
the target's title, whole words within 400 characters of the quote (none -> no row); scope "unknown" when the
target carries more docket numbers than the node has docket numbers.
No answer-key file is read.
"""
import argparse
import collections
import json
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import olink11 as X  # noqa: E402

R, M, L, C2 = X.R, X.M, X.L, X.C2
WORK = os.path.join(HERE, "work")
NL = chr(10)
N0 = 6892454


def node_map(data):
    sys.path.insert(0, os.path.join(C2, "round11"))
    try:
        import nodes11
    except ImportError:
        return None
    nodes11.activate(data)
    return {r["local_id"]: nodes11.node_of(r["local_id"]) for r in read_nodes(data)}


def read_nodes(data):
    out = []
    with open(os.path.join(data, "nodes.tsv"), encoding="utf-8") as f:
        hdr = f.readline().rstrip(NL).split("\t")
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) != len(hdr):
                continue
            out.append(dict(zip(hdr, p)))
    return out


def dk_compact(s):
    return re.sub(r"[^0-9a-z]", "", (s or "").lower().replace("no.", ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(C2, "round11", "data_orders"))
    ap.add_argument("--tag", default="olist")
    ap.add_argument("--part", default="majority")
    ap.add_argument("--keep-dup", action="store_true", help="pipeline test: keep nodes that duplicate a corpus order")
    ap.add_argument("--no-index", action="store_true", help="reuse work/tokidx11.pkl")
    ap.add_argument("--rules", default="C6,K9")
    ap.add_argument("--skip-ids", default=None, help="file of local ids already built (one per line): not rebuilt")
    a = ap.parse_args()
    skip = set()
    if a.skip_ids:
        skip = {x.strip() for x in open(a.skip_ids, encoding="utf-8") if x.strip()}
    rules = a.rules.split(",")
    rows_in = read_nodes(a.data)
    nm = node_map(a.data)
    if nm is None:
        nm = {r["local_id"]: N0 + i for i, r in enumerate(rows_in)}
        src_map = "file-order"
    else:
        src_map = "nodes11"
    corpus = set()
    for o in R.orders().values():
        for d in re.split(r"[;,&]|\band\b", o.get("docket") or ""):
            if dk_compact(d):
                corpus.add((dk_compact(d), o["date"]))
    st = collections.Counter()
    specs, meta = [], {}
    for r in rows_in:
        lid = r["local_id"]
        st["nodes"] += 1
        if lid in skip:
            st["skipped_built"] += 1
            continue
        p = os.path.join(a.data, "text", lid + ".txt")
        if not os.path.exists(p) or lid not in nm:
            st["no_text_or_id"] += 1
            continue
        text = open(p, encoding="utf-8", newline="").read()
        dks = [d for d in r["docket"].split(";") if d and d != "-"]
        if any((dk_compact(d), int(r["date"])) in corpus for d in dks) and not a.keep_dup:
            st["in_corpus"] += 1
            continue
        n = nm[lid]
        specs.append({"n": n, "docket": r["docket"], "caption": r["caption"], "date": int(r["date"]), "text": text,
                      "part": a.part})
        meta[n] = (lid, dks)
    if not a.no_index:
        objs = [o for o, _w in (X.make_order(sp) for sp in specs) if o is not None]
        X.build_tokidx(objs)
    res = X.link_specs(specs) if "C6" in rules else {}
    k9 = {}
    if "K9" in rules:
        objs = []
        for sp in specs:
            o = R.orders().get(sp["n"])
            if o is None:
                o, _w = X.make_order(sp)
                if o is None:
                    continue
                X.inject(o)
            objs.append(o)
        k9 = X.remand_specs(objs)
    rows, links = [], []
    for n in sorted(meta):
        lid, dks = meta[n]
        o, rec, t, why = res.get(n, (R.orders().get(n), None, None, "C6_off"))
        rule = "C6"
        tk, krec, kwhy = k9.get(n, (None, None, "no_K9"))
        if t is not None and tk is not None and tk != t:
            st["C6_K9_disagree"] += 1
            t, why = None, "rules_disagree"
        elif t is None and tk is not None:
            t, rule, why = tk, "K9", "linked_K9"
        elif t is not None and tk is not None:
            st["C6_K9_same"] += 1
        st["why_" + why] += 1
        links.append((lid, n, t if t is not None else "-", o["date"] if o else "-", o["kind"] if o else "-",
                      (o["courts"][0] if o and o["courts"] else "-"), why))
        if t is None:
            continue
        ocap = M.toks(o["caps"][0])
        ttk = M.toks(R.title(t))
        shared = [x for x in ocap if x in ttk]
        T = o["T"]
        q0, q1 = o["disp"]
        w = M.words_str(T[max(0, q0 - 400):q1 + 400])
        ev = []
        for x in shared:
            if (" " + x + " ") in w and x not in ev:
                ev.append(x)
        if not ev:
            st["refused_no_name_evidence"] += 1
            continue
        scope = o["scope"]
        if not R._META:
            R.sibs(n, t)
        node_dk = R._META["node_dk"]
        if scope == "all" and len(node_dk.get(t, ())) > max(1, len(dks)):
            scope = "unknown"
            st["scope_unknown_consolidated"] += 1
        if rule == "C6":
            r = rec["T"][t]
            note = "order-list node %s (%s): caption link C6, %d both-sides candidate(s) of the court below, " \
                   "target %d days before the order" % (lid, o["docket"], len(rec["T"]), r["days"])
        else:
            bs = krec["T"][t]["B"]
            good = sorted(b for b, s in bs.items() if R.ok("K9", s))
            sig = sorted({k for b in good for k in ("capB", "citeBT", "cue", "reason", "odocket", "odate")
                          if bs[b][k]})
            note = "order-list node %s (%s): remand decision(s) of the court below on the same docket: %s " \
                   "(signals %s)" % (lid, o["docket"], ",".join(map(str, good)), ",".join(sig))
        rows.append({"rule": "shadow11:olist-" + rule, "table": "history", "by": n, "target": int(t),
                     "kind": o["kind"], "scope": scope, "main": [q0, q1], "part": o["part"],
                     "ev": "name:" + " ".join(ev[:3]), "anchor": None, "anchor_part": "", "text": "by", "claim": "-",
                     "note": note})
        st["rows"] += 1
        st["rows_" + rule] += 1
        st["rows_" + o["kind"]] += 1
        st["rows_y%d" % (o["date"] // 10000)] += 1
    with open(os.path.join(HERE, "rows_%s.jsonl" % a.tag), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r) + NL)
    with open(os.path.join(WORK, "build11_%s_links.tsv" % a.tag), "w", encoding="utf-8", newline=NL) as f:
        for r in links:
            f.write("\t".join(map(str, r)) + NL)
    st["map_" + src_map] = 1
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "build11_%s_stats.json" % a.tag), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
