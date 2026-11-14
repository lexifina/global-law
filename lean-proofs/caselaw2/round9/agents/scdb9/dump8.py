"""scdb8: reading dump for sampled misses: SC caption, the decision below (court, date, caption, citations), where the
SC text mentions the below's citations (by page key), the round-6/7 disposition and the tail of each opinion part.

    python -X utf8 dump8.py work/sample40.tsv [--diag PATH] > work/sample40_dump.txt
"""
import csv, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "below_sc"))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import link  # noqa: E402

L, C = link.L, link.C
NL = chr(10)


def main():
    args = sys.argv[1:]
    dpath = os.path.join(HERE, "work", "diag8.jsonl.gz")
    if "--diag" in args:
        i = args.index("--diag"); dpath = args[i + 1]; del args[i:i + 2]
    rows = list(csv.DictReader(open(args[0], encoding="utf-8"), delimiter="\t"))
    want = {int(x["sc"]) for x in rows}
    diag = {}
    with gzip.open(dpath, "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["n"] in want:
                diag[d["n"]] = d
    F = L.Facts()
    texts = L.fetch_texts(list(want))
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for i, x in enumerate(rows):
        s, b = int(x["sc"]), int(x["below"])
        br = L.node_row(b)
        text = texts[s][1]
        body0 = 0
        if text.startswith("---"):
            e = text.find(NL + "---", 3)
            if e >= 0:
                nl = text.find(NL, e + 4)
                body0 = nl + 1 if nl >= 0 else len(text)
        hw = C.hard_wrapped(text, body0)
        view = C.unwrap_view(text, body0) if hw else text
        pm, _ = (C.part_map2(text) if hw else C.part_map(text))
        d = diag.get(s, {})
        print("#" * 110)
        print("[%d] %s %s %s | SC %d %s | stage %s | mclass %s" % (i + 1, x["caseId"], x["era"], x["group"], s,
                                                                L.node_row(s)[6][:70], x["stage"], x["mclass"]))
        print("  BELOW %d %s %s | %s | cites %s" % (b, F.date[b], F.court_name(F.court[b])[:50], br[6][:70], br[5][:80]))
        print("  r-reasons:", d.get("reason"), d.get("reasons"))
        print("  DISP:", (d.get("disp_text") or "")[:240])
        print("  PARTS:", [(p, bb - a) for a, bb, p, _s in pm])
        lv = L.norm(view)
        hits = 0
        for c in (br[5] or "").split("|"):
            m = re.match(r"\s*(\d+)\s+(.+?)\s+(\d+)\s*$", c)
            if not m:
                continue
            vol, rep, page = m.groups()
            rp = r"\s*".join(re.escape(t) for t in re.findall(r"[A-Za-z]+|\d+|\S", rep))
            for mm in re.finditer(r"\b" + vol + r"\s+" + rp + r"\.?,?\s+" + page + r"\b", lv):
                print("  CITE@%d: ...%s" % (mm.start(), lv[max(0, mm.start() - 300):mm.end() + 80]))
                hits += 1
                if hits >= 3:
                    break
            if hits >= 3:
                break
        if not hits:
            print("  CITE: (no citation of the below found in the text)")
        for a, bb, p, _s in pm:
            if p in ("majority", "perCuriam", "plurality", "majority~"):
                print("  TAIL[%s]: %s" % (p, lv[max(a, bb - 330):bb]))


if __name__ == "__main__":
    main()
