"""Round 8 `orderdock`: Supreme Court orders -> the decision below through a docket bridge.

    python -X utf8 round8/agents/orderdock/dock.py meta      lower-court docket index      -> work/meta.pkl
    python -X utf8 round8/agents/orderdock/dock.py edges     decisions citing each order    -> work/citers.pkl
    python -X utf8 round8/agents/orderdock/dock.py probe     bridge candidates + validation -> work/probe.json

Inputs: round6/history/cache/*.meta.tsv.gz (node, date, court2, docket), graph/edges.bin (citing, cited),
round6 memo work/orders.pkl (parsed SC orders: kind, courts below, captions, "Reported below" citations).
No answer-key file is read.
"""
import collections
import json
import os
import pickle
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HIST = os.path.join(C2, "round6", "history")
MEMO = os.path.join(HIST, "rules", "memo")
sys.path.insert(0, HIST)
sys.path.insert(0, MEMO)
import r6lib as L  # noqa: E402

WORK = os.path.join(HERE, "work")
NL = chr(10)
SC = 2906

RX_TOK = re.compile(r"[A-Z0-9]+(?:[-:./][A-Z0-9]+)*")


def docket_tokens(s):
    """Docket string -> normalised docket numbers (each must hold a digit and be at least 4 characters)."""
    s = s.upper().replace("–", "-").replace("—", "-").replace("‑", "-")
    s = re.sub(r"\bNOS?\.?\s*", " ", s)
    s = re.sub(r"(?<=\d)\s*-\s*(?=[A-Z0-9])", "-", s)
    out = []
    for m in RX_TOK.finditer(s):
        t = m.group(0).strip(".:/-")
        if len(t) >= 4 and re.search(r"\d", t) and not re.fullmatch(r"(?:1[6-9]|20)\d\d", t):
            if t not in out:
                out.append(t)
    return tuple(out[:8])


def _meta_shard(path):
    out = []
    for r in L.meta_rows(path):
        c = int(r[4]) if r[4].lstrip("-").isdigit() else -1
        if c == SC or not r[5]:
            continue
        tk = docket_tokens(r[5])
        if tk:
            out.append((int(r[0]), c, tk))
    return out


def stage_meta():
    paths = L.shards(".meta.tsv.gz")
    node_dk = {}
    idx = collections.defaultdict(list)
    for out in L.pmap(_meta_shard, paths, procs=10):
        for n, c, tk in out:
            node_dk[n] = tk
            for t in tk:
                idx[(c, t)].append(n)
    with open(os.path.join(WORK, "meta.pkl"), "wb") as f:
        pickle.dump({"node_dk": node_dk, "idx": dict(idx)}, f, protocol=4)
    print("nodes with docket", len(node_dk), "keys", len(idx))


def load_orders():
    d = pickle.load(open(os.path.join(MEMO, "work", "orders.pkl"), "rb"))
    return d["orders"]


def stage_edges():
    orders = load_orders()
    onodes = np.array(sorted({o["n"] for o in orders}), dtype=np.uint32)
    e = np.fromfile(os.path.join(L.W, "graph", "edges.bin"), dtype=np.uint32).reshape(-1, 2)
    m = np.isin(e[:, 1], onodes)
    sub = e[m]
    citers = collections.defaultdict(list)
    for s, d in sub.tolist():
        citers[d].append(s)
    with open(os.path.join(WORK, "citers.pkl"), "wb") as f:
        pickle.dump(dict(citers), f, protocol=4)
    print("orders", len(onodes), "edges to orders", int(m.sum()), "orders cited", len(citers))


def stage_probe():
    import memolib as M
    courts = M.Courts()
    F = L.Facts()
    orders = load_orders()
    meta = pickle.load(open(os.path.join(WORK, "meta.pkl"), "rb"))
    node_dk, idx = meta["node_dk"], meta["idx"]
    citers = pickle.load(open(os.path.join(WORK, "citers.pkl"), "rb"))
    st = collections.Counter()
    val = collections.Counter()
    rows = []
    for o in orders:
        ids = set()
        for k in o["courts"]:
            if k is not None:
                ids.update(courts.group.get(k, ()))
        if not ids:
            st["no_court"] += 1
            continue
        od = o["date"]
        oo = M.ordinal(od)
        truth = {t for t, *_ in o.get("rbn", []) if t is not None}
        # bridge S: a decision of the court below, dated before the order, whose own text cites the order
        # bridge R: a decision of the court below, dated on/after the order, that cites the order; its docket
        #           numbers name earlier decisions of the same court (before the order, <= 10 years)
        S, R = set(), collections.defaultdict(set)
        for b in citers.get(o["n"], ()):
            cb = int(F.court[b])
            if cb not in ids:
                continue
            db = int(F.date[b])
            if db < od:
                if oo - M.ordinal(db) <= 3650:
                    S.add(b)
                continue
            for t in node_dk.get(b, ()):
                for n in idx.get((cb, t), ()):
                    if n == b:
                        continue
                    dn = int(F.date[n])
                    if dn < od and 0 < oo - M.ordinal(dn) <= 3650:
                        R[n].add(b)
        kinds = []
        if len(S) == 1:
            kinds.append(("S", next(iter(S))))
        if len(R) == 1:
            kinds.append(("R", next(iter(R))))
        st["S_any"] += bool(S)
        st["S_uniq"] += len(S) == 1
        st["R_any"] += bool(R)
        st["R_uniq"] += len(R) == 1
        if o["date"] >= 20130101:
            st["2013_orders"] += 1
            st["2013_S_uniq"] += len(S) == 1
            st["2013_R_uniq"] += len(R) == 1
            st["2013_any_uniq"] += bool(kinds)
        if truth:
            for kk, t in kinds:
                val[kk + ("_right" if t in truth else "_wrong")] += 1
        for kk, t in kinds:
            rows.append((o["n"], o["date"], o["kind"], kk, t, sorted(R.get(t, ())) if kk == "R" else []))
    json.dump({"stats": st, "val": val}, open(os.path.join(WORK, "probe.json"), "w"), indent=1)
    with open(os.path.join(WORK, "probe.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write("\t".join(str(x) for x in r) + NL)
    print(dict(st))
    print(dict(val))


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    if sys.argv[1] != "remand":
        {"meta": stage_meta, "edges": stage_edges, "probe": stage_probe}[sys.argv[1]]()


def stage_remand():
    """Bridge R2 (remand docket): order O (any kind) of the Supreme Court; B = a decision of a court O names, dated
    after O, whose text cites O's page (graph edge to any Supreme Court decision carrying one of O's page citations),
    whose title shares a party-name token with O's caption; T = the decision of B's court that shares one of B's
    docket numbers, dated before O and at most 1,095 days older, and whose title shares a party-name token with O's
    caption. O is linked when exactly one T results over all such B."""
    import memolib as M
    courts = M.Courts()
    F = L.Facts()
    orders = load_orders()
    meta = pickle.load(open(os.path.join(WORK, "meta.pkl"), "rb"))
    node_dk, idx = meta["node_dk"], meta["idx"]
    page_nodes = collections.defaultdict(set)   # page key -> SC nodes (all SC decisions)
    for p in L.shards(".meta.tsv.gz"):
        if not os.path.basename(p).startswith("supreme-court"):
            continue
        for r in L.meta_rows(p):
            for c in r[9].split("|"):
                k = L.reader_common().norm_cite(c.strip())
                if k:
                    page_nodes[k].add(int(r[0]))
    sc_nodes = np.array(sorted({n for v in page_nodes.values() for n in v}), dtype=np.uint32)
    e = np.fromfile(os.path.join(L.W, "graph", "edges.bin"), dtype=np.uint32).reshape(-1, 2)
    sub = e[np.isin(e[:, 1], sc_nodes)]
    del e
    citers = collections.defaultdict(list)
    for s, d in sub.tolist():
        citers[d].append(s)
    C = L.reader_common()
    tt = {}

    def toks(n):
        if n not in tt:
            tt[n] = set(M.toks(L.node_row(n)[6]))
        return tt[n]

    st = collections.Counter()
    out = []
    for o in orders:
        ids = set()
        for k in o["courts"]:
            if k is not None:
                ids.update(courts.group.get(k, ()))
        if not ids:
            continue
        od, oo = o["date"], M.ordinal(o["date"])
        ocap = set(M.toks(" ".join(o["caps"]) or o["title"]))
        if not ocap:
            continue
        sib = set()
        for c in (o["cites"] or "").split("|"):
            k = C.norm_cite(c.strip())
            if k:
                sib |= page_nodes.get(k, set())
        Bs = {b for x in sib for b in citers.get(x, ())}
        T = collections.defaultdict(set)
        for b in Bs:
            cb = int(F.court[b])
            if cb not in ids or int(F.date[b]) < od or not (ocap & toks(b)):
                continue
            for tk in node_dk.get(b, ()):
                for n in idx.get((cb, tk), ()):
                    if n == b:
                        continue
                    dn = int(F.date[n])
                    if dn < od and 0 < oo - M.ordinal(dn) <= 1095 and (ocap & toks(n)):
                        T[n].add(b)
        if not T:
            continue
        st["any"] += 1
        if len(T) != 1:
            st["several"] += 1
            continue
        (t, bs), = T.items()
        st["linked"] += 1
        st["linked_" + o["kind"]] += 1
        out.append((o["n"], t, len(bs), ";".join(str(b) for b in sorted(bs)[:6]), o["kind"], o["date"]))
    with open(os.path.join(WORK, "remand_links.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("order\ttarget\tn_bridges\tbridges\tkind\tdate" + NL)
        for r in out:
            f.write("\t".join(str(x) for x in r) + NL)
    print(dict(st))


if __name__ == "__main__" and sys.argv[1] == "remand":
    stage_remand()
