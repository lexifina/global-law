"""fjc9: for pairs whose F1 drop is a guard, show which guard word fired where (cache windows).

    python -X utf8 gpeek.py work/f1why.tsv REASON_SUBSTR N [seed]
"""
import csv, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
from diag import BO, L  # noqa: E402


def show(a, d):
    sidx = diag.shard_index()
    tag = sidx.get(a)
    path = os.path.join(L.CACHE, tag + ".jsonl.gz")
    for n, g in L.decisions(path):
        if n != a:
            continue
        for cw in g["cw"]:
            if cw["j"] != d:
                continue
            w0, wt = cw["w"]
            c0, c1 = cw["c"][0] - w0, cw["c"][1] - w0
            s0, s1 = cw["s"][0] - w0, cw["s"][1] - w0
            ps = BO.prev_sentence(wt, s0)
            a0 = ps[0] if ps else s0
            at = wt[a0:s1]
            hits = []
            for nm, rx, txt in (("EARLIER", BO.EARLIER, at), ("EARLY", BO.EARLY, at),
                                ("LATER_after", BO.LATER, wt[c1:s1] + " || " + wt[s1:s1 + 250])):
                for m in rx.finditer(txt):
                    hits.append("%s:%r" % (nm, m.group(0)))
            sg = BO.SIGNAL_RX.search(wt[s0:c0][-220:])
            if sg:
                hits.append("SIGNAL:%r" % sg.group(0))
            print("--- part", cw["part"], "hits", hits)
            print(wt[max(0, a0 - 300):c0] + "[[" + wt[c0:c1] + "]]" + wt[c1:s1 + 260])
        z = g["z"] or {}
        for e in (z.get("ends") or [])[-1:]:
            print("=== end:", e[1][-400:])
        break


def main():
    rows = list(csv.reader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"))
    sel = [r for r in rows if sys.argv[2] in r[3]]
    random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 1).shuffle(sel)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for r in sel[:int(sys.argv[3])]:
        print("\n######", r[0], r[1], r[2], r[3])
        show(int(r[1]), int(r[0]))


if __name__ == "__main__":
    main()
