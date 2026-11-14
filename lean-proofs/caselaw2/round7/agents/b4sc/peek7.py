"""b4sc: print rows for reading (development / own sample). No answer key.

    python -X utf8 peek7.py <rows.jsonl> [--n 30] [--seed 7] [--match REGEX on rule] [--ctx 600]
"""
import argparse, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rows")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--match", default="")
    ap.add_argument("--ctx", type=int, default=500)
    a = ap.parse_args()
    rows = [json.loads(x) for x in open(a.rows, encoding="utf-8")]
    rows = [r for r in rows if re.search(a.match, r["rule"])]
    random.Random(a.seed).shuffle(rows)
    rows = rows[:a.n]
    F = L.Facts()
    T = L.fetch_texts({r["by"] for r in rows})
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for i, r in enumerate(rows, 1):
        t = T[r["by"]][1]
        b, g = L.node_row(r["by"]), L.node_row(r["target"])
        print("=" * 100)
        print("#%d %s by %d %s (%s) %s | kind %s scope %s ev %s" % (i, r["rule"], r["by"], b[6][:70], b[4], b[5][:40],
                                                                   r["kind"], r["scope"], r["ev"]))
        print("   target %d %s | %s | %s | %s" % (r["target"], g[6][:70], F.court_name(int(F.court[r["target"]])), g[4],
                                              g[5][:60]))
        q0, q1 = r["disp"]
        print("   DISP:", L.norm(t[q0:q1])[:400])
        if r.get("anchor"):
            a0, a1 = r["anchor"]
            print("   ANCHOR [%s]: %s" % (r["anchor_part"], L.norm(t[max(0, a0 - a.ctx):a0]) [-a.ctx:] + " <<" +
                                         L.norm(t[a0:a1]) + ">> " + L.norm(t[a1:a1 + 200])))
        else:
            print("   (plain) near:", L.norm(t[max(0, q0 - a.ctx):q0])[-a.ctx:])


if __name__ == "__main__":
    main()
