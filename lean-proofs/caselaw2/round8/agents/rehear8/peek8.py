"""Development reading: print sampled rows (acting quote, both captions / dates, the start of the target's body).

    python -X utf8 peek8.py ROWS.jsonl N SEED [--body 500] [--rule SUBSTR]
Every pair printed is appended to read_ids.txt (by, target, rows file).
"""
import sys

sys.dont_write_bytecode = True
import argparse, json, os, random  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, os.path.join(C2, "round7", "agents", "b4rehear"))
import r6lib as L  # noqa: E402
import r7rehear as R7  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rows")
    ap.add_argument("n", type=int)
    ap.add_argument("seed", type=int)
    ap.add_argument("--body", type=int, default=500)
    ap.add_argument("--rule", default="")
    ap.add_argument("--ctx", type=int, default=0)
    a = ap.parse_args()
    rows = [json.loads(x) for x in open(a.rows, encoding="utf-8")]
    rows = [r for r in rows if a.rule in r["rule"]]
    random.Random(a.seed).shuffle(rows)
    rows = rows[:a.n]
    texts = L.fetch_texts([r["by"] for r in rows] + [r["target"] for r in rows])
    F = L.Facts()
    with open(os.path.join(HERE, "read_ids.txt"), "a", encoding="utf-8", newline="\n") as o:
        for r in rows:
            o.write("%d\t%d\t%s\n" % (r["by"], r["target"], os.path.basename(a.rows)))
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for i, r in enumerate(rows):
        bt = texts[r["by"]][1]
        tt = texts[r["target"]][1]
        pb, pt = L.node_row(r["by"]), L.node_row(r["target"])
        q0, q1 = r["main"]
        print("=" * 100)
        print("#%d %s %s  scope=%s" % (i, r["rule"], r["kind"], r["scope"]))
        print("BY  %d %s %s | %s" % (r["by"], int(F.date[r["by"]]), pb[6][:90], F.court_name(F.court[r["by"]])))
        print("TGT %d %s %s" % (r["target"], int(F.date[r["target"]]), pt[6][:90]))
        print("Q:", L.norm(bt[max(0, q0 - a.ctx):q1 + a.ctx])[:900])
        b0 = R7.text_body(tt)
        print("T body:", L.norm(tt[b0:b0 + 4000])[:a.body])
        bb = R7.text_body(bt)
        print("BY len", len(bt) - bb, "| T len", len(tt) - b0)


if __name__ == "__main__":
    main()
