"""Bounded search for novel interactions (loop jptax). Writes ~/cmp/loop/jp/runs/novel_*.json and prints summaries."""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(__file__))
from jp import adult, hh, run, one, var, furusato_scan

OUT = os.path.expanduser("~/cmp/loop/jp/runs")
os.makedirs(OUT, exist_ok=True)
which = sys.argv[1] if len(sys.argv) > 1 else "all"


def burden_at(h, d, onestop=False, who=0):
    a, b = run([h, var(h, {f"adults.{who}.furusato": d, f"adults.{who}.oneStop": onestop})])
    return d - (a["_tax"] - b["_tax"])


# N-A: ふるさと burden above 2,000 yen when the 人的控除差調整額 misses a deduction difference
if which in ("all", "A"):
    res = []
    fams = {
        "student_1.0M": dict(children=[{"age": 20, "wages": 1000000}], spouse=0),
        "student_0": dict(children=[{"age": 20, "wages": 0}], spouse=0),
        "spouse_1.5M": dict(children=[], spouse=1500000),   # 合計所得 850,000: 配偶者特別控除, IT 380k / local 330k
        "spouse_0": dict(children=[], spouse=0),
        "lifeins": dict(children=[], spouse=None, life=[80000, 80000, 80000]),
        "single_father": dict(children=[8], spouse=None, father=True),
    }
    for name, f in fams.items():
        worst = None
        for w in range(2000000, 20000001, 50000):
            ad = [adult(48, w, lifeIns=f.get("life", []))]
            if f["spouse"] is not None:
                ad.append(adult(46, f["spouse"]))
            h = hh(ad, married=len(ad) == 2, children=f["children"],
                   jpSingleParentSex="M" if f.get("father") else "F")
            lim, curve = furusato_scan(h, step=2000, hi=600000)
            # excess burden at a donation of 100,000 (or the limit if lower) and at the limit
            d = min(100000, lim) if lim > 2000 else 0
            bd = dict(curve)
            row = dict(fam=name, wage=w, limit=lim, burdenLimit=bd[lim], burden100k=bd.get(100000))
            res.append(row)
            if worst is None or (bd[lim] > worst["burdenLimit"]):
                worst = row
        print("N-A", name, "worst burden at the limit:", worst)
    json.dump(res, open(f"{OUT}/novel_A.json", "w"))

# N-B: ワンストップ over-compensation when the 特例控除 rate is 90 % (x < 0)
if which in ("all", "B"):
    res = []
    for w in range(1100000, 3000001, 10000):
        h = hh([adult(30, w)], married=False)
        lim1, c1 = furusato_scan(h, step=1000, hi=60000)
        lim2, c2 = furusato_scan(h, step=1000, hi=60000, onestop=True)
        b1, b2 = dict(c1), dict(c2)
        res.append(dict(wage=w, limitKakutei=lim1, limitOneStop=lim2, burdenK=b1[lim1], burdenO=b2[lim2],
                        minBurdenO=min(b for d, b in c2 if d >= 2000)))
    best = min(res, key=lambda r: r["minBurdenO"])
    print("N-B lowest ワンストップ burden:", best)
    print("N-B wages where ワンストップ burden at its limit < 1,900:",
          [(r["wage"], r["limitOneStop"], r["burdenO"]) for r in res if r["burdenO"] < 1900][:15])
    json.dump(res, open(f"{OUT}/novel_B.json", "w"))

# N-C: household arbitrage — who claims which child (all assignments) vs the default (top earner)
if which in ("all", "C"):
    kids_sets = {"17": [17], "20": [20], "8,5": [8, 5], "20,17,10": [20, 17, 10], "20w1M": [{"age": 20, "wages": 1000000}]}
    res = []
    for kname, kids in kids_sets.items():
        hs, meta = [], []
        for w1 in range(3000000, 15000001, 500000):
            for w2 in range(0, 6000001, 250000):
                if w2 > w1:
                    continue
                for assign in itertools.product([0, 1], repeat=len(kids)):
                    ch = []
                    for k, a in zip(kids, assign):
                        c = dict(k) if isinstance(k, dict) else {"age": k}
                        c["claimant"] = a
                        ch.append(c)
                    hs.append(hh([adult(45, w1), adult(43, w2)], children=ch))
                    meta.append((w1, w2, assign))
        out = run(hs)
        by = {}
        for (w1, w2, a), r in zip(meta, out):
            by.setdefault((w1, w2), {})[a] = r["_net"]
        gains = []
        for (w1, w2), d in by.items():
            dflt = d[tuple([0] * len(kids))]
            best_a = max(d, key=d.get)
            if d[best_a] > dflt:
                gains.append(dict(kids=kname, w1=w1, w2=w2, best=best_a, gain=d[best_a] - dflt))
        gains.sort(key=lambda g: -g["gain"])
        res += gains
        print("N-C", kname, "cases where the default is not best:", len(gains), "of", len(by), "top:", gains[:3])
    json.dump(res, open(f"{OUT}/novel_C.json", "w"))

# N-D: net income falling for one more yen (marginal > 100 %) with the new inputs
if which in ("all", "D"):
    res = []
    templates = {
        "widow": lambda w: hh([adult(55, w, widow=True)], married=False),
        "spouse_bonus200k": lambda w: hh([adult(40, 6000000), adult(38, w, bonus=200000)]),
        "student_parent_furusato": lambda w: hh([adult(50, w, furusato=60000)], married=False,
                                                 children=[{"age": 20, "wages": 1000000}]),
    }
    for name, f in templates.items():
        ws = list(range(800000, 3000001, 1000))
        out = run([f(w) for w in ws])
        falls = []
        for i in range(1, len(ws)):
            dn = out[i]["_net"] - out[i - 1]["_net"]
            if dn < -100:
                falls.append((ws[i], dn))
        falls.sort(key=lambda x: x[1])
        res.append(dict(t=name, n=len(falls), worst=falls[:5]))
        print("N-D", name, len(falls), "falls; worst:", falls[:5])
    json.dump(res, open(f"{OUT}/novel_D.json", "w"))

# N-E: medical expenses — which spouse should claim (grid)
if which in ("all", "E"):
    res = []
    for med in (120000, 200000, 400000):
        for w1 in range(3000000, 15000001, 1000000):
            for w2 in range(0, 4000001, 250000):
                if w2 > w1:
                    continue
                a, b = run([hh([adult(45, w1, medical=med), adult(43, w2)]),
                            hh([adult(45, w1), adult(43, w2, medical=med)])])
                res.append(dict(med=med, w1=w1, w2=w2, lowerBetterBy=b["_net"] - a["_net"]))
    better = [r for r in res if r["lowerBetterBy"] > 0]
    better.sort(key=lambda r: -r["lowerBetterBy"])
    print("N-E lower spouse better in", len(better), "of", len(res), "top:", better[:4])
    json.dump(res, open(f"{OUT}/novel_E.json", "w"))
