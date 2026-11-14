"""Round 8 `orderdock`: bridge lines (DESIGN8 section 4, D8-3) for the admitted bridge rows.

    python -X utf8 round8/agents/orderdock/certify_bridge8.py [--cert DIR] [--out DIR]
        default --cert round8/agents/orderdock/cert_bridge   (certify8 output: the admitted h8 ids)
        default --out  round8/agents/orderdock/cert_bridge_lines

For every admitted history row of `cert_bridge` (id h8:<O>:<X>:<kind>) the bridge texts W that dres.py recorded for
the order O (work/bridge_links.tsv, work/hist/*.jsonl) are tried in order; the first W whose quote passes the
section-4 conditions 1-6 (pre-checked here in Python) gives the row's line. The quote runs from the start of X's
citation to the end of the first Supreme Court citation after the history cue.

Output folder (stage8 takes it as a delta folder):
  history_bridge_delta.tsv   id, w_node, b_start, b_end, b_quote, src            (6 columns, LF, no header)
  cert_text_delta.tsv        W's window [b_start-400, b_end+400) (sha, start, end, text), as certify8 does for quotes
  window_sha_delta.tsv       sha, start, end, sha1(window text), "corpus"
  cite_index_delta.tsv       key -> node lines for X's and O's citations not already in the base index (each checked
                             as certify8 checks evidence citations: graph index U base index give exactly that node)
  rejects.tsv                id, reason of the LAST W tried (bridgeMismatch / bridgeDate / bridgeClause /
                             bridgeTarget / bridgeCue / bridgeActor / textMissing / shaMismatch / noBridgeText), detail
  stats.json                 counts per reason (first failing condition of every W tried, and per row)
Condition 7 (the row's own check, selfText) is certify8's: only admitted ids are given lines.
No answer-key file is read.
"""
import argparse
import collections
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round8"))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import certify6 as C6  # noqa: E402

L = C6.L
r6cite = C6.r6cite
RC = L.reader_common()
NL, TAB = "\n", "\t"
norm, lower, compact = C6.norm, C6.lower, C6.compact
PAD = 400
BASE = os.path.join(C2, "round7", "stage", "v3")
WORK = os.path.join(HERE, "work")

# DESIGN8 section 4 lists; the cue table's `bridge_cue` / `bridge_max_len` win when lean8 has added them
BRIDGE_CUE = {"certDenied": ["cert. denied", "certiorari denied", "cert denied"],
              "vacated": ["vacated", "judgment vacated", "vacated and remanded"],
              "reversed": ["rev'd", "reversed"],
              "affirmed": ["aff'd", "affirmed"],
              "reviewDismissed": ["cert. dismissed", "certiorari dismissed", "appeal dismissed"]}
BRIDGE_MAX = 600


def load_cues():
    src = "DESIGN8 section 4"
    cues, mx = BRIDGE_CUE, BRIDGE_MAX
    try:
        t = json.load(open(C6.CUE_JSON, encoding="utf-8"))
        if isinstance(t.get("bridge_cue"), dict):
            cues, src = t["bridge_cue"], "cue_table.json"
        if isinstance(t.get("bridge_max_len"), int):
            mx = t["bridge_max_len"]
    except (OSError, ValueError):
        pass
    return cues, mx, src


def cmap(s):
    """compact(s) and, for each compact character, its index in s."""
    out, pos = [], []
    for i, ch in enumerate(s):
        c = compact(ch)
        if c:
            out.append(c)
            pos.append(i)
    return "".join(out), pos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cert", default=os.path.join(HERE, "cert_bridge"))
    ap.add_argument("--out", default=os.path.join(HERE, "cert_bridge_lines"))
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--other-delta", action="append", default=[
        os.path.join(HERE, "cert_bridge"), os.path.join(HERE, "cert_lists_v2"), os.path.join(HERE, "cert_remandcap")],
        help="delta folders staged with the lines (their cite_index_delta lines are part of the staged index)")
    ap.add_argument("--own-page", action="store_true",
                    help="condition 6 also passes when the first citation after the cue is one of O's own citations "
                         "(a reporter page shared by several orders) and the base index maps it to no other node; "
                         "the line key -> O is then added to cite_index_delta (needs the lead's decision)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cues, max_len, cue_src = load_cues()
    st = collections.Counter()
    # admitted rows
    rows = []
    for p in C6.read_tsv(os.path.join(a.cert, "history_delta.tsv")):
        rows.append((p[0], int(p[2]), int(p[1]), p[4], int(p[3])))   # id, O, X, kind, date(O)
    # bridge texts per order
    links = {}
    with open(os.path.join(WORK, "bridge_links.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            q = line.rstrip(NL).split(TAB)
            ws = []
            for b in q[3].split(";"):
                w, rest = b.split("@", 1)
                ws.append((int(w), int(rest.split(":", 1)[0])))
            links[int(q[0])] = (int(q[1]), ws)
    need = {(w, p) for _id, o, _x, _k, _d in rows if o in links for w, p in links[o][1]}
    recs = {}
    for path in glob.glob(os.path.join(WORK, "hist", "*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if (r["n"], r["p"][0]) in need:
                    recs[(r["n"], r["p"][0])] = r
    wnodes = {w for w, _p in need}
    onodes = {o for _id, o, _x, _k, _d in rows}
    dec = C6_read_decisions(os.path.join(a.base, "decisions2.tsv"), wnodes | onodes)
    texts = L.fetch_texts(sorted(w for w in wnodes if w in dec))
    # candidate citation keys (X's citations and the Supreme Court references) -> compact keys to look up
    ckeys = set()
    for r in recs.values():
        for k, ca, cb in r["cites"]:
            for kk in r6cite.keys(r["snip"][ca - r["s0"]:cb - r["s0"]] or k):
                ckeys.add(compact(kk))
        for typ, k, _ra, _rb in r["refs"]:
            if typ == "c":
                ckeys.add(compact(k))
    hits = C6.graph_hits(ckeys)
    base_idx = collections.defaultdict(set)
    for p in C6.read_tsv(os.path.join(a.base, "cite_index.tsv")):
        if len(p) >= 2:
            base_idx[compact(p[0])].add(int(p[1]))

    def index_nodes(c):
        return {n for _, n in hits.get(c, ())} | base_idx.get(c, set())

    own = {}
    if a.own_page:
        import pickle
        for od in pickle.load(open(os.path.join(C2, "round6", "history", "rules", "memo", "work", "orders.pkl"),
                                   "rb"))["orders"]:
            if od["n"] in onodes:
                own[od["n"]] = {compact(RC.norm_cite(c.strip()) or "") for c in (od["cites"] or "").split("|")} - {""}

    def actor_ok(c, o):
        nodes = index_nodes(c)
        if nodes == {o}:
            return "index"
        if a.own_page and c in own.get(o, ()) and not (base_idx.get(c, set()) - {o}):
            return "ownPage"
        return None

    lines, wins, cite_out, rejects, acc = [], {}, set(), [], []
    for rid, o, x, kind, dO in rows:
        if o not in links or links[o][0] != x:
            st["row:noBridgeText"] += 1
            rejects.append((rid, "noBridgeText", ""))
            continue
        last = None
        done = False
        for w, p0 in links[o][1]:
            r = recs.get((w, p0))
            why, detail, got = check_one(r, w, o, x, kind, dO, dec, texts, cues, max_len, index_nodes, actor_ok)
            st["try:" + (why or "ok:" + detail)] += 1
            if why is None:
                b0, b1, quote, xkey, okey, between = got
                t = texts[w][1]
                s0, e0 = max(0, b0 - PAD), min(len(t), b1 + PAD)
                acc.append((rid, w, b0, b1, quote, xkey, x, okey, o, (dec[w][2], s0, e0), norm(t[s0:e0]), detail,
                            between))
                done = True
                break
            last = (why, detail)
        if not done:
            st["row:" + last[0]] += 1
            rejects.append((rid, last[0], last[1]))
    # the staged cite index is one node per key: a key that two accepted lines (or a line and the base index) would
    # map to different nodes (a reporter page shared by several orders) is dropped with every line that needs it
    # Exact section-4 simulation on the staged index (base cite_index + the other orderdock deltas + this delta's
    # proposed lines), iterated until no line fails (dropping a line drops its proposed keys).
    staged = collections.defaultdict(set)
    for c, ns in base_idx.items():
        staged[c] |= ns
    for d in a.other_delta:
        for p in C6.read_tsv(os.path.join(d, "cite_index_delta.tsv")):
            if len(p) >= 2:
                staged[compact(p[0])].add(int(p[1]))
    # writer-side 5b (stricter than the staged index): no citation that the graph or base index resolves (to any
    # node, X's own parallel citations included) may start between X's citation and the cue
    live = []
    for e in acc:
        chain = [k for k in e[12] if index_nodes(compact(k))]
        if chain:
            st["row:bridgeChain"] += 1
            rejects.append((e[0], "bridgeChain", "citation between X and the cue: %s" % ", ".join(chain)))
        else:
            live.append(e)
    while True:
        prop = collections.defaultdict(set)
        for e in live:
            for key, node in ((e[5], e[6]), (e[7], e[8])):
                prop[compact(key)].add(node)
        idx = collections.defaultdict(set)
        for c, ns in staged.items():
            idx[c] |= ns
        for c, ns in prop.items():
            idx[c] |= ns
        klens = sorted({len(c) for c in idx if c}, reverse=True)
        keep, drop = [], []
        for e in live:
            why = simulate(e, idx, klens, cues, max_len)
            (keep if why is None else drop).append((e, why))
        if not drop:
            break
        for e, why in drop:
            st["row:" + why[0]] += 1
            rejects.append((e[0], why[0], why[1]))
        live = [e for e, _ in keep]
    for e in live:
        rid, w, b0, b1, quote, xkey, x, okey, o, wk_, wt, detail, between = e
        lines.append((rid, w, b0, b1, quote, "r8:orderdock:bridge"))
        wins[wk_] = wt
        for key, node in ((xkey, x), (okey, o)):
            if node not in staged.get(compact(key), set()):
                cite_out.add((key, node))
        st["row:ok:" + detail] += 1

    def write(name, items):
        p = os.path.join(a.out, name)
        with open(p, "w", encoding="utf-8", newline=NL) as f:
            for it in items:
                f.write(TAB.join(map(str, it)) + NL)
        return hashlib.sha1(open(p, "rb").read()).hexdigest()

    sha = {}
    sha["history_bridge_delta.tsv"] = write("history_bridge_delta.tsv", lines)
    wk = sorted(wins)
    sha["cert_text_delta.tsv"] = write("cert_text_delta.tsv", ((s, s0, e0, wins[(s, s0, e0)]) for s, s0, e0 in wk))
    sha["window_sha_delta.tsv"] = write("window_sha_delta.tsv", (
        (s, s0, e0, hashlib.sha1(wins[(s, s0, e0)].encode("utf-8")).hexdigest(), "corpus") for s, s0, e0 in wk))
    sha["cite_index_delta.tsv"] = write("cite_index_delta.tsv", sorted(cite_out))
    write("rejects.tsv", ((i, w, d.replace(TAB, " ")) for i, w, d in rejects))
    stats = {"rows": len(rows), "lines": len(lines), "windows": len(wins), "cite_index_lines": len(cite_out),
             "counts": dict(sorted(st.items())), "cue_source": cue_src, "bridge_max_len": max_len, "sha1": sha}
    json.dump(stats, open(os.path.join(a.out, "stats.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in stats.items() if k != "sha1"}, indent=1))


def key_at(cq, i, idx, klens):
    """The longest index key starting at compact position i, or None."""
    for L_ in klens:
        if i + L_ <= len(cq) and cq[i:i + L_] in idx:
            return cq[i:i + L_]
    return None


def simulate(e, idx, klens, cues, max_len):
    """DESIGN8 section 4 steps 1-6 (with 5b) on the staged index; None or (reason, detail).
    Positions: p1 / key ends are compact positions mapped back to quote characters; p2 is a quote position."""
    rid, w, b0, b1, quote, xkey, x, okey, o, wk_, wt, detail, between = e
    if not quote or b1 - b0 > max_len:
        return ("bridgeMismatch", "length")
    if ";" in quote:
        return ("bridgeClause", "")
    cq, cpos = cmap(quote)
    p1 = None
    for i in range(len(cq)):
        k = key_at(cq, i, idx, klens)
        if k is not None and idx[k] == {x}:
            p1, k1 = i, k
            break
    if p1 is None:
        return ("bridgeTarget", "no index key mapping to X alone in the compact quote")
    q1 = cpos[p1]
    ql = lower(quote)
    p2 = -1
    for c in cues.get(kind_of(rid), ()):
        j = ql.find(c, q1 + 1)
        if j > q1 and (p2 < 0 or j < p2):
            p2 = j
    if p2 < 0:
        return ("bridgeCue", "")
    # 5b: no index key starts after the end of X's key and before the cue
    x_end = p1 + len(k1)
    for i in range(x_end, len(cq)):
        if cpos[i] >= p2:
            break
        k = key_at(cq, i, idx, klens)
        if k is not None:
            return ("bridgeChain", "index key %s between X and the cue" % k)
    # 6: the first index key after the cue (longest at its position) maps to O alone
    for i in range(len(cq)):
        if cpos[i] < p2:
            continue
        k = key_at(cq, i, idx, klens)
        if k is not None:
            if idx[k] == {o}:
                return None
            return ("bridgeActor", "first index key after the cue %s -> %s" % (k, sorted(idx[k])))
    return ("bridgeActor", "no index key after the cue")


def kind_of(rid):
    return rid.rsplit(":", 1)[1]


def C6_read_decisions(path, want):
    """{node: (court2, date, text_sha)} (as certify8.read_decisions)."""
    out = {}
    with open(path, "rb") as f:
        for line in f:
            i = line.find(b"\t")
            try:
                k = int(line[:i])
            except ValueError:
                continue
            if k in want:
                p = line.rstrip(b"\n").decode("utf-8").split(TAB)
                if len(p) > 7:
                    out[k] = (int(p[1]), int(p[2]), p[7])
    return out


def check_one(r, w, o, x, kind, dO, dec, texts, cues, max_len, index_nodes, actor_ok):
    """Section-4 conditions 1-6 for one bridge text; (None, '', (b0, b1, quote, xkey, okey)) or (reason, detail)."""
    if r is None or w not in dec:
        return "noBridgeText", "record or decision missing", None
    if w not in texts:
        return "textMissing", str(w), None
    sha, t = texts[w]
    if sha != dec[w][2]:
        return "shaMismatch", "git %s, decisions2 %s" % (sha, dec[w][2]), None
    # X's citation in the clause (the last group before the phrase), O's first page reference after the phrase
    xc = None
    for k, ca, cb in r["cites"]:
        raw = t[ca:cb]
        for kk in r6cite.keys(raw) or [k]:
            if index_nodes(compact(kk)) == {x} and not (index_nodes(compact(k)) - {x}):
                # the line written to the index is the PRINTED key (its compact form is what the quote holds)
                xc = (k, ca, cb, k)
                break
    if xc is None:
        return "bridgeTarget", "no citation of the clause maps to X alone in the index", None
    _k, b0, _xb, xkey = xc
    oref = None
    for typ, k, ra, rb in r["refs"]:
        if typ == "c" and ra > r["p"][0]:
            oref = (k, ra, rb)
            break
    if oref is None:
        return "bridgeActor", "no citation after the cue", None
    b1 = oref[2]
    quote = norm(t[b0:b1])
    # 1. bridgeMismatch
    if not quote or b0 >= b1 or b1 - b0 > max_len:
        return "bridgeMismatch", "length %d" % (b1 - b0), None
    # 2. bridgeDate
    dW = dec[w][1]
    if not dW or not dO or dW < dO:
        return "bridgeDate", "W %s O %s" % (dW, dO), None
    # 3. bridgeClause
    if ";" in quote:
        return "bridgeClause", "", None
    # 4. bridgeTarget: the first compact citation that the index maps to X (X's key as printed, or its alias line)
    cq, cpos = cmap(quote)
    cx = compact(t[b0:xc[2]])
    p1c = cq.find(cx)
    if p1c < 0:
        return "bridgeTarget", "X citation not resolved in the quote", None
    p1 = cpos[p1c]
    # 5. bridgeCue after p1
    ql = lower(quote)
    p2 = -1
    for c in cues.get(kind, ()):
        i = ql.find(c, p1 + 1)
        if i > p1 and (p2 < 0 or i < p2):
            p2 = i
    if p2 < 0:
        return "bridgeCue", "no %s cue after X's citation" % kind, None
    # 6. bridgeActor: after p2, the first citation of the quote maps to O
    first = None
    for cm in RC.CITE_RX.finditer(quote, p2):
        kk = RC.cite_key(cm)
        if kk:
            first = kk
            break
    if first is None:
        return "bridgeActor", "no citation after the cue", None
    how = actor_ok(compact(first), o)
    nodes = index_nodes(compact(first))
    if how is None:
        return "bridgeActor", "first citation after the cue %s maps to %s" % (first, ",".join(map(str, sorted(nodes)))
                                                                             or "nothing"), None
    # 5b. bridgeChain: no citation starts between the end of X's citation and the cue (keys checked in main()
    #     against the staged index: base cite_index + this delta; and against the graph index for another node)
    between = []
    for cm in RC.CITE_RX.finditer(quote, _xb - b0, p2):
        kk = RC.cite_key(cm)
        if kk:
            between.append(kk)
    return None, how, (b0, b1, quote, xkey, first, between)


if __name__ == "__main__":
    main()
