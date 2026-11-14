"""shadow13: round-7 JSON rows of the round-13 Shadow leftover rules, one file per rule (each audited on its own).

    python -X utf8 round13/agents/shadow13/build13.py
        -> rows_D.jsonl (d13: same person, second docket), rows_S.jsonl (alt13 S: officer successor),
           rows_A.jsonl (alt13 A: agency acronym); work/build13_links.tsv, work/build13_stats.json

Orders: corpus GVR orders of the round-6 memo parse and the order-list nodes of round12/data_orders (the 1,871 nodes
v12a holds; nodes whose docket and date have a corpus order node are left out, as round 12). An order that already
has a history row in v12a (any target) gets no row. Row terms as round-12 build12 (kind / scope / quote from the
order's own words; evidence name:<tokens> within 400 characters of the quote; scope 'unknown' when the target carries
more docket numbers than the order; corpus head-matter orders before 2013 refused, after 2012 claim orderHead).
No answer-key file is read.
"""
import collections
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import alt13 as AL  # noqa: E402
import d13 as D  # noqa: E402

B12, X, C8, R, M, cap10 = AL.B12, AL.X, AL.C8, AL.R, AL.M, AL.cap10
C2, WORK, NL = AL.C2, AL.WORK, AL.NL
PARTS_OK = ("majority", "perCuriam", "plurality")


def row_for(o, t, rule, src, note, st):
    if src == "corpus":
        if o["part"] == "headmatter":
            if o["date"] < 20130101:
                st[rule + "_refused_headmatter_pre2013"] += 1
                return None
            claim = "orderHead"
        elif o["part"] in PARTS_OK:
            claim = "-"
        else:
            st[rule + "_refused_part_" + o["part"]] += 1
            return None
        q0, q1 = o["disp"]
        ev = B12.evidence({"caps": [R.one_caption(o, True) or ""], "title": ""}, t, o["T"], q0, q1, o["off"])
        ndk = max(1, len(o["caps"]))
    else:
        claim = "-"
        q0, q1 = o["disp"]
        ev = B12.evidence(o, t, o["T"], q0, q1, 0)
        ndk = max(1, len(o.get("ndk", ())))
    if not ev:
        st[rule + "_refused_no_name_evidence"] += 1
        return None
    if not R._META:
        R.sibs(o["n"], t)
    scope = o["scope"]
    if scope == "all" and len(R._META["node_dk"].get(t, ())) > ndk:
        scope = "unknown"
        st[rule + "_scope_unknown_consolidated"] += 1
    tag = "shadow13:%s-%s" % ("cap" if src == "corpus" else "olist", rule)
    return {"rule": tag, "table": "history", "by": o["n"], "target": int(t), "kind": o["kind"], "scope": scope,
            "main": [q0, q1], "part": o["part"], "ev": "name:" + " ".join(ev[:3]), "anchor": None, "anchor_part": "",
            "text": "by", "claim": claim, "note": note}


def main():
    os.makedirs(WORK, exist_ok=True)
    base = D.base_hist()
    st = collections.Counter()
    rows = {"D": [], "S": [], "A": []}
    links = []
    # order-list nodes (full order dicts injected before any minimal one)
    nodes = AL.node_orders()
    nset = {o["n"] for o in nodes}
    # --- D: corpus (shadow10 cap_cand) + nodes (shadow12 build12 recs on round12/data_orders)
    cand = pickle.load(open(os.path.join(C2, "round10/agents/shadow10/work/cap_cand.pkl"), "rb"))
    nrec = {}
    for lid, (n, rec, date, docket, title) in pickle.load(open(D.NODE_RECS, "rb")).items():
        if n in nset:
            nrec[n] = rec
    for src, recs in (("corpus", cand), ("node", nrec)):
        dom = {o: D.domain(r) for o, r in recs.items()}
        dom = {o: g for o, g in dom.items() if g}
        C8.texts({t for g in dom.values() for x in g for t in x})
        for o_n in sorted(dom):
            st["D_%s_domain" % src] += 1
            t = D.pick(recs[o_n], o_n, "Dwin")
            if t is None:
                continue
            if base.get(o_n):
                st["D_%s_has_v12a_row_%s" % (src, "same" if t in base[o_n] else "other")] += 1
                continue
            o = R.orders()[o_n]
            gs = dom[o_n]
            note = ("%s: D, full-name candidates of the court below on %d dockets (%s); one docket holds a judgment "
                    "in the filing window of the order's docket number (on or after %d, before %d): the latest, "
                    "%d days before the order") % (
                "caption link" if src == "corpus" else "order-list node %s (%s)" % (o.get("lid"), o.get("docket")),
                len(gs), " | ".join(",".join(map(str, sorted(g))) for g in gs), cap10.term_end(o_n) - 20000,
                cap10.term_end(o_n), recs[o_n]["T"][t]["days"])
            r = row_for(o, t, "D", src, note, st)
            links.append(("D", src, o_n, t, "row" if r else "refused"))
            if r:
                rows["D"].append(r)
    # --- S and A: orders with no both-sides candidate
    corp = AL.corpus_orders()
    for src, objs in (("corpus", corp), ("node", nodes)):
        for o in objs:
            if base.get(o["n"]):
                continue
            if src == "node" and X.candidates(o)[0] is not None:
                continue
            for rule in ("S", "A"):
                rec, why = AL.alt_candidates(o, rule)
                if rec is None:
                    continue
                st["%s_%s_domain" % (rule, src)] += 1
                t, how = AL.pick(rec, rule)
                if t is None:
                    st["%s_%s_%s" % (rule, src, how)] += 1
                    continue
                what = "same office" if rule == "S" else "agency acronym spelled out"
                note = ("%s: %s, caption tie by name on one side and %s on the other; %d such candidate(s) of the "
                        "court below, pick %s; target %d days before the order") % (
                    "caption link" if src == "corpus" else "order-list node %s (%s)" % (o.get("lid"), o.get("docket")),
                    rule, what, len(rec["T"]), how, rec["T"][t]["days"])
                r = row_for(o, t, rule, src, note, st)
                links.append((rule, src, o["n"], t, "row" if r else "refused"))
                if r:
                    rows[rule].append(r)
    seen = set()
    for k in ("D", "S", "A"):
        keep = []
        for r in rows[k]:
            key = (r["by"], r["target"])
            if key in seen:
                st[k + "_dup_pair"] += 1
                continue
            seen.add(key)
            keep.append(r)
        rows[k] = keep
        st[k + "_rows"] = len(keep)
        with open(os.path.join(HERE, "rows_%s.jsonl" % k), "w", encoding="utf-8", newline=NL) as f:
            for r in keep:
                f.write(json.dumps(r) + NL)
    with open(os.path.join(WORK, "build13_links.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for x in links:
            o = R.orders()[x[2]]
            f.write("\t".join(map(str, x + (o["date"], o.get("docket", ""), R.one_caption(o, True), R.title(x[3]))))
                    + NL)
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "build13_stats.json"), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
