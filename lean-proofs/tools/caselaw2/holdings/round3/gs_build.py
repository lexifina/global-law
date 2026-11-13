"""Round 3: read the courts-of-appeals decisions on the US Code SECTIONS of the gold splits that the split reader
never read (classes A1/A2 of round2/splits_misses.tsv). Gold gives only the list of sections.

    python gs_build.py [TOTAL=840] [CAND=80] [PER=20]

1. sections = usc section of every A1/A2 row, ranked by number of gold rows.
2. citers  = courts-of-appeals decisions citing the section (usc/results/rows_out.tsv, 1995 on). At most CAND per
   section are fetched (seeded sample) -- the cap.
3. windows = as splits_windows.py but at section level (mention +-4 sentences, <= 30 sentences), with its cue scores.
4. chosen  = per section, windows with conflict language first, then by score, round-robin across circuits; quota
   6 + 2*(gold rows - 1), max 12, until TOTAL.
writes work/round3/splits/w: sections.tsv, windows.json {wid: {...}}, batch_XX.md (PER windows each)
"""
import collections, json, math, os, random, re, sys
HT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HT)
import core, text, splits_select, splits_windows as SW

C2 = os.path.join(text.WORK, "caselaw-lean-2")
OUT = os.path.join(C2, "work", "round3", "splits", "w")
CIRC = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth", 6: "Sixth", 7: "Seventh", 8: "Eighth", 9: "Ninth",
        10: "Tenth", 11: "Eleventh", 12: "D.C.", 13: "Federal"}
_K = None


def sect(u):
    return re.sub(r"\(.*$", "", u)


def gold_sections():
    cnt = collections.Counter()
    for l in open(os.path.join(C2, "round2", "splits_misses.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        if f[0] == "missed" and f[6][:2] in ("A1", "A2") and f[4] not in ("-", ""):
            cnt[sect(f[4])] += 1
    return cnt


def keys():
    global _K
    if _K is None:
        _K = json.load(open(os.path.join(OUT, "citers.json"), encoding="utf-8"))
    return _K


def pats(key):
    t, s = key.split(":", 1)
    S = re.escape(s)
    full = re.compile(r"\b" + t + r"\s*U\.?\s?S\.?\s?C\.?[A-Z.]*\s*,?\s*(?:§§?|[Ss]ec(?:tion|s?\.)?)?\s*" + S + r"(?![\w-])")
    short = re.compile(r"(?:§§?|\b[Ss]ection|\b[Ss]ec\.)\s*" + S + r"(?![\w-])")
    return full, short


def work(nid, raw):
    t = text.norm_text(raw)
    parts, form = core.court_parts(t)
    unpub = 1 if SW.UNPUB.search(t[:6000]) else 0
    out = []
    for key, kind, d in keys().get(str(nid), []):
        full, short = pats(key)
        if not full.search(t):
            continue
        ms = []
        for b, e, part in parts:
            for p in (full, short):
                ms += [m.start() for m in p.finditer(t, b, e)]
        ms = sorted(set(ms))
        if not ms:
            continue
        sents = []
        for b, e, part in parts:
            sents += core.split_sentences(t, b, e)
        idx = set()
        j = 0
        for m in ms:
            while j < len(sents) and sents[j][1] < m:
                j += 1
            if j < len(sents):
                for x in range(max(0, j - 4), min(len(sents), j + 5)):
                    idx.add(x)
        win = [sents[i] for i in sorted(idx) if sents[i][1] - sents[i][0] < 1500]
        wt = " ".join(t[a:z] for a, z in win)
        cues = len(SW.INTERP.findall(wt))
        sc_ = len(SW.SPLITC.findall(wt))
        score = 2 * min(cues, 8) + math.log2(1 + len(ms)) + 3 * min(sc_, 3) - (4 if unpub else 0)
        if len(win) > 30:
            ranked = sorted(win, key=lambda s: -(bool(SW.INTERP.search(t[s[0]:s[1]])) + 2 * bool(SW.SPLITC.search(t[s[0]:s[1]]))
                                               + any(s[0] <= m < s[1] for m in ms) * 2))
            win = sorted(ranked[:30])
        out.append({"key": key, "nid": nid, "kind": kind, "date": d, "sha": text.text_sha(raw), "unpub": unpub,
                    "mentions": len(ms), "cues": cues, "splitcues": sc_, "score": round(score, 2), "sents": win,
                    "lines": [core.show(t, a, z, 600) for a, z in win]})
    return out or None


def main():
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 840
    cand = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    per = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    os.makedirs(OUT, exist_ok=True)
    gs = gold_sections()
    print("gold A1/A2 rows", sum(gs.values()), "sections", len(gs), flush=True)
    kind = splits_select.node_kind()
    cit = collections.defaultdict(dict)
    for l in open(os.path.join(text.WORK, "usc", "results", "rows_out.tsv"), encoding="utf-8"):
        f = l.split("\t", 4)
        k = kind.get(int(f[1]))
        if not k:
            continue
        m = re.match(r"(\d+) U\.S\.C\. § (\S+)$", f[3])
        if not m:
            continue
        key = m.group(1) + ":" + m.group(2)
        if key in gs:
            cit[key][int(f[1])] = (k, int(f[2].replace("-", "")))
    rnd = random.Random(3)
    by_nid = collections.defaultdict(list)
    ncit = {}
    for key in gs:
        ns = sorted(cit.get(key, {}))
        ncit[key] = len(ns)
        if len(ns) > cand:
            ns = rnd.sample(ns, cand)
        for n in ns:
            by_nid[str(n)].append((key, cit[key][n][0], cit[key][n][1]))
    json.dump(by_nid, open(os.path.join(OUT, "citers.json"), "w", encoding="utf-8"))
    print("decisions to fetch", len(by_nid), flush=True)
    wins = collections.defaultdict(list)
    for res in text.map_nodes(sorted(int(n) for n in by_nid), work, procs=6, chunk=3000):
        if isinstance(res, tuple):
            continue
        for r in res:
            if r["cues"] + r["splitcues"] > 0:
                wins[r["key"]].append(r)
    chosen = []
    srows = []
    left = total
    for key, g in sorted(gs.items(), key=lambda x: (-x[1], x[0])):
        rs = wins.get(key, [])
        quota = min(12, 5 + 2 * (g - 1), left)
        circ = collections.defaultdict(list)
        for r in sorted(rs, key=lambda r: (-(r["splitcues"] > 0), -r["score"])):
            circ[r["kind"]].append(r)
        pick = []
        while len(pick) < quota and any(circ.values()):
            for c in sorted(circ, key=lambda c: (-(circ[c][0]["splitcues"] > 0), -circ[c][0]["score"]) if circ[c] else (9, 9)):
                if circ[c] and len(pick) < quota:
                    pick.append(circ[c].pop(0))
        left -= len(pick)
        chosen += pick
        srows.append((key, g, ncit[key], min(ncit[key], cand), len(rs), len(pick)))
    with open(os.path.join(OUT, "sections.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("section\tgold_rows\tcoa_citers_1995on\tfetched\twindows_with_cues\tread\n")
        for r in srows:
            f.write("\t".join(str(x) for x in r) + "\n")
    rnd.shuffle(chosen)
    chosen.sort(key=lambda r: r["key"])  # keep a section's windows together, so one reader words its questions alike
    idx = {}
    blocks = []
    for i, r in enumerate(chosen):
        wid = "W%04d" % i
        idx[wid] = {k: r[k] for k in ("key", "nid", "kind", "date", "sha", "unpub", "score", "splitcues", "sents")}
        t, s = r["key"].split(":")
        blk = ["## Window %s" % wid, "Section: %s U.S.C. § %s" % (t, s),
               "Court: %s Circuit, decided %d" % (CIRC[r["kind"]], r["date"]), "Sentences:"]
        blk += ["[%d] %s" % (j, ln) for j, ln in enumerate(r["lines"])]
        blocks.append("\n".join(blk))
    json.dump(idx, open(os.path.join(OUT, "windows.json"), "w", encoding="utf-8"))
    nb = (len(blocks) + per - 1) // per
    for i in range(nb):
        with open(os.path.join(OUT, "batch_%02d.md" % i), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n\n".join(blocks[i * per:(i + 1) * per]) + "\n")
    cov = sum(g for k, g, _, _, _, n in srows if n > 0)
    print("windows", len(chosen), "batches", nb, "sections read", sum(1 for r in srows if r[5] > 0), "of", len(srows),
          "gold rows on read sections", cov, "of", sum(gs.values()))


if __name__ == "__main__":
    main()
