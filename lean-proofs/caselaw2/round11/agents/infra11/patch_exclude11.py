"""infra11 (lead 05:4x, bug from fjc11): make_packs11 --exclude also matches a row's identity (table, by node, target
node, kind), so an earlier round's sample (h10:/t10: ids) excludes the same row certified again under h11:/t11: ids.

    python -X utf8 round11/agents/infra11/patch_exclude11.py
"""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(C2, "round11", "audit", "make_packs11.py")
s = open(p, encoding="utf-8").read()
assert "excluded_keys" not in s, "already patched"


def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a))
    s = s.replace(a, b)


rep('''--exclude   a sample.tsv of an earlier run: its row ids (and decoys) are not drawn again.''',
    '''--exclude   a sample.tsv of an earlier run: its row ids (and decoys) are not drawn again. Round 11: also every row
            with the same identity (table, by node, target node, kind) as a row of that sample (its row 1 and row 2),
            so a round-10 sample (h10:/t10: ids) excludes the same row re-certified with an h11:/t11: id.''')
rep('''    excluded = set()
    for e in a.exclude:
        kr = A.read_tsv(A.resolve(e))
        if kr:
            col = kr[0].index("row_id") if "row_id" in kr[0] else 0
            excluded |= {p[col] for p in kr[1:] if len(p) > col}
''', '''    excluded = set()
    excluded_keys = set()  # round 11 (infra11): (table, by, target, kind) of the excluded samples' rows
    for e in a.exclude:
        kr = A.read_tsv(A.resolve(e))
        if kr:
            col = kr[0].index("row_id") if "row_id" in kr[0] else 0
            excluded |= {p[col] for p in kr[1:] if len(p) > col}
            h = kr[0]
            if all(c in h for c in ("table", "by_node", "target_node", "kind", "role")):
                for p in kr[1:]:
                    d = dict(zip(h, p + [""] * (len(h) - len(p))))
                    if d["role"] != "real":
                        continue
                    excluded_keys.add((d["table"], str(d["by_node"]), str(d["target_node"]), d["kind"]))
                    if d.get("row2_id") and d.get("kind2"):
                        excluded_keys.add((d["table"], str(d["by_node"]), str(d["target_node"]), d["kind2"]))
''')
rep('''    print("class %s: %d rows in the inputs (%s), %d after filters, %d with valid nodes; %d strata; excluded ids %d"
          % (a.cls, n_in, table, len(rows), len(pop), len(popn), len(excluded)))
''', '''    def rkey(r):
        return (r["table"], str(r["by"]), str(r["target"]), r["kind"])
    n_xkey = sum(1 for r in pop if r["id"] not in excluded and (rkey(r) in excluded_keys or (
        r.get("row2") and rkey(r["row2"]) in excluded_keys)))
    print("class %s: %d rows in the inputs (%s), %d after filters, %d with valid nodes; %d strata; excluded ids %d; "
          "rows excluded by identity (table, by, target, kind) only %d"
          % (a.cls, n_in, table, len(rows), len(pop), len(popn), len(excluded), n_xkey))
''')
rep('''        if r["id"] in excluded or (r.get("row2") and r["row2"]["id"] in excluded) or pair in pairs:
            continue
''', '''        if r["id"] in excluded or (r.get("row2") and r["row2"]["id"] in excluded) or pair in pairs:
            continue
        if rkey(r) in excluded_keys or (r.get("row2") and rkey(r["row2"]) in excluded_keys):
            continue
''')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched round11/audit/make_packs11.py")
