"""fedcir11: corpus-intrinsic population of Federal Circuit (and CCPA) review pairs, and how v10d marks them.

    python -X utf8 pop.py run [--procs 5]     -> work/pop.tsv (one line per (acting, cited lower-tribunal decision))

Acting decision D: an opinion of the Federal Circuit (courts2 520) or of the Court of Customs and Patent Appeals (655).
Pair (D, J): J is a cited decision (round-6 cache cw, rel lower) of a federal trial court / special court, dated
0..6 years before D. Per pair: tribunal class, gap, caption relation (round 6 cap_rel), the round-6 below_other trace
(fjc8 diag.trace_one), the judgment line read by round 6 decide (bare, direct), the v10d history rows by D on J with
their Lean verdict, and J's v10d status rows with D as actor. Reads no key.
"""
import argparse, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round8", "agents", "fjc8"))
import diag  # noqa: E402
from diag import BO, L  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work")
ACT_COURTS = {520, 655}
G = {}


def tclass(jc, jdate):
    nm, t = BO.court_at(jc, jdate)
    n = nm.lower()
    if jc == 656:
        return "cfc"
    if jc == 657:
        return "cit"
    if jc == 651:
        return "cavc"
    if jc == 654:
        return "coc"
    if jc == 678:
        return "tax"
    if BO.G["F"].system(jc) == 0 and "district court" in n:
        return "dist"
    if BO.G["F"].system(jc) == 0 and "bankruptcy" in n:
        return "bankr"
    if BO.G["F"].system(jc) == 0:
        return "fedother:%d" % jc
    return "state"


def init():
    BO.init()
    hist = collections.defaultdict(list)
    ids = {}
    F = BO.G["F"]
    with open(os.path.join(C2, "round10", "stage", "v10d", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            try:
                t, b = int(p[1]), int(p[2])
            except (ValueError, IndexError):
                continue
            if int(F.court[b]) in ACT_COURTS:
                hist[(b, t)].append([p[0], p[4], p[5], p[12]])
                ids[p[0]] = None
    with open(os.path.join(C2, "round10", "out", "v10d", "certs.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 3)
            if p[0] == "history" and p[1] in ids:
                ids[p[1]] = p[2]
    for k, v in hist.items():
        for r in v:
            r.append(ids.get(r[0]) or "?")
    G["hist"] = hist
    st = collections.defaultdict(list)
    with open(os.path.join(C2, "round10", "out", "v10d", "status.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) < 10 or p[1] != "-" or p[9] == "-":
                continue
            try:
                a = int(p[9])
            except ValueError:
                continue
            st[int(p[0])].append(p[5] + "@" + p[9])
    G["status"] = st


def run_shard(path):
    if "hist" not in G:
        init()
    F, N = BO.G["F"], BO.G["N"]
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    out = []
    nop = collections.Counter()
    for n, g in L.decisions(path):
        dc = int(F.court[n])
        if dc not in ACT_COURTS:
            continue
        nop["opinions"] += 1
        d_date = int(F.date[n])
        mrow = meta.get(n)
        d_all, d_sides = BO.caption(mrow[7] if mrow else "")
        if not d_all and mrow:
            d_all, d_sides = BO.caption("", mrow[8].split(" | ")[:2])
        disps = BO.dispositions(g)
        res, why = BO.decide(disps, {"district court", "trial court", "court below"}, True)
        jl = ("%s/%s" % (res[0], res[1])) if res else ("-/" + why)
        js = collections.defaultdict(list)
        for cw in g["cw"]:
            if cw["rel"] != "lower":
                continue
            j = cw["j"]
            jd = int(F.date[j])
            gap = BO.day(d_date) - BO.day(jd)
            if gap < 0 or gap > BO.MAX_GAP_DAYS:
                continue
            js[j].append(cw)
        if js:
            nop["with_pair"] += 1
        for j, cws in js.items():
            jc = int(F.court[j])
            cls = tclass(jc, int(F.date[j]))
            cap = BO.cap_rel(d_all, N.name(j), d_sides)
            try:
                stage, info = diag.trace_one(n, g, mrow, j, None)
            except Exception as ex:  # noqa: BLE001
                stage, info = "error:%r" % ex, {}
            h = G["hist"].get((n, j), [])
            s = G["status"].get(j, [])
            out.append([n, j, dc, d_date // 10000, cls, jc, int(F.date[j]), (BO.day(d_date) - BO.day(F.date[j])) // 365,
                        cap, len(cws), jl, stage, ";".join("|".join(x) for x in h) or "-", ";".join(s) or "-",
                        (mrow[7] if mrow else "")[:80], N.name(j)[:80]])
    with open(os.path.join(WORK, "pop." + tag + ".tsv"), "w", encoding="utf-8", newline=NL) as f:
        for r in out:
            f.write("\t".join(str(x).replace("\t", " ") for x in r) + NL)
    return tag, len(out), dict(nop)


COLS = "acting jnode acourt ayear tclass jcourt jdate gapy cap ncw judgment r6stage v10d_hist v10d_status atitle jname"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=5)
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    paths = [p for p in L.shards() if os.path.basename(p).startswith(("cafc.", "federal-special.0"))]
    tot = collections.Counter()
    for tag, k, nop in L.pmap(run_shard, paths, procs=a.procs, initializer=init):
        print(tag, k, nop, flush=True)
        tot.update(nop)
    with open(os.path.join(WORK, "pop.tsv"), "w", encoding="utf-8", newline=NL) as fo:
        fo.write("\t".join(COLS.split()) + NL)
        for p in sorted(paths):
            fp = os.path.join(WORK, "pop." + os.path.basename(p)[:-len(".jsonl.gz")] + ".tsv")
            if os.path.exists(fp):
                fo.writelines(open(fp, encoding="utf-8"))
                os.remove(fp)
    print(dict(tot))


if __name__ == "__main__":
    main()
