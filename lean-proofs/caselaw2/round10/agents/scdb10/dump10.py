"""scdb10: diagnosis dump of the h0 no_anchor misses (anatomy10 output): each occurrence of the decision below's
citations in the SC text, with its part, its position against the history-zone end and the text before it.

    python -X utf8 dump10.py work/anatomy_v9c.tsv [--stage no_anchor] [--diag PATH] > work/noanchor_dump.txt
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
    dpath = os.path.join(C2, "round9", "agents", "scdb9", "work", "diag9.jsonl.gz")
    stage = "no_anchor"
    if "--diag" in args:
        i = args.index("--diag"); dpath = args[i + 1]; del args[i:i + 2]
    if "--stage" in args:
        i = args.index("--stage"); stage = args[i + 1]; del args[i:i + 2]
    rows = [x for x in csv.DictReader(open(args[0], encoding="utf-8"), delimiter="\t") if x["stage"].startswith(stage)]
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
        ph = d.get("ph_end")
        print("#" * 100)
        print("[%d] %s %s %s | SC %d %s | %s | len %d ph_end %s" % (i + 1, x["caseId"], x["era"], x["group"], s,
                                                                   L.node_row(s)[6][:60], x["stage"], len(view), ph))
        print("  BELOW %d %s %s | %s | cites %s" % (b, F.date[b], F.court_name(F.court[b])[:50], br[6][:60], br[5][:80]))
        print("  reasons:", d.get("reasons"), "| DISP:", (d.get("disp_text") or "")[:160].replace(NL, " "))
        for c in d.get("cands", []):
            if c["j"] != b:
                continue
            for o in c["occ"]:
                p0 = o[0]
                print("  OCC@%d [%s%s typ=%s sig=%s named=%s disq=%s]: ...%s" % (
                    p0, o[1], " zone" if ph and p0 < ph else "", o[2], o[3], o[4], o[5],
                    L.norm(view[max(0, p0 - 380):p0 + 70])))


if __name__ == "__main__":
    main()
