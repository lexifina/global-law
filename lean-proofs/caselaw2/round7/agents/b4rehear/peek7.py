"""Development reading: a seeded random sample of rows of one rule pattern, shown compactly.

    python -X utf8 peek7.py ROWS.jsonl RULE_REGEX N SEED [--ids-out FILE]

Prints, per row: acting and target (name, date, docket), the main quote, the anchor, and the opening of the
target's text. Every row id shown is appended to read_ids.txt (excluded from the blind audit spec)."""
import sys

sys.dont_write_bytecode = True
import json, os, random, re  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "round6", "history")))
import r6lib as L  # noqa: E402

rows_path, rx, n, seed = sys.argv[1], re.compile(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
rows = [json.loads(x) for x in open(rows_path, encoding="utf-8")]
rows = [r for r in rows if rx.search(r["rule"])]
if "--fresh" in sys.argv:  # rows not shown before (read_ids.txt)
    seen = set(open(os.path.join(HERE, "read_ids.txt"), encoding="utf-8").read().split()) \
        if os.path.exists(os.path.join(HERE, "read_ids.txt")) else set()
    rows = [r for r in rows if "h7:%d:%d:%s" % (r["by"], r["target"], r["kind"]) not in seen]
random.Random(seed).shuffle(rows)
rows = rows[:n]
F = L.Facts()
texts = L.fetch_texts({r["by"] for r in rows} | {r["target"] for r in rows})
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ids = []
for i, r in enumerate(rows):
    d, t = L.node_row(r["by"]), L.node_row(r["target"])
    dt, tt = texts[r["by"]][1], texts[r["target"]][1]
    q = L.norm(dt[r["main"][0]:r["main"][1]])
    a = L.norm(dt[r["anchor"][0]:r["anchor"][1]]) if r.get("anchor") else ""
    b0 = tt.find("\n---", 3)
    tb = L.norm(tt[b0 + 4:b0 + 4 + 2500]) if b0 >= 0 else L.norm(tt[:2500])
    print("#%d %s %s %s scope=%s ev=%s claim=%s" % (i, r["rule"], r["kind"], "", r["scope"], r["ev"][:50], r.get("claim")))
    print("  D %d %s | %s | %s" % (r["by"], int(F.date[r["by"]]), d[6][:90] if len(d) > 6 else "", len(dt)))
    print("  T %d %s | %s | %s" % (r["target"], int(F.date[r["target"]]), t[6][:90] if len(t) > 6 else "", len(tt)))
    print("  Q:", q[:500])
    if a:
        print("  A:", a[:300])
    print("  Tbody:", tb[300:900] if len(tb) > 900 else tb[:600])
    ids.append("h7:%d:%d:%s" % (r["by"], r["target"], r["kind"]))
with open(os.path.join(HERE, "read_ids.txt"), "a", encoding="utf-8", newline="\n") as o:
    for x in ids:
        o.write(x + "\n")
