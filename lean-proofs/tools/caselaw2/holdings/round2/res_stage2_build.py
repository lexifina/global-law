"""Stage-2 deep-read batches: (split question, Supreme Court decision) pairs that passed the stage-1 screen (yes/maybe).
The Supreme Court text is read from git (court's own part only), cut into sentences with offsets as the holdings
pipeline does; the reader picks a sentence id. No gold.
 -> work/res2/batch_XX.md, work/res2/sents.json {pid: {issue, node, sha, form, S: {sid: [start, end, part]}}}"""
import os, re, json, collections, glob
import common as C
import text, core, syl

TAG = os.environ.get("RES_TAG", "")
PER = int(os.environ.get("RES_PER", "8"))
STOP = set("the a an of to in for and or is are be was were been does do did under that which this with by on as at it its from not any may can whether when we our court courts case cases have has had would should could must there their they them than then but also such see supra section".split())


def toks(s):
    return {w for w in re.findall(r"[a-z][a-z\-']{3,}", s.lower()) if w not in STOP}


def main():
    od = os.path.join(C.PRIV, "work", os.environ.get("RES_DIR", "res2" + TAG))
    os.makedirs(od, exist_ok=True)
    v = {}
    for fn in glob.glob(os.path.join(C.PRIV, "work", "res1" + TAG, "out_*.jsonl")):
        for l in open(fn, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                v[r["pid"]] = r["v"]
    pairs = [l.rstrip("\n").split("\t") for l in open(os.path.join(C.PRIV, "work", "res1" + TAG, "pairs.tsv"), encoding="utf-8")]
    pairs = [p for p in pairs if v.get(p[0]) in ("yes", "maybe")]
    only = os.environ.get("RES_ONLY")
    if only:
        pairs = [p for p in pairs if p[0] in only.split(",")]
    iss = C.load_issues()
    keys = {p[1] for p in pairs}
    scn = {int(p[2]) for p in pairs}
    H = C.load_holdings(pred=lambda f: f[2] in keys and f[4] in ("yes", "no"))
    meta = C.node_meta({int(f[1]) for f in H} | scn)
    cs = C.courts()
    names = C.node_names({int(f[1]) for f in H} | scn)
    side = collections.defaultdict(lambda: {"yes": [], "no": []})
    for f in H:
        n = int(f[1])
        if C.court_kind(cs.get(meta[n][0])) != "scotus":
            side[f[2]][f[4]].append((-float(f[13]), meta[n][1], names.get(n, ("?",))[0], cs[meta[n][0]][2], f[3], f[9]))
    form2 = {}
    with open(os.path.join(C.DATA, "decisions2.tsv"), encoding="utf-8") as fh:
        for l in fh:
            i = l.find("\t")
            if l[:i].isdigit() and int(l[:i]) in scn:
                form2[int(l[:i])] = l.split("\t", 7)[6]
    raw = text.fetch(scn)
    idx = {}
    blocks = []
    for pid, k, n in pairs:
        n = int(n)
        if n not in raw:
            continue
        t = text.norm_text(raw[n])
        parts, form = syl.court_parts2(t)
        sents = []
        for b, e, part in parts:
            for a, z in core.split_sentences(t, b, e):
                if z - a <= 1500:
                    sents.append((a, z, part))
        if not sents:
            continue
        q = iss[k]
        sec = C.sect(q[3]).split(":")[1]
        ys, ns = sorted(side[k]["yes"])[:2], sorted(side[k]["no"])[:2]
        ref = toks(q[4] + " " + " ".join(x[4] for x in ys + ns))
        st = [toks(t[a:z]) for a, z, _ in sents]
        df = collections.Counter(w for s in st for w in s)
        pick = set(range(min(10, len(sents)))) | set(range(max(0, len(sents) - 4), len(sents)))
        for c in core.candidates(t, parts, k=16, frame=3):
            j = next((i for i, s in enumerate(sents) if s[0] == c[1]), None)
            if j is not None:
                pick.add(j)
        sc = []
        for i, s in enumerate(st):
            if core.CITEISH(t[sents[i][0]:sents[i][1]]):
                continue
            val = sum(1.0 / (1 + df[w]) ** 0.5 for w in s & ref)
            if val > 0:
                sc.append((-val, i))
        for _, i in sorted(sc)[:16]:
            pick.add(i)
        extra = 0
        for i, (a, z, _) in enumerate(sents):
            if extra >= 6:
                break
            s = t[a:z]
            if i not in pick and re.search(r"(?<![\w.])" + re.escape(sec) + r"(?![\w])", s) and not core.CITEISH(s) \
                    and core.STRONG.search(s):
                pick.add(i)
                extra += 1
        nm = names.get(n, ("?", "", ""))
        blk = ["## Pair %s" % pid,
               "QUESTION (%s): %s" % (q[3].replace(":", " U.S.C. § ", 1), q[4]),
               "Courts of appeals answering YES:"]
        for x in ys:
            blk.append("- %s (Cir. %d, %d): %s  [court's sentence: \"%s\"]" % (x[2], x[3], x[1], x[4], x[5][:400]))
        blk.append("Courts of appeals answering NO:")
        for x in ns:
            blk.append("- %s (Cir. %d, %d): %s  [court's sentence: \"%s\"]" % (x[2], x[3], x[1], x[4], x[5][:400]))
        blk.append("SUPREME COURT DECISION: %s, %s (decided %d). Selected sentences of the opinion of the Court:" % (
            nm[0], nm[1].split("|")[0], meta[n][1]))
        for i in sorted(pick):
            a, z, part = sents[i]
            blk.append("S%d: %s" % (i, core.show(t, a, z, 600)))
        idx[pid] = {"issue": k, "node": n, "sha": text.text_sha(raw[n]), "form": form, "form2": form2.get(n, ""),
                    "date": meta[n][1], "S": {str(i): list(sents[i]) for i in pick}}
        blocks.append("\n".join(blk))
    json.dump(idx, open(os.path.join(od, "sents.json"), "w", encoding="utf-8"))
    nb = (len(blocks) + PER - 1) // PER
    sizes = []
    for i in range(nb):
        fn = os.path.join(od, "batch_%02d.md" % i)
        with open(fn, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n\n".join(blocks[i * PER:(i + 1) * PER]) + "\n")
        sizes.append(os.path.getsize(fn))
    print("pairs", len(blocks), "batches", nb, sizes)


if __name__ == "__main__":
    main()
