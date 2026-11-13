"""Task 3: reading batches for cross-circuit disagreement pairs (no gold).
Candidates: work/xc_pairs.tsv (reader treatments where a court of appeals declines to follow / disapproves a decision of
another circuit). Cut: the disagreeing decision cites the US Code within +-3000 chars of the disagreement quote, the
quote is in the court's own part, by-date >= 1970.
For each pair a digest with numbered sentences: B<i> (the disagreeing decision: +-9 sentences round the quote and 6 cue
sentences) and T<i> (the earlier decision: 14 cue sentences, 2 framing sentences, and sentences naming a US Code section
that the B passage names).
 -> work/xc/batch_XX.md, work/xc/sents.json  {pid: {"B": {sid: [start, end, part]}, "T": {...}, meta}}"""
import os, re, json, collections, sys
import common as C
import text, core

USC = re.compile(r"(\d{1,2})\s+U\.\s?S\.\s?C\.(?:\s?A\.)?\s*(?:§+|[Ss]ec(?:tion|\.)?s?)\s*(\d+[a-z]{0,2}(?:-\d+)?)((?:\([A-Za-z0-9]{1,4}\))*)")
SECN = re.compile(r"§+\s*(\d+[a-z]{0,2}(?:-\d+)?)")
PER = int(os.environ.get("XC_PER", "14"))


STOP = set("the a an of to in for and or is are be was were been does do did under that which this with by on as at it its from not any may can whether when we our court courts case cases have has had would should could must there their they them than then but also such see supra".split())


def toks(s):
    return {w for w in re.findall(r"[a-z][a-z\-']{3,}", s.lower()) if w not in STOP}


def sents_of(t):
    parts, form = core.court_parts(t)
    out = []
    for b, e, part in parts:
        for a, z in core.split_sentences(t, b, e):
            if z - a <= 1500:
                out.append((a, z, part))
    return out, parts


def main():
    P = [l.rstrip("\n").split("\t") for l in open(os.path.join(C.PRIV, "work", "xc_pairs.tsv"), encoding="utf-8")]
    P = [p for p in P if p[13] in ("majority", "perCuriam") and int(p[-4]) >= 19700000]
    seen = set()
    P2 = []
    for p in P:
        if (p[1], p[2]) not in seen:
            seen.add((p[1], p[2]))
            P2.append(p)
    P = P2
    nodes = {int(p[1]) for p in P} | {int(p[2]) for p in P}
    raw = text.fetch(nodes)
    names = C.node_names(nodes)
    od = os.path.join(C.PRIV, "work", "xc")
    os.makedirs(od, exist_ok=True)
    idx = {}
    blocks = []
    stats = collections.Counter()
    for p in P:
        b, tn = int(p[1]), int(p[2])
        if b not in raw or tn not in raw:
            stats["no_text"] += 1
            continue
        tb, tt = text.norm_text(raw[b]), text.norm_text(raw[tn])
        if text.text_sha(raw[b]) != p[8]:
            stats["sha_changed"] += 1
            continue
        qs, qe = int(p[9]), int(p[10])
        near = tb[max(0, qs - 3000):qe + 3000]
        cites = USC.findall(near)
        if not cites:
            stats["no_usc_near_quote"] += 1
            continue
        sb, _ = sents_of(tb)
        st, pt = sents_of(tt)
        if not sb or not st:
            stats["no_sentences"] += 1
            continue
        i0 = next((i for i, (a, z, _) in enumerate(sb) if z > qs), None)
        if i0 is None or sb[i0][0] > qe + 5:
            stats["quote_not_in_court_part"] += 1
            continue
        pickb = set(range(max(0, i0 - 7), min(len(sb), i0 + 8)))
        partsb, _ = core.court_parts(tb)
        for c in core.candidates(tb, partsb, k=4, frame=1):
            j = next((i for i, s in enumerate(sb) if s[0] == c[1]), None)
            if j is not None:
                pickb.add(j)
        secs = {c[1] for c in cites} | set(SECN.findall(near))
        pickt = set()
        for c in core.candidates(tt, pt, k=8, frame=1):
            j = next((i for i, s in enumerate(st) if s[0] == c[1]), None)
            if j is not None:
                pickt.add(j)
        # T sentences closest in words to B's disagreement passage (+-3 sentences round the quote)
        local = toks(" ".join(tb[a:z] for a, z, _ in sb[max(0, i0 - 3):i0 + 4]))
        tt_toks = [toks(tt[a:z]) for a, z, _ in st]
        df = collections.Counter(w for t_ in tt_toks for w in t_)
        sc = []
        for i, t_ in enumerate(tt_toks):
            if core.CITEISH(tt[st[i][0]:st[i][1]]):
                continue
            v = sum(1.0 / (1 + df[w]) ** 0.5 for w in t_ & local)
            if v > 0:
                sc.append((-v, i))
        for _, i in sorted(sc)[:10]:
            pickt.add(i)
        extra = 0
        for i, (a, z, _) in enumerate(st):
            if extra >= 5:
                break
            s = tt[a:z]
            if i not in pickt and any(re.search(r"(?<![\w.])" + re.escape(x) + r"(?![\w])", s) for x in secs)                     and not core.CITEISH(s):
                pickt.add(i)
                extra += 1
        pid = "X%04d" % len(idx)
        nb, nt = names.get(b, ("?", "", "")), names.get(tn, ("?", "", ""))
        usc_list = sorted({"%s U.S.C. § %s%s" % c for c in cites})[:8]
        blk = ["## Pair %s" % pid,
               "B = %s, %s (Cir. %s, %s)   [the later decision; it says it declines to follow / disagrees with T]" % (
                   nb[0], nb[1].split("|")[0], p[16], p[18]),
               "T = %s, %s (Cir. %s, %s)   [the earlier decision]" % (nt[0], nt[1].split("|")[0], p[17], p[19]),
               "Disagreement sentence found in B: \"%s\"" % p[11][:500],
               "US Code citations near it in B: " + "; ".join(usc_list),
               "### B sentences"]
        for i in sorted(pickb):
            a, z, part = sb[i]
            blk.append("B%d: %s" % (i, core.show(tb, a, z, 550)))
        blk.append("### T sentences")
        for i in sorted(pickt):
            a, z, part = st[i]
            blk.append("T%d: %s" % (i, core.show(tt, a, z, 550)))
        idx[pid] = {"by": b, "target": tn, "tid": p[0], "kind": p[4], "sha_b": p[8], "sha_t": text.text_sha(raw[tn]),
                    "B": {str(i): list(sb[i]) for i in pickb}, "T": {str(i): list(st[i]) for i in pickt},
                    "circ_b": int(p[16]), "circ_t": int(p[17]), "date_b": int(p[18]), "date_t": int(p[19]),
                    "pub_b": p[20], "pub_t": p[21]}
        blocks.append("\n".join(blk))
        stats["pairs"] += 1
    json.dump(idx, open(os.path.join(od, "sents.json"), "w", encoding="utf-8"))
    nb = (len(blocks) + PER - 1) // PER
    sizes = []
    for i in range(nb):
        fn = os.path.join(od, "batch_%02d.md" % i)
        with open(fn, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n\n".join(blocks[i * PER:(i + 1) * PER]) + "\n")
        sizes.append(os.path.getsize(fn))
    print(dict(stats), "batches", nb, "bytes", sum(sizes), "max", max(sizes) if sizes else 0)


if __name__ == "__main__":
    main()
