"""calpart9: show a refused row in context: zones of its text node and the quote's neighbourhood.

    python -X utf8 show.py <refused.tsv> <k> [k ...]      (line numbers, 0-based)
"""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import partzone as PZ  # noqa: E402

L = PZ.L
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
for k in sys.argv[2:]:
    p = lines[int(k)].split("\t")
    n, s, e = int(p[3]), int(p[4]), int(p[5])
    t = L.fetch_texts([n])[n][1]
    zs, info = PZ.zones(t)
    print("=" * 100)
    print(p[0], p[1], "row part", p[6], "zone", p[7], "| court", p[12], p[13], "hw", info["hw"])
    for a, b, zp in zs:
        if a < e + 3000 and b > s - 3000:
            print("  zone %d-%d %s | %s" % (a, b, zp, L.norm(t[a:a + 120])))
    print("  --- before:", L.norm(t[max(0, s - 500):s]))
    print("  --- QUOTE:", L.norm(t[s:e])[:600])
