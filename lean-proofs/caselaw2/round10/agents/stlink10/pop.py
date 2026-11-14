"""stlink10 step 1: corpus-intrinsic population of state court-of-last-resort reversals of an intermediate decision.

    python -X utf8 pop.py scan [--procs 8]      -> work/pop/<shard>.jsonl (one record per L opinion of interest)
    python -X utf8 pop.py caption               -> work/pop_capmatch.jsonl (uncited same-caption A decisions)
    python -X utf8 pop.py table                 -> work/pairs.tsv + printed shares

Reads the round-6 cache, graph/nodes.tsv, court facts, the v9c history table and certs (to know which pairs are
marked). No key.
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
from diag import BO, L  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work")
POP = os.path.join(WORK, "pop")
GAP = 1826
NEG = {"reversed", "vacated", "modified"}
C2 = L.C2
G = {}


def init():
    BO.init()
    F = BO.G["F"]
    # A-tier courts of each state system
    acourts = collections.defaultdict(set)
    for cid, rows in BO.G["epochs"].items():
        for e0, e1, nm, t in rows:
            if t == "A" and F.system(cid) not in (0, -1):
                acourts[F.system(cid)].add(cid)
    G["acourts"] = acourts


def app_phrases(sysid, date, d_name):
    ph = set()
    lo = date - 60000   # the court must have sat as an intermediate court within ~6 years before the date
    for c in G["acourts"].get(sysid, ()):
        if not any(t == "A" and e0 <= date and e1 >= lo for e0, e1, _nm, t in BO.G["epochs"][c]):
            continue
        p, cls = BO.tphr(c, date)
        if cls == "app":
            ph |= p
    return {p for p in ph if p not in d_name}


def trial_phrases(app, d_name):
    ph = set(BO.TRIAL_PHRASES) | {"trial court", "trial judge", "trial justice", "chancellor", "court of chancery"}
    return {p for p in ph if p not in d_name and p not in app}


def scan_shard(path):
    if "acourts" not in G:
        init()
    F, N = BO.G["F"], BO.G["N"]
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    out = []
    st = collections.Counter()
    for n, g in L.decisions(path):
        dc = int(F.court[n])
        sysid = F.system(dc)
        d_date = int(F.date[n])
        if sysid in (0, -1) or not d_date:
            continue
        d_cname, d_tier = BO.court_at(dc, d_date)
        if d_tier != "L":
            continue
        st["L_opinions"] += 1
        if not G["acourts"].get(sysid):
            continue
        mrow = meta.get(n)
        d_name = BO.norm_ws(d_cname).replace("courts of", "court of")
        app = app_phrases(sysid, d_date, d_name)
        if not app:
            continue
        st["L_with_A"] += 1
        disps = BO.dispositions(g)
        ra, wa = BO.decide(disps, app, True)
        rt, wt = BO.decide(disps, trial_phrases(app, d_name), False)
        ka = ra[0] if ra else None
        kt = ra and None
        kt = rt[0] if rt else None
        d_all, d_sides = BO.caption(mrow[7] if mrow else "")
        if not d_all and mrow:
            d_all, d_sides = BO.caption("", mrow[8].split(" | ")[:2])
        z = g["z"]
        ctx = ""
        if z:
            ctx = (z["head"][1][:2500] if z.get("head") else "") + " " + (z["open"][1] if z.get("open") else "")
        inter_named = any(BO.norm_ws(m.group(1)) in app for m in BO.COURT_RX.finditer(ctx))
        cands = {}
        for cw in g["cw"]:
            j = cw["j"]
            jc = int(F.court[j])
            if F.system(jc) != sysid:
                continue
            jd = int(F.date[j])
            if BO.court_at(jc, jd)[1] != "A":
                continue
            gap = BO.day(d_date) - BO.day(jd)
            if gap < 0 or gap > GAP:
                continue
            cap = BO.cap_rel(d_all, N.name(j), d_sides)
            if cap < 1:
                continue
            phrases, cls = BO.tphr(jc, jd)
            ph2 = {p for p in phrases if p not in d_name}
            ok, why, anchor, apart = BO.eval_candidate(cw, cap, ph2, True)
            c = cands.setdefault(j, {"j": j, "cap": cap, "gap": gap, "whys": [], "parts": []})
            c["whys"].append(why if not ok else "ok:" + why)
            c["parts"].append(cw["part"])
        if not cands and ka not in NEG:
            continue
        rec = {"n": n, "tag": tag, "sys": sysid, "date": d_date, "ka": ka,
               "sa": ra[1] if ra else wa, "how": ra[4] if ra else "", "kt": kt, "ht": rt[4] if rt else wt,
               "inter": int(inter_named), "toks": sorted(d_all), "sides": [sorted(s) for s in d_sides],
               "cands": list(cands.values())}
        if cands:
            stage = {}
            for j in cands:
                try:
                    s, info = diag.trace_one(n, g, mrow, j, collections.Counter())
                except Exception as ex:  # noqa: BLE001
                    s = "trace_error"
                stage[j] = s
            for c in rec["cands"]:
                c["r6"] = stage[c["j"]]
        out.append(rec)
        st["records"] += 1
    with open(os.path.join(POP, tag + ".jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(POP, tag + ".stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(st, f)
    return tag, len(out)


STATE_RX = re.compile(r"^(?!ca\d|cadc|cafc|bankruptcy|supreme-court|tax-court|federal-special|tribal)[a-z-]+$")


def state_shards():
    out = []
    for p in L.shards():
        tag = os.path.basename(p)[:-len(".jsonl.gz")]
        base = tag.split(".")[0]
        if base.endswith(("-appellate", "-other-courts", "-district")) or "-appellate-" in base:
            continue
        if not STATE_RX.match(base):
            continue
        out.append(p)
    return out


def load_recs():
    recs = []
    for f in sorted(os.listdir(POP)):
        if f.endswith(".jsonl"):
            recs += [json.loads(l) for l in open(os.path.join(POP, f), encoding="utf-8") if l.strip()]
    return recs


def caption_pass():
    """uncited A decisions of the same state with the acting caption (cap 2), 0..5 years before, for negative
    opinions (judgment line negative for the intermediate court, named or bare)."""
    init()
    F = BO.G["F"]
    recs = [r for r in load_recs() if r["ka"] in NEG]
    idx = collections.defaultdict(list)
    for r in recs:
        for t in r["toks"]:
            idx[(r["sys"], t)].append(r)
    acourt_ids = set().union(*G["acourts"].values())
    import numpy as np
    courts = F.court
    mask = np.isin(courts, np.array(sorted(acourt_ids)))
    want = set(np.nonzero(mask)[0].tolist())
    print("A-court nodes", len(want), flush=True)
    found = collections.defaultdict(list)
    with open(L.NODES, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i not in want:
                continue
            p = line.rstrip("\r\n").split("\t")
            nm = p[6] if len(p) > 6 else ""
            jc = int(courts[i])
            jd = int(F.date[i])
            if not jd or BO.court_at(jc, jd)[1] != "A":
                continue
            sysid = F.system(jc)
            j_all, _ = BO.caption(nm)
            seen = set()
            for t in j_all:
                for r in idx.get((sysid, t), ()):
                    if r["n"] in seen:
                        continue
                    seen.add(r["n"])
                    gap = BO.day(r["date"]) - BO.day(jd)
                    if gap < 0 or gap > GAP:
                        continue
                    cap = BO.cap_rel(set(r["toks"]), nm, [set(s) for s in r["sides"]])
                    if cap >= 2:
                        found[r["n"]].append((i, gap))
    with open(os.path.join(WORK, "pop_capmatch.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for n, v in found.items():
            f.write(json.dumps({"n": n, "m": v}) + NL)
    print("opinions with a same-caption A decision", len(found))


def table():
    recs = {r["n"]: r for r in load_recs()}
    cm = {}
    p = os.path.join(WORK, "pop_capmatch.jsonl")
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            d = json.loads(l)
            cm[d["n"]] = d["m"]
    hist = collections.defaultdict(list)
    with open(os.path.join(C2, "round9", "stage", "v9c", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            q = line.rstrip(NL).split("\t")
            if len(q) >= 13:
                hist[int(q[1])].append((q[0], int(q[2]), q[4], q[5], q[12]))
    ver = {}
    with open(os.path.join(C2, "round9", "out", "v9c", "certs.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            q = line.rstrip(NL).split("\t")
            if q[0] == "history":
                ver[q[1]] = q[2]
    rows = []
    for n, r in recs.items():
        if r["ka"] not in NEG:
            continue
        cited = {c["j"]: c for c in r["cands"]}
        unc = {j: g for j, g in cm.get(n, []) if j not in cited}
        for j, c in cited.items():
            rows.append((n, j, "cited", c["cap"], c["gap"], c.get("r6", ""), ",".join(sorted(set(c["whys"])))))
        for j, g in unc.items():
            rows.append((n, j, "uncited", 2, g, "uncited", ""))
    out = []
    cnt = collections.Counter()
    for n, j, how, cap, gap, r6, whys in rows:
        r = recs[n]
        hs = hist.get(j, [])
        mine = [h for h in hs if h[1] == n]
        mark = "-"
        if mine:
            h = mine[0]
            mark = "%s:%s:%s" % (h[2], h[3], ver.get(h[0], "?"))
        other_neg = [h for h in hs if h[1] != n and h[2] in ("reversed", "vacated", "modified")]
        ncand = len(r["cands"]) + len([1 for jj, _ in cm.get(n, []) if jj not in {c["j"] for c in r["cands"]}])
        out.append([n, j, r["tag"], r["sys"], r["date"] // 100000 * 10, how, cap, gap, r["ka"], r["sa"], r["how"],
                    r["kt"] or "-", r["inter"], ncand, r6, whys, mark, len(other_neg)])
        stat = "marked_ok" if mine and ver.get(mine[0][0]) == "ok" else ("marked_refused" if mine else "unmarked")
        cnt[(how, stat)] += 1
    with open(os.path.join(WORK, "pairs.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("by\ttarget\ttag\tsys\tdecade\thow\tcap\tgap\tka\tsa\tdhow\tkt\tinter\tncand\tr6\twhys\tmark\tother_neg\n")
        for o in out:
            f.write("\t".join(str(x) for x in o) + NL)
    for k, v in sorted(cnt.items()):
        print(k, v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--shards")
    a = ap.parse_args()
    os.makedirs(POP, exist_ok=True)
    if a.cmd == "scan":
        paths = state_shards()
        if a.shards:
            want = set(a.shards.split(","))
            paths = [p for p in paths if os.path.basename(p)[:-len(".jsonl.gz")] in want]
        paths.sort(key=os.path.getsize, reverse=True)
        print(len(paths), "shards", flush=True)
        if a.procs <= 1:
            init()
            for p in paths:
                print(scan_shard(p), flush=True)
        else:
            for tag, k in L.pmap(scan_shard, paths, procs=a.procs, initializer=init):
                print(tag, k, flush=True)
    elif a.cmd == "caption":
        caption_pass()
    elif a.cmd == "table":
        table()


if __name__ == "__main__":
    main()
