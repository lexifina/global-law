"""scdb9: text files for reader sub-agents (corpus text only; no key field, no rule, no expected answer).

    python -X utf8 readdump9.py <sample.tsv> <outdir>   -> <outdir>/<sc node>.txt (the Supreme Court decision's text)
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

NL = chr(10)


def main():
    rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    want = sorted({int(x["sc"]) for x in rows})
    texts = L.fetch_texts(want)
    for n in want:
        t = texts[n][1]
        with open(os.path.join(out, "%d.txt" % n), "w", encoding="utf-8", newline=NL) as f:
            f.write(t if t.endswith(NL) else t + NL)
    print("wrote", len(want))


if __name__ == "__main__":
    main()
