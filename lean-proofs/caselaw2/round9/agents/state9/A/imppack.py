# state9 round 9 (imp): copy of round7/agents/antecedent/antepack.py, adapted.
"""Round 7, agent `antecedent`: reader packs from sel.jsonl (the candidates chosen for reading).

    python -X utf8 antepack.py [--sel sel.jsonl] [--size 40] [--start 1]

Writes packs/pack_NNN.md (READER_BRIEF_IMP.md describes the item layout) and packs/index.tsv
(id, pack, n targets). The window is cut from the git-HEAD text (unwrapped view of a hard-wrapped text, same
offsets), from 1000 characters before the act sentence (not before its part) to 300 after it; the act sentence is
marked ⟦ ⟧, each listed decision's citation / name hit is followed by [Tk]. Items whose act sentence no longer matches
the text are skipped (counted). No answer key is read.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402
C = L.reader_common()
NL = chr(10)


def fmt_date(d):
    d = str(d)
    return "%s-%s-%s" % (d[:4], d[4:6], d[6:8]) if len(d) == 8 else d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sel", default=os.path.join(HERE, "sel.jsonl"))
    ap.add_argument("--size", type=int, default=40)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--out", default=os.path.join(HERE, "packs"))
    a = ap.parse_args()
    F = L.Facts()
    items = [json.loads(l) for l in open(a.sel, encoding="utf-8")]
    os.makedirs(a.out, exist_ok=True)
    texts = {}
    nodes = sorted({it["n"] for it in items})
    for i in range(0, len(nodes), 2000):
        for n, (sha, t) in L.fetch_texts(nodes[i:i + 2000]).items():
            texts[n] = t
    idx = open(os.path.join(a.out, "index.tsv"), "a", encoding="utf-8", newline=NL)
    skipped = 0
    blocks = []
    for it in items:
        t = texts.get(it["n"])
        if t is None:
            skipped += 1
            continue
        body0 = 0
        if t.startswith("---"):
            e = t.find(NL + "---", 3)
            if e >= 0:
                nl = t.find(NL, e + 4)
                body0 = nl + 1 if nl >= 0 else len(t)
        view = C.unwrap_view(t, body0) if it["hw"] else t
        s0, s1 = it["s"]
        if L.norm(view[s0:s1]) != it["act"]:
            skipped += 1
            continue
        w0 = max(it.get("pstart", 0), s0 - 1000, body0)
        tl = [x for x in it["targets"] if x["hit"][0] >= w0]
        w1 = min(len(view), s1 + 300)
        marks = [(s0, "⟦"), (s1, "⟧")]
        lines = []
        for k, x in enumerate(tl, 1):
            x["T"] = "T%d" % k
            marks.append((x["hit"][1], "[T%d]" % k))
            where = {"act": "in act", "near": "before (gap %d)" % (s0 - x["span"][1]),
                     "far": "earlier (far; context only)"}[x["where"]]
            how = ('cite "%s"' % x["ev"][5:]) if x["how"] == "cite" else ('name "%s"' % x["ev"][5:])
            lines.append("- T%d: %s | %s | %s | %s | %s | %s" % (k, x["name"] or "?", x["cite"] or "?",
                                                                fmt_date(x["date"]), F.court_name(x["court"]), how, where))
        marks.sort(key=lambda m: (m[0], m[1] != "⟧"))
        out, pos = [], w0
        for off, m in marks:
            if off < w0 or off > w1:
                continue
            out.append(view[pos:off])
            out.append(m)
            pos = off
        out.append(view[pos:w1])
        win = "".join(out).replace("\t", " ")
        blk = ["### ITEM %s" % it["id"],
               "ACTING: %s | %s | %s | %s | part: %s" % (it["by_name"] or "?", it["by_cite"] or "?",
                                                         F.court_name(it["by_court"]), fmt_date(it["by_date"]),
                                                         it["part"].rstrip("~")),
               "TARGETS:"] + lines + ["WINDOW:", "", win.strip(), "", "ACT: " + it["act"].strip(), ""]
        tmap = {x["T"]: {k2: x[k2] for k2 in ("t", "ev", "span", "where", "hit", "how", "name", "cite")} for x in tl}
        blocks.append((it["id"], len([x for x in tl if x["where"] != "far"]), NL.join(blk),
                       {"id": it["id"], "n": it["n"], "s": it["s"], "act": it["act"], "part": it["part"],
                        "hw": it["hw"], "tier": it.get("tier", ""), "T": tmap}))
    k = a.start
    for i in range(0, len(blocks), a.size):
        name = "pack_%03d" % k
        chunk = blocks[i:i + a.size]
        with open(os.path.join(a.out, name + ".md"), "w", encoding="utf-8", newline=NL) as f:
            f.write("# %s (%d items; brief: READER_BRIEF_IMP.md)\n\n" % (name, len(chunk)))
            for _id, _nt, b, _m in chunk:
                f.write(b + NL)
        with open(os.path.join(a.out, "map.jsonl"), "a", encoding="utf-8", newline=NL) as fm:
            for _id, nt, _b, m in chunk:
                idx.write("%s\t%s\t%d\n" % (_id, name, nt))
                m["pack"] = name
                fm.write(json.dumps(m, ensure_ascii=False) + NL)
        k += 1
    idx.close()
    print("packs", k - a.start, "items", len(blocks), "skipped", skipped)


if __name__ == "__main__":
    main()
