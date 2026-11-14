"""fjc8 rule S1 on base rows: round-6 below_other rows of federal courts of appeals whose scope is `unknown` only
because a consequence dismissal ("Reversed; the petition is dismissed", "... remand with instructions to dismiss")
was read as a second act. The opinion is re-read with round 6's linker and S1's `kind_of` (fjc_scope.py); when the
same (target, kind) comes out with scope `all` and the same disposition quote, the base row is rewritten with scope
`all` (a `--replace` line, DESIGN7 section 6). Nothing else of the row changes.

    python -X utf8 scope_base.py [--procs 10]  -> scope_replace.tsv (13-column history rows), scope_ids.txt, scope_stats.json
"""
import argparse, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
from diag import BO, L  # noqa: E402
import fjc_scope  # noqa: E402

NL = chr(10)
G = {}


def init():
    BO.init()
    G["want"] = json.load(open(os.path.join(HERE, "work", "scope_want.json")))


def run_shard(path):
    if "want" not in G:
        init()
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    want = G["want"].get(tag, {})
    if not want:
        return tag, []
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    out = []
    orig = BO.kind_of
    patched = fjc_scope.make_kind_of(BO)
    for n, g in L.decisions(path):
        rows = want.get(str(n))
        if not rows:
            continue
        BO.kind_of = orig
        r0 = {(r["target"], r["kind"]): r for r in BO.process(n, g, meta.get(n), collections.Counter(), None)}
        BO.kind_of = patched
        r1 = {(r["target"], r["kind"]): r for r in BO.process(n, g, meta.get(n), collections.Counter(), None)}
        BO.kind_of = orig
        for row in rows:
            t, k, q0, q1 = row["target"], row["kind"], row["q0"], row["q1"]
            a, b = r0.get((t, k)), r1.get((t, k))
            if a is None:
                out.append((row["id"], "not_reproduced"))
            elif b is None or b["scope"] != "all":
                out.append((row["id"], "still_unknown"))
            elif b["disp"] != [q0, q1]:
                out.append((row["id"], "other_quote"))
            else:
                out.append((row["id"], "all"))
    return tag, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=10)
    a = ap.parse_args()
    BO.init()
    F = BO.G["F"]
    sidx = diag.shard_index()
    base = {}
    want = collections.defaultdict(lambda: collections.defaultdict(list))
    with open(os.path.join(L.C2, "round7", "stage", "v3", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) < 13 or not p[12].startswith("r6:below:") or p[5] != "unknown" or p[4] not in ("reversed", "vacated"):
                continue
            by = int(p[2])
            if F.system(int(F.court[by])) != 0 or by not in sidx:
                continue
            base[p[0]] = p
            want[sidx[by]][str(by)].append({"id": p[0], "target": int(p[1]), "kind": p[4], "q0": int(p[7]), "q1": int(p[8])})
    json.dump(want, open(os.path.join(HERE, "work", "scope_want.json"), "w"))
    paths = [os.path.join(L.CACHE, t + ".jsonl.gz") for t in want]
    res = collections.Counter()
    ids = []
    for tag, out in L.pmap(run_shard, paths, procs=a.procs, initializer=init):
        for i, v in out:
            res[v] += 1
            if v == "all":
                ids.append(i)
    ids.sort()
    with open(os.path.join(HERE, "scope_replace.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for i in ids:
            p = list(base[i])
            p[5] = "all"
            f.write("\t".join(p) + NL)
    with open(os.path.join(HERE, "scope_ids.txt"), "w", encoding="utf-8", newline=NL) as f:
        f.write(NL.join(ids) + NL)
    st = {"population": len(base), "result": dict(res)}
    json.dump(st, open(os.path.join(HERE, "scope_stats.json"), "w"), indent=1)
    print(st)


if __name__ == "__main__":
    main()
