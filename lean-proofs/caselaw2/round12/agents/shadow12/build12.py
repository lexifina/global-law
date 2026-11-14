"""shadow12: rule C8 rows (several full-name candidates on one docket -> the latest judgment before the end of the
order's docket-term year; c8_12.pick rule C8fj) as round-7 JSON rows for round12/certify12.py.

    python -X utf8 round12/agents/shadow12/build12.py corpus --tag NAME
        corpus GVR orders (round-6 memo parse; shadow10 work/cap_cand.pkl candidates) not linked by v11d (any target)
    python -X utf8 round12/agents/shadow12/build12.py nodes --data round11/data_orders --tag NAME [--skip-ids F]
        order-list nodes: C6 / K9 as round 11 (olink11); C8 only where neither links. Rows of C8 only, unless
        --all-rules (then C6/K9 rows too, for new nodes).
Row terms as round-10 build10 / round-11 build11 (kind / scope / quote from the order's own words; evidence
name:<tokens> within 400 characters of the quote; scope "unknown" when the target carries more docket numbers).
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
import c8_12 as C8  # noqa: E402

C2 = C8.C2
sys.path.insert(0, os.path.join(C2, "round11", "agents", "shadow11"))
import olink11 as X  # noqa: E402
import build11 as B11  # noqa: E402

R, M, L, cap10 = X.R, X.M, X.L, X.cap10
WORK = os.path.join(HERE, "work")
X.TOK11 = os.path.join(WORK, "tokidx12.pkl")      # never write into round11/
NL = chr(10)
PARTS_OK = ("majority", "perCuriam", "plurality")
RULE = "C8v2"


RX_SUBSPLIT = re.compile(r";\s*(?:and\s+)?")
RX_V = re.compile(r"\s[Vv]\.?\s")
SUB0 = 950_000_000


def sub_captions(cap):
    """An order-list entry that disposes of consolidated cases prints one caption per case, joined by '; ' or
    '; and ' ('A, Petitioner v. United States; and B, Petitioner v. United States'): the captions, when >= 2."""
    parts = [x.strip() for x in RX_SUBSPLIT.split(cap or "") if RX_V.search(" " + x + " ")]
    return parts if len(parts) >= 2 else []


def make_order12(sp):
    o, why = X.make_order(sp)
    if o is not None and sp.get("sub"):
        c = X.norm_caption(sp["sub"])
        o["title"], o["caps"] = c, [c]
    return o, why


def link_specs12(specs):
    """olink11.link_specs with make_order12 (a sub-caption spec takes its own caption)."""
    out, recs = {}, {}
    for sp in specs:
        o, why = make_order12(sp)
        if o is None:
            out[sp["n"]] = (None, None, None, why)
            continue
        X.inject(o)
        rec, why = X.candidates(o)
        if rec is None:
            out[sp["n"]] = (o, None, None, why)
            continue
        recs[o["n"]] = (o, rec)
    need = set()
    for o, rec in recs.values():
        if cap10.full_names(R.one_caption(o, True) or ""):
            need |= set(rec["T"])
    X.heads(need)
    for n, (o, rec) in recs.items():
        X.mark_full(o, rec)
        t = X.pick_c6(rec)
        out[n] = (o, rec, t, "linked" if t is not None else ("no_full_name" if not rec["has_full"] else "not_unique"))
    return out


def base_hist():
    base = collections.defaultdict(set)
    with open(os.path.join(C2, "round11/stage/v11d/history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 3)
            base[int(p[2])].add(int(p[1]))
    return base


def evidence(o, t, T, q0, q1, off):
    ocap = M.toks(o["caps"][0] if o.get("caps") else o["title"])
    ttk = M.toks(R.title(t))
    shared = [x for x in ocap if x in ttk]
    w = M.words_str(T[max(0, q0 - 400 - off):max(0, q1 + 400 - off)])
    ev = []
    for x in shared:
        if (" " + x + " ") in w and x not in ev:
            ev.append(x)
    return ev


def c8_note(rec, t, lead):
    good = sorted(x for x in rec["T"] if rec["T"][x].get("full"))
    dropped = [x for x in good if C8.not_judgment(x)]
    return "%s: C8, %d full-name candidates on one docket of the court below (%s), post-judgment orders set aside " \
           "(%s), latest before %d; target %d days before the order" % (
               lead, len(good), ",".join(map(str, good)), ",".join(map(str, dropped)) or "none",
               cap10.term_end(rec["_o"]), rec["T"][t]["days"])


def corpus(a):
    orders = R.orders()
    cand = pickle.load(open(os.path.join(C2, "round10/agents/shadow10/work/cap_cand.pkl"), "rb"))
    node_dk = pickle.load(open(os.path.join(C2, "round8/agents/orderdock/work/meta.pkl"), "rb"))["node_dk"]
    base = base_hist()
    C8.texts({t for r in cand.values() if r.get("has_full") for t in r["T"] if r["T"][t].get("full")})
    st = collections.Counter()
    rows, links = [], []
    for o_n, rec in sorted(cand.items()):
        if cap10.pick(rec, "C6_fullname_unique_nosib") is not None:
            continue
        t = C8.pick(rec, RULE, o_n)
        if t is None:
            continue
        rec["_o"] = o_n
        o = orders[o_n]
        st["linked"] += 1
        links.append((o_n, t, o["date"], o["kind"], o["part"], RULE))
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
        q0, q1 = o["disp"]
        ev = evidence({"caps": [R.one_caption(o, True) or ""], "title": ""}, t, o["T"], q0, q1, o["off"])
        if not ev:
            st["refused_no_name_evidence"] += 1
            continue
        scope = o["scope"]
        if scope == "all" and len(node_dk.get(t, ())) > max(1, len(o["caps"])):
            scope = "unknown"
            st["scope_unknown_consolidated"] += 1
        rows.append({"rule": "shadow12:cap-C8", "table": "history", "by": o_n, "target": int(t),
                     "kind": o["kind"], "scope": scope, "main": [q0, q1], "part": o["part"],
                     "ev": "name:" + " ".join(ev[:3]), "anchor": None, "anchor_part": "", "text": "by",
                     "claim": claim, "note": c8_note(rec, t, "caption link")})
        st["rows"] += 1
        st["rows_" + o["kind"]] += 1
        st["rows_post2013" if o["date"] >= 20130101 else "rows_pre2013"] += 1
    return rows, links, st


def nodes(a):
    skip = set()
    if a.skip_ids:
        skip = {x.strip() for x in open(a.skip_ids, encoding="utf-8") if x.strip()}
    rows_in = B11.read_nodes(a.data)
    nm = B11.node_map(a.data) if not a.file_order else None
    src_map = "nodes overlay"
    if nm is None:
        nm = {r["local_id"]: B11.N0 + i for i, r in enumerate(rows_in)}
        src_map = "file-order"
    corpus_dk = set()
    for o in R.orders().values():
        for d in re.split(r"[;,&]|\band\b", o.get("docket") or ""):
            if B11.dk_compact(d):
                corpus_dk.add((B11.dk_compact(d), o["date"]))
    st = collections.Counter()
    st["map_" + src_map] = 1
    specs, meta, submeta = [], {}, {}
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
        if any((B11.dk_compact(d), int(r["date"])) in corpus_dk for d in dks):
            st["in_corpus"] += 1
            continue
        n = nm[lid]
        specs.append({"n": n, "docket": r["docket"], "caption": r["caption"], "date": int(r["date"]), "text": text,
                      "part": "majority"})
        meta[n] = (lid, dks)
        if a.sub:
            for j, sc in enumerate(sub_captions(r["caption"])):
                sn = SUB0 + len(submeta)
                submeta[sn] = (n, j, sc)
                specs.append(dict(specs[-1], n=sn, sub=sc))
    if not a.no_index:
        objs = [o for o, _w in (make_order12(sp) for sp in specs) if o is not None]
        X.build_tokidx(objs)
    res = link_specs12(specs)
    objs = []
    for sp in specs:
        o = R.orders().get(sp["n"])
        if o is not None and (o["n"] in meta or o["n"] in submeta):
            objs.append(o)
    k9 = X.remand_specs(objs)
    need = set()
    for n, (o, rec, t, why) in res.items():
        if rec is not None and rec.get("has_full"):
            need |= {x for x in rec["T"] if rec["T"][x].get("full")}
    C8.texts(need)
    pickle.dump({meta[n][0]: (n, rec, o["date"], o.get("docket"), o["title"]) for n, (o, rec, _t, _w) in res.items()
                 if rec is not None and n in meta}, open(os.path.join(WORK, "c8_recs_%s.pkl" % a.tag), "wb"))
    node_dk = None
    rows, links = [], []
    linked_nodes = set()
    seen = set()
    for n in sorted(meta) + sorted(submeta):
        if n in submeta:
            node, j, sc = submeta[n]
            if node in linked_nodes:
                continue             # the whole caption links: sub-captions are not read
            lid, dks = meta[node][0] + "#%d" % j, [d for d in meta[node][1]]
        else:
            node = n
            lid, dks = meta[n]
        o, rec, t, why = res.get(n, (None, None, None, "none"))
        rule = "C6"
        tk, krec, _kw = k9.get(n, (None, None, "no_K9"))
        if t is not None and tk is not None and tk != t:
            t, why = None, "rules_disagree"
        elif t is None and tk is not None:
            t, rule, why = tk, "K9", "linked_K9"
        if t is None and why == "not_unique" and rec is not None:
            t8 = C8.pick(rec, RULE, n)
            if t8 is not None:
                t, rule, why = t8, "C8", "linked_C8"
            else:
                g = [x for x in rec["T"] if rec["T"][x].get("full")]
                why = "c8_none_full%d" % min(len(g), 2)
        st[("subwhy_" if n in submeta else "why_") + why] += 1
        if t is not None:
            linked_nodes.add(node)
        links.append((lid, node, t if t is not None else "-", o["date"] if o else "-", o["kind"] if o else "-",
                      (o["courts"][0] if o and o["courts"] else "-"), why))
        if t is None or (rule != "C8" and n not in submeta and not a.all_rules):
            continue
        if (node, t) in seen:
            st["dup_pair"] += 1
            continue
        seen.add((node, t))
        q0, q1 = o["disp"]
        ev = evidence(o, t, o["T"], q0, q1, 0)
        if not ev:
            st["refused_no_name_evidence"] += 1
            continue
        scope = o["scope"]
        if not R._META:
            R.sibs(n, t)
        node_dk = R._META["node_dk"]
        if scope == "all" and len(node_dk.get(t, ())) > max(1, 1 if n in submeta else len(dks)):
            scope = "unknown"
            st["scope_unknown_consolidated"] += 1
        if rule == "C8":
            rec["_o"] = n
            note = c8_note(rec, t, "order-list node %s (%s)" % (lid, o["docket"]))
        elif rule == "C6":
            note = "order-list node %s (%s): caption link C6, %d both-sides candidate(s) of the court below, " \
                   "target %d days before the order" % (lid, o["docket"], len(rec["T"]), rec["T"][t]["days"])
        else:
            bs = krec["T"][t]["B"]
            good = sorted(b for b, s in bs.items() if R.ok("K9", s))
            sig = sorted({k for b in good for k in ("capB", "citeBT", "cue", "reason", "odocket", "odate")
                          if bs[b][k]})
            note = "order-list node %s (%s): remand decision(s) of the court below on the same docket: %s " \
                   "(signals %s)" % (lid, o["docket"], ",".join(map(str, good)), ",".join(sig))
        tag = "shadow12:olist-C8" if rule == "C8" else "shadow11:olist-" + rule
        if n in submeta:
            tag = "shadow12:olist-sub-" + rule
            note = note.replace("order-list node %s" % lid, "order-list node %s, caption %d of %d ('%s')" % (
                meta[node][0], j + 1, len(sub_captions(o.get("spec_caption", ""))), sc[:80]))
        rows.append({"rule": tag, "table": "history", "by": node, "target": int(t),
                     "kind": o["kind"], "scope": scope, "main": [q0, q1], "part": o["part"],
                     "ev": "name:" + " ".join(ev[:3]), "anchor": None, "anchor_part": "", "text": "by", "claim": "-",
                     "note": note})
        st["rows"] += 1
        st["rows_" + tag.split(":")[1]] += 1
        st["rows_y%d" % (o["date"] // 10000)] += 1
    return rows, links, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("corpus", "nodes"))
    ap.add_argument("--tag", required=True)
    ap.add_argument("--data", default=os.path.join(C2, "round11", "data_orders"))
    ap.add_argument("--skip-ids", default=None)
    ap.add_argument("--no-index", action="store_true")
    ap.add_argument("--all-rules", action="store_true")
    ap.add_argument("--file-order", action="store_true")
    ap.add_argument("--sub", action="store_true", help="also the sub-captions of consolidated entries (unlinked nodes)")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    rows, links, st = corpus(a) if a.mode == "corpus" else nodes(a)
    with open(os.path.join(HERE, "rows_%s.jsonl" % a.tag), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r) + NL)
    with open(os.path.join(WORK, "build12_%s_links.tsv" % a.tag), "w", encoding="utf-8", newline=NL) as f:
        for r in links:
            f.write("\t".join(map(str, r)) + NL)
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "build12_%s_stats.json" % a.tag), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
