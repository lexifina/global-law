"""Merge the set-aside rows: base claims (r7setaside_base.py), new below_other rows (r7setaside_bo.py), rehear rows
(r7rehear.py) -> rows_setaside.jsonl. One row per (by, target, kind), base first. A row of the other two files whose
(by, target, kind) is a base history row is left to the base script's decision (certify7 would check the base row's
own certificate and scope with the claim, so the base rules must be the ones that apply)."""
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
R6H = os.path.normpath(os.path.join(HERE, "..", "..", "..", "round6", "history"))
base = set()
for line in open(os.path.join(R6H, "stage", "final2", "history.tsv"), encoding="utf-8"):
    p = line.split("\t", 6)
    base.add((int(p[2]), int(p[1]), p[4]))
seen, out, c = set(), [], collections.Counter()
for f in ("rows_setaside_base.jsonl", "rows_setaside_bo.jsonl", "rows_setaside_rehear.jsonl"):
    for line in open(os.path.join(HERE, f), encoding="utf-8"):
        r = json.loads(line)
        k = (r["by"], r["target"], r["kind"])
        if k in seen:
            c["dup:" + f] += 1
            continue
        if f != "rows_setaside_base.jsonl" and k in base:
            c["base_row_left_to_base_rules:" + f] += 1
            continue
        seen.add(k)
        out.append(r)
        c[f] += 1
with open(os.path.join(HERE, "rows_setaside.jsonl"), "w", encoding="utf-8", newline="\n") as o:
    for r in out:
        o.write(json.dumps(r, ensure_ascii=False) + "\n")
print(dict(c), len(out))
