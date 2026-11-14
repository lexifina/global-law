# fjc8 copy of round7 b4sc gfeat7.py/guard7.py (round-6 guard, unchanged; same relative paths)
# b4sc copy of round6/history/rules/guard/gfeat.py (paths only)
"""Round 6 guard, stage 1: features of every base history row of a status-changing kind (and affirmed).

    python -X utf8 round6/history/rules/guard/gfeat.py [--procs 6]

Reads the base table (round5/stage/final/history.tsv = data/history.tsv; read only), the acting decision's text from
git, graph/cite_index.tsv, graph/nodes.tsv (names), node dates and courts2 ids. Reads NO Shepardized file, no gold
file, no reports.tsv, no split file. Writes work/features.jsonl.gz (one JSON object per base row):

  id, T, D, kind, scope, mode, ev, dD, dT, cD, cT, q:[q0,q1], titleD, nameT, hw,
  dopen:   the first 700 characters of the first opinion part of D (bench / rehearing wording)
  dhead:   the first 1200 characters of D's head matter / title zone
  dsent:   [s0, text] the sentence of D that ends the row's quote; dlead: the 300 characters before it
  ntocc, tocc: [{c:[c0,c1], key, part, s:[s0,s1], w:[w0,text]}]   citations of T in D (window = sentence -300/+200)
  cand:    [{j, key, n, c, part, s, w, court, date, name, shT, shD, nT, nJ, own, rel}]  other decisions D cites in
           the same litigation (a shared party-name token with T's name or D's title, or one of D's party tokens in
           the 250 characters before the citation), dated from T's date to D's date
           rel: same (court of T) | peer (same system and rank as T) | mid (rank between T and D) |
                dsame (D's own court) | hi (above D or other)
Offsets are characters of the git-HEAD text (UTF-8, CRLF -> LF); stored texts have tab/newline -> space.
"""
import argparse, collections, gzip, json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
R6 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "round6", "history")
sys.path.insert(0, R6)
import r6lib as L  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work", "guard")
BASE = os.path.join(L.C2, "round5", "stage", "final", "history.tsv")
KINDS = ("reversed", "vacated", "withdrawn", "substitutedBy", "rehearingEnBancGranted", "affirmed")
BAD_PARTS = ("dissent", "concurrence", "dissent~", "concurrence~", "front")
G = {}


def base_rows():
    out = []
    with open(G.get("base", BASE), encoding="utf-8", newline=NL) as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) >= 13 and p[4] in KINDS:
                out.append(p)
    return out


def init():
    C = L.reader_common()
    G["C"] = C
    idx = {}
    with open(os.path.join(L.W, "graph", "cite_index.tsv"), encoding="utf-8") as f:
        for line in f:
            k, v = line.rstrip(NL).split("\t")
            idx[k] = int(v)
    G["idx"] = idx
    G["F"] = L.Facts()
    G["names"] = {}
    G["nf"] = open(L.NODES, "rb")
    G["off"] = L._offsets()


def node_name(n):
    nm = G["names"].get(n)
    if nm is None:
        f = G["nf"]
        f.seek(int(G["off"][n]))
        p = f.readline().decode("utf-8").rstrip("\r\n").split("\t")
        nm = p[6] if len(p) > 6 else ""
        if len(G["names"]) > 500000:
            G["names"].clear()
        G["names"][n] = nm
    return nm


def toks_of(name):
    C = G["C"]
    return C.name_tokens(name) | C.short_name_tokens(name)


def window(view, body0, c0, c1):
    C = G["C"]
    s0, s1 = C.sentence_span(view, c0, c1)
    w0, w1 = max(body0, s0 - 300), min(len(view), s1 + 200)
    return [s0, s1], [w0, L.norm(view[w0:w1])]


def analyze(D, rows, text):
    C, F, idx = G["C"], G["F"], G["idx"]
    n_text = len(text)
    body0 = 0
    fm = ""
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            fm = text[:e]
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else n_text
    mt = re.search(r"^# (.+)$", text[body0:body0 + 3000], re.M)
    title = mt.group(1).strip() if mt else ""
    hw = C.hard_wrapped(text, body0)
    view = C.unwrap_view(text, body0) if hw else text
    pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    toksD = toks_of(title)
    tok_rx = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in sorted(toksD)) + r")\b") if toksD else None
    dD = int(F.date[D])
    cD = int(F.court[D])
    rD = F.rank(cD)
    sD = F.system(cD)
    # every resolved citation outside separate opinions
    cites = collections.defaultdict(list)
    for m in C.CITE_RX.finditer(view, body0):
        key = C.cite_key(m)
        if not key:
            continue
        j = idx.get(key)
        if j is None or j == D:
            continue
        part, _sec = C.part_at(pm, m.start())
        if part in BAD_PARTS:
            continue
        cites[j].append((m.start(), m.end(), key, part))
    ops = [(a, b, p) for a, b, p, s_ in pm if p in ("majority", "perCuriam", "plurality", "majority~", "unknown")]
    dopen = L.norm(view[ops[0][0]:min(n_text, ops[0][0] + 700)]) if ops else ""
    heads = [(a, b) for a, b, p, s_ in pm if p in ("headmatter", "title")]
    h0 = min((a for a, b in heads), default=body0)
    h1 = max((b for a, b in heads), default=body0)
    dhead = L.norm(view[h0:min(h1, h0 + 1200)])
    out = []
    for p in rows:
        rid, T, kind, scope = p[0], int(p[1]), p[4], p[5]
        q0, q1 = int(p[7]), int(p[8])
        dT = int(F.date[T])
        cT = int(F.court[T])
        rT = F.rank(cT)
        sT = F.system(cT)
        nameT = node_name(T)
        toksT = toks_of(nameT)
        r = {"id": rid, "T": T, "D": D, "kind": kind, "scope": scope, "mode": p[12].split(":")[1] if ":" in p[12] else "",
             "ev": p[10], "dD": dD, "dT": dT, "cD": cD, "cT": cT, "q": [q0, q1], "titleD": title[:200],
             "nameT": nameT[:200], "hw": int(hw), "dopen": dopen, "dhead": dhead}
        e1 = max(q0 + 1, min(q1, n_text))
        s0, s1 = C.sentence_span(view, max(q0, e1 - 2), e1)
        s0 = max(s0, q0) if q1 - q0 < 600 else s0
        r["dsent"] = [s0, L.norm(view[s0:min(s1, s0 + 900)])]
        r["dlead"] = L.norm(view[max(body0, s0 - 300):s0])
        occ = cites.get(T, [])
        r["ntocc"] = len(occ)
        r["tocc"] = []
        for c0, c1, key, part in occ[:6]:
            s, w = window(view, body0, c0, c1)
            r["tocc"].append({"c": [c0, c1], "key": key, "part": part, "s": s, "w": w})
        cand = []
        for j, oc in cites.items():
            if j == T:
                continue
            dj = int(F.date[j])
            if not dj or dj > dD or dj < dT:
                continue
            cj = int(F.court[j])
            rj = F.rank(cj)
            sj = F.system(cj)
            if cj == cT:
                rel = "same"
            elif cj == cD:
                rel = "dsame"
            elif sj == sT and rj == rT:
                rel = "peer"
            elif rT < rj < rD and (sj == sT or sj == sD):
                rel = "mid"
            else:
                rel = "hi"
            nm = node_name(j)
            tj = toks_of(nm)
            shT = len(tj & toksT)
            shD = len(tj & toksD)
            own = 0
            if tok_rx:
                for c0, c1, key, part in oc:
                    if tok_rx.search(view, max(body0, c0 - 250), c0):
                        own = 1
                        break
            if not (shT or shD or own):
                continue
            c0, c1, key, part = oc[0]
            s, w = window(view, body0, c0, c1)
            rec = {"j": j, "key": key, "n": len(oc), "c": [c0, c1], "part": part, "s": s, "w": w, "court": cj,
                   "date": dj, "name": nm[:160], "shT": shT, "shD": shD, "nT": len(toksT), "nJ": len(tj),
                   "nD": len(toksD), "own": own, "rel": rel}
            if len(oc) > 1:
                c0, c1, key, part = oc[-1]
                s, w = window(view, body0, c0, c1)
                rec["last"] = {"c": [c0, c1], "part": part, "s": s, "w": w}
            cand.append(rec)
        cand.sort(key=lambda x: (-(x["shT"] + x["shD"]), x["c"][0]))
        r["cand"] = cand[:12]
        r["ncand"] = len(cand)
        out.append(r)
    return out


def run_chunk(task):
    k, items, tag = task  # items: [(D, [rows])]
    if "idx" not in G:
        init()
    outp = os.path.join(WORK, "%sfeat.%03d.jsonl.gz" % (tag, k))
    if os.path.exists(outp):
        return k, -1, 0
    texts = L.fetch_texts([d for d, _ in items])
    n = miss = 0
    with gzip.open(outp + ".part", "wt", encoding="utf-8", newline=NL, compresslevel=4) as f:
        for D, rows in items:
            if D not in texts:
                miss += len(rows)
                continue
            sha, text = texts[D]
            if sha != rows[0][6]:
                miss += len(rows)
                continue
            try:
                recs = analyze(D, rows, text)
            except Exception as ex:  # count and go on
                sys.stderr.write("D %d: %r\n" % (D, ex))
                miss += len(rows)
                continue
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + NL)
                n += 1
    os.replace(outp + ".part", outp)
    return k, n, miss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--base", help="another history table with the same columns (default: the round-5 base)")
    ap.add_argument("--tag", default="", help="prefix of the work files, e.g. v1_")
    a = ap.parse_args()
    if a.base:
        G["base"] = a.base
    os.makedirs(WORK, exist_ok=True)
    rows = base_rows()
    by_d = collections.defaultdict(list)
    for p in rows:
        by_d[int(p[2])].append(p)
    ds = sorted(by_d)
    # chunk by repo so that each chunk needs few git processes
    off = L._offsets()
    repo_of = {}
    with open(L.NODES, "rb") as f:
        for d in ds:
            f.seek(int(off[d]))
            repo_of[d] = f.readline().decode("utf-8").split("\t")[1]
    ds.sort(key=lambda d: (repo_of[d], d))
    size = 700
    tasks = [(k, [(d, by_d[d]) for d in ds[i:i + size]], a.tag) for k, i in enumerate(range(0, len(ds), size))]
    print("rows", len(rows), "acting decisions", len(ds), "chunks", len(tasks), flush=True)
    t0 = time.time()
    tot = miss = 0
    import multiprocessing as mp
    with mp.Pool(a.procs) as pool:
        for k, n, m in pool.imap_unordered(run_chunk, tasks, chunksize=1):
            tot += max(n, 0)
            miss += m
            if k % 10 == 0:
                print("chunk", k, n, m, round(time.time() - t0), flush=True)
    # merge
    outp = os.path.join(WORK, a.tag + "features.jsonl.gz")
    n = 0
    with gzip.open(outp + ".part", "wt", encoding="utf-8", newline=NL, compresslevel=4) as fo:
        for k in range(len(tasks)):
            with gzip.open(os.path.join(WORK, "%sfeat.%03d.jsonl.gz" % (a.tag, k)), "rt", encoding="utf-8") as fi:
                for line in fi:
                    fo.write(line)
                    n += 1
    os.replace(outp + ".part", outp)
    print("features", n, "of", len(rows), "missing (text / sha / error)", miss, round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
