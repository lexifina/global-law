"""Round 7, agent `antecedent`: candidates from the scan (antescan.py) -> cands.jsonl.gz.

    python -X utf8 antecands.py

For every act sentence of scan/*.jsonl.gz, the earlier decisions it may act on:
  - by citation: a citation in the act sentence or in the 2000 characters before it (same part, no heading between)
    whose key resolves to one decision (the staged cite index round6/history/stage/final2/cite_index.tsv first, as the
    checker reads it; else graph/cite_index.tsv when it names exactly one node);
  - by name: a decision the opinion cites elsewhere (in an opinion-of-the-court part) whose caption words, as printed
    beside that citation, stand as whole words in the act sentence or before it.
A named decision is kept when date(X) <= date(W), X != W, and W's court could have power over X's: same court; the
Supreme Court over a federal court; else same system and a lower tier (an obvious no-power pair is dropped; Lean
decides authority). Its NAMING SENTENCE is the sentence that holds the citation / name; it is NEAR when it ends at
most 300 characters before the act sentence starts (DESIGN7 2.2 joinedGap), or IN-ACT when the name is in the act
sentence itself. A candidate needs >= 1 near or in-act decision.

Also counts, per candidate, whether an admitted explicit base row (round6/history/out/final2/certs.tsv ok /
okUnverifiedBy, explicit = 1, status-changing kind) already has the same (W, X): the recall / sanity check.
No answer key is read.
"""
import collections, glob, gzip, json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
W = os.path.dirname(C2)
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402
C = L.reader_common()
FINAL2 = os.path.join(C2, "round6", "history", "stage", "final2")
OUT6 = os.path.join(C2, "round6", "history", "out", "final2")
NL = chr(10)
GAP = 300
STATUS_KINDS = ("overruled", "disapproved", "abrogated", "recededFrom")


def alnum(s):
    return re.sub(r"[^0-9a-z]", "", s.lower())


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def records():
    for p in sorted(glob.glob(os.path.join(HERE, "scan", "*.jsonl.gz"))):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                yield json.loads(line)


def resolver(keys):
    live = {}
    with open(os.path.join(FINAL2, "cite_index.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) >= 2:
                live.setdefault(alnum(p[0]), set()).add(int(p[1]))
    graph = collections.defaultdict(set)
    kb = {k.encode("utf-8") for k in keys}
    with open(os.path.join(W, "graph", "cite_index.tsv"), "rb") as f:
        for raw in f:
            i = raw.find(b"\t")
            if raw[:i] in kb:
                graph[raw[:i].decode("utf-8")].add(int(raw[i + 1:].strip()))
    res = {}
    for k in keys:
        c = alnum(k)
        if c in live:
            v = live[c]
            res[k] = next(iter(v)) if len(v) == 1 else None
        else:
            v = graph.get(k, ())
            res[k] = next(iter(v)) if len(v) == 1 else None
    return res


def names_of(nodes):
    """{node: (name, cite)} from graph/nodes.tsv (one sorted pass with seeks)."""
    off = L._offsets()
    out = {}
    with open(L.NODES, "rb") as f:
        for n in sorted(nodes):
            f.seek(int(off[n]))
            p = f.readline().decode("utf-8", "replace").rstrip("\r\n").split("\t")
            out[n] = (p[6] if len(p) > 6 else "", p[5] if len(p) > 5 else "")
    return out


def base_pairs():
    ok = set()
    for line in open(os.path.join(OUT6, "certs.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if p[0] == "treatment" and p[2] in ("ok", "okUnverifiedBy"):
            ok.add(p[1])
    pairs = {}
    for line in open(os.path.join(FINAL2, "treatments.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if p[0] in ok and p[7] == "1" and p[4] in STATUS_KINDS:
            pairs.setdefault((int(p[1]), int(p[2])), []).append((p[0], p[4], int(p[9]), int(p[10])))
    return pairs


class Power:
    def __init__(self, F):
        self.F = F

    def ok(self, w, x):
        F = self.F
        if w == x or not F.date[x] or not F.date[w] or F.date[x] > F.date[w]:
            return False
        cw, cx = int(F.court[w]), int(F.court[x])
        if cw == cx:
            return True
        if F.is_scotus(cw):
            return F.system(cx) == 0
        return F.system(cw) == F.system(cx) and F.rank(cx) < F.rank(cw)


TOKEN_RX = re.compile(r"[A-Za-z][A-Za-z'\-]+")


def printed_tokens(name, prefix):
    """Caption words of `name` (reader name tokens, three-letter party names) that the opinion prints beside the
    citation (prefix: the 90 characters before it); if none is printed, the caption's own words."""
    toks = C.name_tokens(name) | C.short_name_tokens(name)
    pw = set(TOKEN_RX.findall(prefix or ""))
    pr = {t for t in toks if t in pw}
    return pr or toks


def main():
    F = L.Facts()
    P = Power(F)
    keys = set()
    nrec = 0
    for r in records():
        nrec += 1
        for k, _a, _b in r["cites"]:
            keys.add(k)
        for k, _p in r["ocites"]:
            keys.add(k)
    log("records", nrec, "keys", len(keys))
    res = resolver(keys)
    log("resolved", sum(1 for v in res.values() if v is not None))
    pairs = base_pairs()
    log("base admitted explicit status pairs", len(pairs))
    # nodes whose names we need: the acting decisions and every power-ok resolved cite
    need = set()
    for r in records():
        n = r["n"]
        need.add(n)
        for k, _p in r["ocites"]:
            x = res.get(k)
            if x is not None:
                need.add(x)
        for k, _a, _b in r["cites"]:
            x = res.get(k)
            if x is not None and P.ok(n, x):
                need.add(x)
    NM = names_of(need)
    log("names", len(NM))
    st = collections.Counter()
    out = gzip.open(os.path.join(HERE, "cands.jsonl.gz"), "wt", encoding="utf-8", newline=NL)
    for r in records():
        st["act_sentences"] += 1
        n = r["n"]
        s0, s1 = r["s"]
        w0, wt = r["w"]
        rel0 = s0 - w0
        own = C.name_tokens(NM.get(n, ("", ""))[0]) | C.short_name_tokens(NM.get(n, ("", ""))[0])
        tg = {}

        def add(x, how, ev, h0, h1):
            a, b = C.sentence_span(wt, h0 - w0, h1 - w0)
            if h0 >= s0:
                a, b, where = rel0, len(wt), "act"
            else:
                b = min(b, rel0)
                if rel0 - b > GAP:
                    where = "far"
                else:
                    where = "near"
            a += w0
            b += w0
            cur = tg.get(x)
            rank = {"act": 0, "near": 1, "far": 2}
            # keep the closest naming sentence; a citation beats a name in the same place
            if cur is None or rank[where] < rank[cur["where"]] or (rank[where] == rank[cur["where"]] and (
                    b > cur["span"][1] or (b == cur["span"][1] and how == "cite" and cur["how"] == "name"))):
                tg[x] = {"t": x, "how": how, "ev": ev, "span": [a, b], "where": where, "hit": [h0, h1],
                         "xpara": int(NL in wt[b - w0:rel0]) if where == "near" else 0}
        for k, c0, c1 in r["cites"]:
            x = res.get(k)
            if x is None:
                st["cite_unresolved"] += 1
                continue
            if not P.ok(n, x):
                st["cite_nopower"] += 1
                continue
            add(x, "cite", "cite:" + k, c0, c1)
        # names of decisions cited elsewhere in the opinion
        seen = {}
        for k, pre in r["ocites"]:
            x = res.get(k)
            if x is None or x in seen or x == n:
                continue
            seen[x] = [t for t in printed_tokens(NM.get(x, ("", ""))[0], pre) if t not in own]
        # a caption word shared by two decisions the opinion cites names neither
        tok_n = collections.Counter(t for toks in seen.values() for t in set(toks))
        for x, toks in seen.items():
            if not P.ok(n, x):
                continue
            toks = [t for t in toks if tok_n[t] == 1]
            if not toks:
                continue
            rx = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in sorted(toks)) + r")\b")
            hits = list(rx.finditer(wt, max(0, rel0 - 2000)))
            if not hits:
                continue
            hits = [h for h in hits if h.start() < len(wt)]
            h = hits[-1]
            got = sorted({m.group(0) for m in hits if m.start() >= h.start() - 200})
            add(x, "name", "name:" + " ".join(got[:2]), w0 + h.start(), w0 + h.end())
        near = [v for v in tg.values() if v["where"] in ("near", "act")]
        if not near:
            st["no_near_target"] += 1
            continue
        st["cands"] += 1
        for v in tg.values():
            nm, cite = NM.get(v["t"], ("", ""))
            v["name"], v["cite"], v["date"], v["court"] = nm, cite, int(F.date[v["t"]]), int(F.court[v["t"]])
            v["base"] = [b[0] for b in pairs.get((n, v["t"]), [])]
        anyb = any(v["base"] for v in near)
        st["cands_with_base_row"] += int(anyb)
        if any(v["where"] == "act" for v in near):
            st["cands_with_inact_target"] += 1
        if all(v["where"] == "act" for v in near):
            st["cands_inact_only"] += 1
        for f in r["flags"]:
            st["flag_" + f] += 1
        rec = {"id": "%d:%d" % (n, s0), "n": n, "s": [s0, s1], "act": r["act"], "part": r["part"], "flags": r["flags"],
               "hw": r["hw"], "w0": w0, "pstart": r["pstart"], "wt": wt[max(0, rel0 - 1500):], "wt0": w0 + max(0, rel0 - 1500),
               "by_name": NM.get(n, ("", ""))[0], "by_cite": NM.get(n, ("", ""))[1], "by_date": int(F.date[n]),
               "by_court": int(F.court[n]), "targets": sorted(tg.values(), key=lambda v: v["hit"][0])}
        out.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + NL)
    out.close()
    with open(os.path.join(HERE, "cands_stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(st), f, indent=1)
    log(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
