"""shadow9 (round 9, move 4): GVR order -> decision below through the court below's own remand decision, found by
docket (no citation edge needed), confirmed by what the remand decision's text says.

    python -X utf8 round9/agents/shadow9/remandtext.py index   -> work/tokidx.pkl  (court, caption token) -> nodes
    python -X utf8 round9/agents/shadow9/remandtext.py pairs   -> work/pairs.pkl   (O, T, B) candidates
    python -X utf8 round9/agents/shadow9/remandtext.py text    -> work/pairsig.pkl signals read from B's text

General rule (corpus-wide; no answer-key file is read):
  O = a Supreme Court order of the round-6 memo parse with kind vacated or reversed and a court below.
  T = a decision of a court O names, dated 1..1,095 days before O, whose title shares a party-name token with O's
      caption (memolib.toks).
  B = a decision of T's court sharing one of T's docket numbers (cache meta), dated 0..1,826 days after O.
  Signals (O, T, B):
    capB    B's title shares a party-name token with O's caption
    citeBO  B cites O (graph edge to a Supreme Court node carrying one of O's page citations)
    citeBT  B cites T (graph edge)
    cue     B's text says the Supreme Court vacated / remanded (a sentence holding "Supreme Court" and one of
            vacat- / remand- / "in light of" / "for further consideration" / GVR)
    reason  B's text names O's reason case ("in light of X": X's first party name followed by " v. "), or cites
            (graph) a Supreme Court decision O cites
    odocket B's text holds O's docket number
    odate   B's text holds O's date ("Month D, YYYY")
Inputs: graph/nodes.tsv, graph/edges.bin, round6 memo orders.pkl, round8 orderdock work/meta.pkl, corpus texts (git).
"""
import collections
import datetime
import os
import pickle
import re
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
KINDS = ("vacated", "reversed")
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def gvr_orders():
    courts = M.Courts()
    out = []
    for o in pickle.load(open(os.path.join(MEMO, "work", "orders.pkl"), "rb"))["orders"]:
        if o["kind"] not in KINDS:
            continue
        ids = set()
        for k in o["courts"]:
            if k is not None:
                ids.update(courts.group.get(k, ()))
        ocap = M.toks(" ".join(o["caps"]) or o["title"])
        if ids and ocap:
            out.append((o, ids, ocap))
    return out


def stage_index():
    gv = gvr_orders()
    want_tok = set()
    want_ct = set()
    for o, ids, ocap in gv:
        want_tok |= ocap
        want_ct |= ids
    node_dk = pickle.load(open(os.path.join(OD, "work", "meta.pkl"), "rb"))["node_dk"]
    F = L.Facts()
    idx = collections.defaultdict(list)
    with open(L.NODES, "rb") as f:
        for n, line in enumerate(f):
            if n not in node_dk:
                continue
            c = int(F.court[n])
            if c not in want_ct:
                continue
            p = line.decode("utf-8", "replace").rstrip("\r\n").split("\t")
            if len(p) < 7:
                continue
            for w in M.toks(p[6]) & want_tok:
                idx[(c, w)].append(n)
    pickle.dump(dict(idx), open(os.path.join(WORK, "tokidx.pkl"), "wb"), protocol=4)
    print("gvr orders", len(gv), "tokens", len(want_tok), "courts", len(want_ct), "keys", len(idx))


def stage_pairs():
    gv = gvr_orders()
    tokidx = pickle.load(open(os.path.join(WORK, "tokidx.pkl"), "rb"))
    meta = pickle.load(open(os.path.join(OD, "work", "meta.pkl"), "rb"))
    node_dk, idx = meta["node_dk"], meta["idx"]
    F = L.Facts()
    out = []
    st = collections.Counter()
    for o, ids, ocap in gv:
        od, oo = o["date"], M.ordinal(o["date"])
        Ts = set()
        for c in ids:
            for w in ocap:
                for n in tokidx.get((c, w), ()):
                    dn = int(F.date[n])
                    if dn < od and 0 < oo - M.ordinal(dn) <= 1095:
                        Ts.add(n)
        trip = []
        for t in Ts:
            ct = int(F.court[t])
            for tk in node_dk.get(t, ()):
                for b in idx.get((ct, tk), ()):
                    db = int(F.date[b])
                    if b != t and db >= od and M.ordinal(db) - oo <= 1826:
                        trip.append((t, b, tk))
        if trip:
            st["orders_with_pair"] += 1
            out.append((o["n"], trip))
        st["orders"] += 1
    pickle.dump(out, open(os.path.join(WORK, "pairs.pkl"), "wb"), protocol=4)
    print(dict(st), "triples", sum(len(t) for _, t in out), "B", len({b for _, t in out for _, b, _ in t}))


CUE_SC = re.compile(r"Supreme\s+Court", re.I)
CUE_ACT = re.compile(r"vacat|remand|in\s+light\s+of|further\s+consideration|\bGVR", re.I)
SENT = re.compile(r"(?<=[.;])\s+(?=[A-Z])")


def has_cue(text):
    for m in CUE_SC.finditer(text):
        a, b = max(0, m.start() - 300), min(len(text), m.end() + 300)
        w = text[a:b]
        # the sentence(s) around the mention
        if CUE_ACT.search(w) and re.search(r"(?:United\s+States\s+)?Supreme\s+Court\b", w):
            if "Supreme Court of" in w[m.start() - a:m.start() - a + 40] and "United States" not in \
                    w[m.start() - a:m.start() - a + 60]:
                continue   # "Supreme Court of <State>": a state high court
            return True
    return False


RX_LIGHT = re.compile(r"in\s+light\s+of\s+(?:the\s+)?([A-Z][^,;()]{2,120}?)\s+v\.\s", re.S)


def reason_name(T):
    m = RX_LIGHT.search(T or "")
    if not m:
        return None
    name = m.group(1).strip()
    name = re.sub(r"^(?:our|this Court's|the Court's) decisions? in\s+", "", name)
    return name.split()[-1] if name else None


def docket_rx(dk):
    dk = (dk or "").strip().strip(".;:")
    for ch in ("–", "—", "‑", "‐"):
        dk = dk.replace(ch, "-")
    m = re.match(r"(\d{2})-(\d{1,5})$", dk.split()[0] if dk else "")
    if not m:
        return None
    return re.compile(r"\b%s\s*[-–—‑]\s*%s\b" % (m.group(1), m.group(2)))


def date_strs(d):
    y, m, dd = d // 10000, d // 100 % 100, d % 100
    full = MONTHS[m - 1]
    ab = full[:3] + "." if len(full) > 4 else full
    return [r"%s\s+%d,\s+%d" % (full, dd, y), r"%s\s+%d,\s+%d" % (re.escape(ab), dd, y)]


def _sig(args):
    items = args
    texts = L.fetch_texts([b for b, _ in items])
    out = {}
    for b, olist in items:
        if b not in texts:
            continue
        tx = texts[b][1]
        cue = has_cue(tx)
        for o_n, rname, drx, dstr in olist:
            s = {"cue": cue, "reason_txt": False, "odocket": False, "odate": False}
            if rname and re.search(r"\b%s\s+v\.\s" % re.escape(rname), tx):
                s["reason_txt"] = True
            if drx and re.search(drx, tx):
                s["odocket"] = True
            if any(re.search(p, tx) for p in dstr):
                s["odate"] = True
            out[(o_n, b)] = s
    return out


def stage_text():
    orders = {o["n"]: o for o in pickle.load(open(os.path.join(MEMO, "work", "orders.pkl"), "rb"))["orders"]}
    pairs = pickle.load(open(os.path.join(WORK, "pairs.pkl"), "rb"))
    perB = collections.defaultdict(list)
    for o_n, trip in pairs:
        o = orders[o_n]
        rn = reason_name(o["T"])
        drx = docket_rx(o["docket"])
        ds = date_strs(o["date"])
        for b in sorted({b for _, b, _ in trip}):
            perB[b].append((o_n, rn, drx.pattern if drx else None, ds))
    items = sorted(perB.items())
    chunks = [items[i:i + 400] for i in range(0, len(items), 400)]
    res = {}
    for k, r in enumerate(L.pmap(_sig, chunks, procs=8)):
        res.update(r)
    pickle.dump(res, open(os.path.join(WORK, "pairsig.pkl"), "wb"), protocol=4)
    c = collections.Counter()
    for s in res.values():
        for k, v in s.items():
            c[k] += bool(v)
    print("B texts", len(perB), "pairs", len(res), dict(c))


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    if sys.argv[1] != "link":
        {"index": stage_index, "pairs": stage_pairs, "text": stage_text}[sys.argv[1]]()


def stage_link():
    """Per order: candidate T with the signals of its bridges B -> work/link.pkl."""
    orders = {o["n"]: o for o in pickle.load(open(os.path.join(MEMO, "work", "orders.pkl"), "rb"))["orders"]}
    pairs = pickle.load(open(os.path.join(WORK, "pairs.pkl"), "rb"))
    sig = pickle.load(open(os.path.join(WORK, "pairsig.pkl"), "rb"))
    F = L.Facts()
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
    allB = np.array(sorted({b for _, t in pairs for _, b, _ in t}), dtype=np.uint32)
    onodes = np.array(sorted({o for o, _ in pairs}), dtype=np.uint32)
    e = np.fromfile(os.path.join(L.W, "graph", "edges.bin"), dtype=np.uint32).reshape(-1, 2)
    b_out = collections.defaultdict(set)
    for s, d in e[np.isin(e[:, 0], allB)].tolist():
        b_out[s].add(d)
    o_out = collections.defaultdict(set)
    for s, d in e[np.isin(e[:, 0], onodes)].tolist():
        o_out[s].add(d)
    del e
    tok = {}
    off = L._offsets()
    fh = open(L.NODES, "rb")

    def ttoks(n):
        if n not in tok:
            fh.seek(int(off[n]))
            r = fh.readline().decode("utf-8").rstrip("\r\n").split("\t")
            tok[n] = M.toks(r[6]) if len(r) > 6 else frozenset()
        return tok[n]

    out = {}
    for o_n, trip in pairs:
        o = orders[o_n]
        ocap = M.toks(" ".join(o["caps"]) or o["title"])
        sib = set()
        for c in (o["cites"] or "").split("|"):
            k = C.norm_cite(c.strip())
            if k:
                sib |= page_nodes.get(k, set())
        reasons = {x for x in o_out.get(o_n, ()) if int(F.court[x]) == SC} - sib
        T = {}
        for t, b, tk in trip:
            s = sig.get((o_n, b))
            if s is None:
                continue
            bo = b_out.get(b, set())
            rec = T.setdefault(t, {"B": {}, "date": int(F.date[t]), "court": int(F.court[t]), "dk": set()})
            rec["dk"].add(tk)
            rec["B"][b] = {"cue": s["cue"], "citeBO": bool(sib & bo), "citeBT": t in bo,
                           "reason": s["reason_txt"] or bool(reasons & bo), "odocket": s["odocket"],
                           "odate": s["odate"], "capB": bool(ocap & ttoks(b)), "date": int(F.date[b])}
        out[o_n] = {"kind": o["kind"], "part": o["part"], "date": o["date"], "T": T}
    pickle.dump(out, open(os.path.join(WORK, "link.pkl"), "wb"), protocol=4)
    print("orders", len(out))


if __name__ == "__main__" and sys.argv[1] == "link":
    stage_link()
