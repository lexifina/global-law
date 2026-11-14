"""fjc8: corpus funnel over federal court of appeals opinions (no key read).

    python -X utf8 funnel.py [--procs 10]  -> work/funnel/<shard>.jsonl.gz + work/funnel_summary.json

For every federal court of appeals opinion in the round-6 cache: the below_other rows it gets, its own negative
judgment line (decide() with direct review), and for each distinct cited lower-court (trial / bankruptcy) decision
of its own circuit within 6 years the first failing below_other step (diag.trace_one).
"""
import argparse, collections, gzip, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
from diag import BO, L  # noqa: E402

NL = chr(10)
OUT = os.path.join(HERE, "work", "funnel")


def run_shard(path):
    if "F" not in BO.G:
        BO.init()
    F = BO.G["F"]
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    st = collections.Counter()
    with gzip.open(os.path.join(OUT, tag + ".jsonl.gz.part"), "wt", encoding="utf-8", newline=NL) as fo:
        for n, g in L.decisions(path):
            if not g["cw"]:
                continue
            dc = int(F.court[n])
            if F.system(dc) != 0:
                continue
            d_date = int(F.date[n])
            if not d_date:
                continue
            if BO.court_at(dc, d_date)[1] != "A":
                continue
            st["opinions"] += 1
            rows = BO.process(n, g, meta.get(n), collections.Counter(), None)
            disps = BO.dispositions(g)
            js = []
            for cw in g["cw"]:
                j = cw["j"]
                if cw["rel"] != "lower" or j in js:
                    continue
                jc = int(F.court[j])
                ph, cls = BO.tphr(jc, int(F.date[j]))
                if cls not in ("trial", "bankr"):
                    continue
                if not BO.circuit_ok(dc, jc, d_date):
                    continue
                gap = BO.day(d_date) - BO.day(F.date[j])
                if gap < 0 or gap > BO.MAX_GAP_DAYS:
                    continue
                js.append(j)
            tr = {}
            for j in js:
                stage, info = diag.trace_one(n, g, meta.get(n), j, None)
                tr[j] = [stage, info.get("cap", -1)]
            res, why = BO.decide(disps, {"district court", "district judge", "trial court", "court below"}, True)
            jl = [res[0], res[1]] if res else [None, why]
            fo.write(json.dumps({"n": n, "rows": [[r["target"], r["kind"], r["scope"]] for r in rows],
                                 "jl": jl, "cands": tr}, separators=(",", ":")) + NL)
    os.replace(os.path.join(OUT, tag + ".jsonl.gz.part"), os.path.join(OUT, tag + ".jsonl.gz"))
    return tag, dict(st)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    paths = [p for p in L.shards() if diag.APP_RX.match(os.path.basename(p)[:-len(".jsonl.gz")])]
    paths.sort(key=os.path.getsize, reverse=True)
    for tag, st in L.pmap(run_shard, paths, procs=a.procs, initializer=BO.init):
        print(tag, st, flush=True)


if __name__ == "__main__":
    main()
