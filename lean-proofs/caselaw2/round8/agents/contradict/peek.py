"""Show a pair: python -X utf8 peek.py <pid> [...]  (base quote, new quote, text between, cache h records)."""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "work", "pairs.tsv"), encoding="utf-8")]
cols = rows[0]
idx = {r[0]: dict(zip(cols, r)) for r in rows[1:]}
for pid in sys.argv[1:]:
    r = idx[pid]
    by = int(r["by"])
    t = L.fetch_texts([by])[by][1]
    tr = L.node_row(int(r["target"]))
    print("=" * 100)
    print(pid, r["rule"], "by", by, L.node_row(by)[6], L.node_row(by)[4], "| target", tr[0], tr[6], tr[4], tr[5])
    print("new %s/%s  base %s/%s  pos %s final %s" % (r["new_kind"], r["new_scope"], r["base_kind"], r["base_scope"],
                                                    r["pos"], r["final"]))
    bs, be, ns, ne = int(r["base_s"]), int(r["base_e"]), int(r["new_s"]), int(r["new_e"])
    print("BASE:", L.norm(t[bs:be]))
    print("NEW :", L.norm(t[ns:ne]))
    lo, hi = min(bs, ns), max(be, ne)
    if hi - lo < 2500:
        print("SPAN:", L.norm(t[max(0, lo - 200):hi + 200]))
    else:
        print("TAIL:", L.norm(t[max(0, ne - 600):ne + 300]))
    print("len", len(t))
