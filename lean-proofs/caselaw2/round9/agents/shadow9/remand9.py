"""shadow9 (round 9, move 4): Supreme Court order -> decision below through the remand docket bridge, with every
independent second signal recorded per candidate.

    python -X utf8 round9/agents/shadow9/remand9.py cand     -> work/cand.pkl  (all orders of the memo parse)

General rule (corpus-wide; no answer-key file is read):
  O = a Supreme Court order of the round-6 memo parse (orders.pkl) with a court below.
  B = a decision of a court O names, dated on/after O and at most 5 years later, whose text cites O (a graph edge to
      any Supreme Court node carrying one of O's page citations).
  T = a decision of B's court that shares one of B's docket numbers (cache meta), dated before O and at most 1,095
      days older.
  Signals recorded per (O, T):
    capT   the target's title shares a party-name token with O's caption
    capB   the bridge's title shares a party-name token with O's caption
    citeBT a bridge B cites T (graph edge B -> T): the remand opinion names the decision below
    reason a bridge B cites a Supreme Court decision O itself cites (the GVR's "in light of X" case)
    latest T is the latest decision of B's court on that docket dated before O
    days   O.date - T.date in days
Inputs: round6/history/cache/*.meta.tsv.gz, graph/edges.bin, graph/nodes.tsv (titles), round6 memo orders.pkl,
round8 orderdock work/meta.pkl (lower-court docket index).
"""
import collections
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HIST = os.path.join(C2, "round6", "history")
MEMO = os.path.join(HIST, "rules", "memo")
OD = os.path.join(C2, "round8", "agents", "orderdock")
sys.path.insert(0, HIST)
sys.path.insert(0, MEMO)
import r6lib as L  # noqa: E402
import memolib as M  # noqa: E402

WORK = os.path.join(HERE, "work")
SC = 2906


class Titles:
    def __init__(self):
        self.off = L._offsets()
        self.f = open(L.NODES, "rb")
        self.c = {}

    def toks(self, n):
        if n not in self.c:
            self.f.seek(int(self.off[n]))
            r = self.f.readline().decode("utf-8").rstrip("\r\n").split("\t")
            self.c[n] = M.toks(r[6]) if len(r) > 6 else frozenset()
        return self.c[n]


def stage_cand():
    courts = M.Courts()
    F = L.Facts()
    orders = pickle.load(open(os.path.join(MEMO, "work", "orders.pkl"), "rb"))["orders"]
    meta = pickle.load(open(os.path.join(OD, "work", "meta.pkl"), "rb"))
    node_dk, idx = meta["node_dk"], meta["idx"]
    C = L.reader_common()
    page_nodes = collections.defaultdict(set)
    for p in L.shards(".meta.tsv.gz"):
        if not os.path.basename(p).startswith("supreme-court"):
            continue
        for r in L.meta_rows(p):
            for c in r[9].split("|"):
                k = C.norm_cite(c.strip())
                if k:
                    page_nodes[k].add(int(r[0]))
    sc_all = np.array(sorted({n for v in page_nodes.values() for n in v}), dtype=np.uint32)
    onodes = np.array(sorted({o["n"] for o in orders}), dtype=np.uint32)
    e = np.fromfile(os.path.join(L.W, "graph", "edges.bin"), dtype=np.uint32).reshape(-1, 2)
    sub = e[np.isin(e[:, 1], sc_all)]
    citers = collections.defaultdict(list)
    for s, d in sub.tolist():
        citers[d].append(s)
    oe = e[np.isin(e[:, 0], onodes)]
    o_out = collections.defaultdict(set)
    for s, d in oe.tolist():
        o_out[s].add(d)
    print("edges into SC", len(sub), "order out-edges", len(oe), flush=True)
    # pass 1: bridges per order
    cand_B = {}
    allB = set()
    for o in orders:
        ids = set()
        for k in o["courts"]:
            if k is not None:
                ids.update(courts.group.get(k, ()))
        if not ids:
            continue
        od, oo = o["date"], M.ordinal(o["date"])
        sib = set()
        for c in (o["cites"] or "").split("|"):
            k = C.norm_cite(c.strip())
            if k:
                sib |= page_nodes.get(k, set())
        if not sib:
            continue
        Bs = set()
        for x in sib:
            for b in citers.get(x, ()):
                cb = int(F.court[b])
                db = int(F.date[b])
                if cb in ids and db >= od and M.ordinal(db) - oo <= 1826 and node_dk.get(b):
                    Bs.add(b)
        if Bs:
            cand_B[o["n"]] = (sib, Bs)
            allB |= Bs
    print("orders with a bridge", len(cand_B), "bridges", len(allB), flush=True)
    be = e[np.isin(e[:, 0], np.array(sorted(allB), dtype=np.uint32))]
    del e, sub, oe
    b_out = collections.defaultdict(set)
    for s, d in be.tolist():
        b_out[s].add(d)
    del be
    TT = Titles()
    out = {}
    st = collections.Counter()
    for o in orders:
        if o["n"] not in cand_B:
            continue
        sib, Bs = cand_B[o["n"]]
        od, oo = o["date"], M.ordinal(o["date"])
        ocap = M.toks(" ".join(o["caps"]) or o["title"])
        reason_set = {x for x in o_out.get(o["n"], ()) if int(F.court[x]) == SC} - sib
        T = collections.defaultdict(lambda: {"B": set(), "citeBT": set(), "reason": set(), "capB": set(), "dk": set()})
        for b in Bs:
            cb = int(F.court[b])
            bo = b_out.get(b, set())
            for tk in node_dk.get(b, ()):
                ns = [n for n in idx.get((cb, tk), ()) if n != b and int(F.date[n]) < od
                      and 0 < oo - M.ordinal(int(F.date[n])) <= 1095]
                if not ns:
                    continue
                last = max(int(F.date[n]) for n in ns)
                for n in ns:
                    rec = T[n]
                    rec["B"].add(b)
                    rec["dk"].add(tk)
                    if n in bo:
                        rec["citeBT"].add(b)
                    if reason_set & bo:
                        rec["reason"].add(b)
                    if ocap & TT.toks(b):
                        rec["capB"].add(b)
                    if int(F.date[n]) == last:
                        rec["latest"] = True
        if not T:
            continue
        recs = {}
        for n, rec in T.items():
            recs[n] = {"B": sorted(rec["B"]), "citeBT": sorted(rec["citeBT"]), "reason": sorted(rec["reason"]),
                       "capB": sorted(rec["capB"]), "dk": sorted(rec["dk"]), "latest": rec.get("latest", False),
                       "capT": bool(ocap & TT.toks(n)), "days": oo - M.ordinal(int(F.date[n])),
                       "date": int(F.date[n]), "court": int(F.court[n])}
        out[o["n"]] = {"kind": o["kind"], "part": o["part"], "date": od, "n_reason": len(reason_set), "T": recs}
        st["orders_with_T"] += 1
        st["kind_" + o["kind"]] += 1
    pickle.dump(out, open(os.path.join(WORK, "cand.pkl"), "wb"), protocol=4)
    print(dict(st))


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    {"cand": stage_cand}[sys.argv[1]]()
