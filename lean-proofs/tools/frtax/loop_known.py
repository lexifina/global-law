"""Loophole hunt, step 1: known optimisations and anomalies, recomputed with the Lean model over grids of households,
then the same grids (or a sample of them) through Mlang.

usage: loop_known.py [items...]      writes runs/loop/known_<item>.json and runs/loop/known_examples.jsonl
Each item: a list of options per household; `gain` = burden(option 0, the default) - burden(best other option), etc.
"""
import json, os, sys, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loop_lib as L

OUT = os.path.expanduser("~/fr/runs/loop")
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
ATT = {2020: 5959, 2021: 6042, 2022: 6368, 2023: 6674, 2024: 6794, 2025: 6855}   # art. 196 B / 156 II 2°
AGE = {2020: (2448, 1224, 15340, 24690), 2021: (2484, 1242, 15560, 25040), 2022: (2620, 1310, 16410, 26400),
       2023: (2746, 1373, 17200, 27670), 2024: (2796, 1398, 17510, 28170), 2025: (2822, 1411, 17670, 28430)}
SALMAX = {2020: 12652, 2021: 12829, 2022: 13522, 2023: 14171, 2024: 14426, 2025: 14555}
SALMIN = {2020: 442, 2021: 448, 2022: 472, 2023: 495, 2024: 504, 2025: 509}


def flat10(year, s):
    return 0 if s <= 0 else min(s, max(SALMIN[year], min(SALMAX[year], (2 * 1000 * s + 10000) // 20000)))


class Grid:
    """Households, each with several options; each option = list of returns (id, year, boxes) whose burdens add."""

    def __init__(self, name):
        self.name, self.rows = name, []

    def add(self, key, options):
        self.rows.append((key, options))

    def cases(self):
        for i, (key, opts) in enumerate(self.rows):
            for j, rets in enumerate(opts):
                for k, (y, b) in enumerate(rets):
                    yield (f"{self.name}_{i}_{j}_{k}", y, b)

    def evaluate(self, res, mfun=False):
        out = []
        for i, (key, opts) in enumerate(self.rows):
            bs = []
            for j, rets in enumerate(opts):
                tot = 0
                for k, (y, b) in enumerate(rets):
                    r = res.get(f"{self.name}_{i}_{j}_{k}")
                    if r is None:
                        tot = None
                        break
                    tot += (L.m_burden(b, r) if mfun else L.burden(b, r))
                bs.append(tot)
            out.append((key, bs))
        return out


def run(grid, msample=600, seed=1):
    cs = list(grid.cases())
    lr = L.lean(cs)
    ev = grid.evaluate(lr)
    random.seed(seed)
    idx = sorted(random.sample(range(len(grid.rows)), min(msample, len(grid.rows))))
    sub = Grid(grid.name); sub.rows = [grid.rows[i] for i in idx]
    mr, ko = L.mlang(list(sub.cases()))
    mev = sub.evaluate(mr, mfun=True)
    lev = sub.evaluate(lr)  # same ids as sub? no: ids are positional; recompute Lean on sub ids
    lr2 = L.lean(list(sub.cases()))
    lev = sub.evaluate(lr2)
    agree = sum(1 for (k, a), (_, b) in zip(lev, mev) if None not in b and all(abs(x - y) < 0.5 for x, y in zip(a, b)))
    comparable = sum(1 for (_, b) in mev if None not in b)
    diffs = [(k, a, b) for (k, a), (_, b) in zip(lev, mev) if None not in b and any(abs(x - y) >= 0.5 for x, y in zip(a, b))]
    return ev, {"m_sample": len(sub.rows), "m_comparable": comparable, "m_agree": agree,
                "m_refused": collections.Counter(ko.values()).most_common(5), "m_diffs": diffs[:10]}


def summarise(ev, label_opts):
    """ev: [(key, [b0, b1, ...])]. Gain of best non-default over default (option 0)."""
    rows = []
    for key, bs in ev:
        best = min(range(1, len(bs)), key=lambda j: bs[j])
        rows.append({**key, "burden": bs, "gain_best_vs_default": bs[0] - bs[best], "best": label_opts[best]
                     if bs[best] < bs[0] else label_opts[0]})
    return rows


EXAMPLES = []


def example(item, key, opts):
    EXAMPLES.append({"item": item, "key": key, "options": [[{"year": y, "boxes": b} for y, b in o] for o in opts]})


# ---------------------------------------------------------------- K1 adult child: attach vs alimony
def k1():
    g = Grid("k1")
    for y in YEARS:
        for fam in ("couple0", "couple1", "couple2", "singleT"):
            for S in range(10000, 300001, 2000):
                n = int(fam[-1]) if fam.startswith("couple") else 0
                if fam.startswith("couple"):
                    base = L.couple(y, **{"1AJ": round(S * 0.6), "1BJ": S - round(S * 0.6)})
                else:
                    base = L.single(y, **{"0AC": 1, "1AJ": S})
                A = L.kids(dict(base), y, nf=n, nj=1)
                if fam == "singleT":
                    A["0BT"] = 1
                B = L.kids(dict(base), y, nf=n)
                B["6EL"] = ATT[y]
                if fam == "singleT":
                    B["0AL"] = 1          # art. 195, 1, a: lives alone, an adult child taxed separately
                child = L.single(y, born=y - 20, **{"1AO": ATT[y]})
                g.add({"year": y, "fam": fam, "S": S}, [[(y, A)], [(y, B), (y, child)]])
    ev, mc = run(g)
    rows = summarise(ev, ["attach", "alimony"])
    res = {"m": mc, "by": {}}
    for y in YEARS:
        for fam in ("couple0", "couple1", "couple2", "singleT"):
            rs = [r for r in rows if r["year"] == y and r["fam"] == fam]
            g_ = [r["gain_best_vs_default"] for r in rs]
            cross = next((r["S"] for r in rs if r["burden"][1] < r["burden"][0]), None)
            mx = max(rs, key=lambda r: r["burden"][0] - r["burden"][1])
            mn = min(rs, key=lambda r: r["burden"][0] - r["burden"][1])
            res["by"][f"{y}/{fam}"] = {"first_S_alimony_better": cross,
                                      "max_alimony_advantage": [mx["S"], mx["burden"][0] - mx["burden"][1]],
                                      "max_attach_advantage": [mn["S"], mn["burden"][1] - mn["burden"][0]],
                                      "at": {r["S"]: r["burden"][0] - r["burden"][1] for r in rs if r["S"] in (30000, 50000, 80000, 120000, 200000, 300000)}}
    for i, (key, opts) in enumerate(g.rows):
        if key["year"] == 2025 and key["S"] in (60000, 150000) and key["fam"] in ("couple1", "singleT"):
            example("k1", key, opts)
    return res


# ---------------------------------------------------------------- K2 PFU vs scale option (2OP)
def k2():
    g = Grid("k2")
    for y in YEARS:
        for fam in ("single", "couple"):
            for S in range(0, 200001, 2500):
                for D in (2000, 10000, 40000):
                    for mix in ("div", "div+int"):
                        b = L.single(y, **{"1AJ": S}) if fam == "single" else L.couple(y, **{"1AJ": S // 2, "1BJ": S - S // 2})
                        if b.get("1AJ") == 0:
                            b.pop("1AJ")
                        if fam == "couple" and b.get("1BJ") == 0:
                            b.pop("1BJ")
                        b["2DC"] = D
                        inv = D
                        if mix == "div+int":
                            b["2TR"] = D
                            inv += D
                        b["2BH"] = inv           # social levies withheld at source
                        A = dict(b); B = dict(b); B["2OP"] = 1
                        g.add({"year": y, "fam": fam, "S": S, "D": D, "mix": mix}, [[(y, A)], [(y, B)]])
    ev, mc = run(g)
    rows = summarise(ev, ["PFU", "scale"])
    res = {"m": mc, "by": {}}
    for y in YEARS:
        for fam in ("single", "couple"):
            for D in (2000, 10000, 40000):
                for mix in ("div", "div+int"):
                    rs = [r for r in rows if (r["year"], r["fam"], r["D"], r["mix"]) == (y, fam, D, mix)]
                    better = [r["S"] for r in rs if r["burden"][1] < r["burden"][0]]
                    mx = max(rs, key=lambda r: r["burden"][0] - r["burden"][1])
                    mn = min(rs, key=lambda r: r["burden"][0] - r["burden"][1])
                    res["by"][f"{y}/{fam}/D{D}/{mix}"] = {
                        "scale_better_S_range": [min(better), max(better)] if better else None,
                        "n_scale_better": len(better), "n": len(rs),
                        "max_scale_saving": [mx["S"], mx["burden"][0] - mx["burden"][1]],
                        "max_scale_cost": [mn["S"], mn["burden"][1] - mn["burden"][0]]}
    for key, opts in g.rows:
        if key["year"] == 2025 and key["fam"] == "single" and key["D"] == 10000 and key["mix"] == "div" and key["S"] in (15000, 60000):
            example("k2", key, opts)
    return res


# ---------------------------------------------------------------- K3 actual expenses vs 10 % (with union dues)
def k3():
    g = Grid("k3")
    for y in YEARS:
        for S in range(15000, 150001, 5000):
            U = (S + 50) // 100        # union dues at 1 % of salary
            f = flat10(y, S)
            for delta in (0, 50, 100, 200, 400, 800, 1600):
                b = L.single(y, **{"1AJ": S, "7AC": U})
                A = dict(b)
                B = dict(b); B["1AK"] = f + delta + U      # actual expenses, the union dues among them
                g.add({"year": y, "S": S, "delta": delta, "U": U}, [[(y, A)], [(y, B)]])
    ev, mc = run(g)
    rows = summarise(ev, ["flat+credit", "actual"])
    res = {"m": mc, "by": {}}
    for y in YEARS:
        for delta in (0, 50, 100, 200, 400, 800, 1600):
            rs = [r for r in rows if r["year"] == y and r["delta"] == delta]
            worse = [r for r in rs if r["burden"][1] > r["burden"][0]]
            res["by"][f"{y}/delta{delta}"] = {"n_actual_costs_more": len(worse), "n": len(rs),
                                             "max_cost": max((r["burden"][1] - r["burden"][0], r["S"]) for r in rs)}
    for key, opts in g.rows:
        if key["year"] == 2025 and key["S"] == 40000 and key["delta"] == 200:
            example("k3", key, opts)
    return res


# ---------------------------------------------------------------- K4 marriage / PACS vs two singles
def k4():
    g = Grid("k4")
    for y in (2024, 2025):
        for kind in ("work", "retired"):
            born = 1980 if kind == "work" else 1950
            box1, box2 = ("1AJ", "1BJ") if kind == "work" else ("1AS", "1BS")
            for nk in ((0, 2) if kind == "work" else (0,)):
                for a in range(0, 150001, 2500):
                    for b_ in range(0, a + 1, 2500):
                        if a == 0:
                            continue
                        C = L.couple(y, born, born, **{box1: a})
                        if b_:
                            C[box2] = b_
                        L.kids(C, y, nf=nk)
                        s1 = L.single(y, born, **{"1AJ" if kind == "work" else "1AS": a})
                        s2 = L.single(y, born, **({"1AJ" if kind == "work" else "1AS": b_} if b_ else {}))
                        opts = [[(y, C)]]
                        if nk == 0:
                            opts.append([(y, s1), (y, s2)])
                        else:
                            opts.append([(y, L.kids(dict(s1), y, nf=2)), (y, s2)])
                            opts.append([(y, s1), (y, L.kids(dict(s2), y, nf=2))])
                            opts.append([(y, L.kids(dict(s1), y, nf=1)), (y, L.kids(dict(s2), y, nf=1, ages=(12,)))])
                        g.add({"year": y, "kind": kind, "kids": nk, "a": a, "b": b_}, opts)
    ev, mc = run(g, msample=800)
    res = {"m": mc, "by": {}}
    for y in (2024, 2025):
        for kind, nk in (("work", 0), ("work", 2), ("retired", 0)):
            rs = [(k, bs) for k, bs in ev if (k["year"], k["kind"], k["kids"]) == (y, kind, nk)]
            gains = [(min(bs[1:]) - bs[0], k["a"], k["b"]) for k, bs in rs]   # >0: marriage bonus
            pen = [x for x in gains if x[0] < 0]
            res["by"][f"{y}/{kind}/kids{nk}"] = {"n": len(gains), "n_penalty": len(pen),
                                                "max_bonus": max(gains), "max_penalty": min(gains),
                                                "penalty_examples": sorted(pen)[:5]}
    for key, opts in g.rows:
        if key["year"] == 2025 and ((key["kind"], key["kids"], key["a"], key["b"]) in
                                    (("retired", 0, 17500, 17500), ("work", 0, 20000, 20000), ("work", 0, 100000, 0))):
            example("k4", key, opts)
    return res


# ---------------------------------------------------------------- K5 separated parents, two children
def k5():
    g = Grid("k5")
    for y in (2024, 2025):
        for a in range(10000, 200001, 5000):
            for b_ in range(0, a + 1, 5000):
                def p(inc, **kw):
                    d = L.single(y, **{"0AD": 1}); d.pop("0AC")
                    if inc:
                        d["1AJ"] = inc
                    d.update(kw)
                    return d
                opts = [
                    # 0 shared residence, both children (0CH) and box T on both returns
                    [(y, L.kids(p(a, **{"0BT": 1}), y, nh=2)), (y, L.kids(p(b_, **{"0BT": 1}), y, nh=2))],
                    # 1 both children with the higher earner A
                    [(y, L.kids(p(a, **{"0BT": 1}), y, nf=2)), (y, p(b_))],
                    # 2 both with B
                    [(y, p(a)), (y, L.kids(p(b_, **{"0BT": 1}), y, nf=2))],
                    # 3 one each
                    [(y, L.kids(p(a, **{"0BT": 1}), y, nf=1)), (y, L.kids(p(b_, **{"0BT": 1}), y, nf=1, ages=(12,)))],
                ]
                # 4-6 both with B, A pays child support Y (deducted 6GU; received 1AO)
                for Y in (3000, 6000, 12000):
                    opts.append([(y, p(a, **{"6GU": Y})), (y, L.kids(p(b_, **{"0BT": 1, "1AO": Y}), y, nf=2))])
                g.add({"year": y, "a": a, "b": b_}, opts)
    ev, mc = run(g, msample=500)
    labels = ["shared", "both_A", "both_B", "one_each", "B+3000", "B+6000", "B+12000"]
    res = {"m": mc, "by": {}}
    for y in (2024, 2025):
        rs = [(k, bs) for k, bs in ev if k["year"] == y]
        cnt = collections.Counter(labels[min(range(len(bs)), key=lambda j: bs[j])] for k, bs in rs)
        cnt_nosupport = collections.Counter(labels[min(range(4), key=lambda j: bs[j])] for k, bs in rs)
        best = max(rs, key=lambda kb: kb[1][0] - min(kb[1]))
        best4 = max(rs, key=lambda kb: kb[1][0] - min(kb[1][:4]))
        res["by"][y] = {"best_option_counts": dict(cnt), "best_without_support": dict(cnt_nosupport),
                        "max_gain_vs_shared": [best[0], best[1][0] - min(best[1]), labels[min(range(len(best[1])), key=lambda j: best[1][j])]],
                        "max_gain_vs_shared_no_support": [best4[0], best4[1][0] - min(best4[1][:4])],
                        "at": {f"{k['a']}/{k['b']}": dict(zip(labels, bs)) for k, bs in rs
                               if (k["a"], k["b"]) in ((40000, 20000), (80000, 30000), (150000, 30000), (60000, 60000))}}
    for key, opts in g.rows:
        if key["year"] == 2025 and (key["a"], key["b"]) in ((80000, 30000),):
            example("k5", key, opts)
    return res


# ---------------------------------------------------------------- K6/K7 value of half parts, T, L, and the QF cap
def k67():
    g = Grid("k67")
    for y in (2024, 2025):
        for S in range(10000, 300001, 1000):
            s = lambda **kw: L.single(y, **{"1AJ": S, **kw})
            c = lambda **kw: L.couple(y, **{"1AJ": S // 2, "1BJ": S - S // 2, **kw})
            g.add({"year": y, "S": S, "what": "T_with_child"}, [[(y, L.kids(s(), y, nf=1))], [(y, L.kids(s(**{"0BT": 1}), y, nf=1))]])
            g.add({"year": y, "S": S, "what": "L"}, [[(y, s())], [(y, s(**{"0AL": 1}))]])
            g.add({"year": y, "S": S, "what": "widow_child"}, [[(y, L.kids(s(**{"0BT": 1}), y, nf=1))],
                                                             [(y, L.kids({**{k: v for k, v in s().items() if k != "0AC"}, "0AV": 1}, y, nf=1))]])
            for n in (1, 2, 3):
                g.add({"year": y, "S": S, "what": f"couple_child{n}"}, [[(y, L.kids(c(), y, nf=n - 1))], [(y, L.kids(c(), y, nf=n))]])
            g.add({"year": y, "S": S, "what": "shared_child1_T"}, [[(y, s())], [(y, L.kids(s(**{"0BT": 1}), y, nh=1))]])
            g.add({"year": y, "S": S, "what": "disabled_P_single"}, [[(y, s())], [(y, s(**{"0AP": 1}))]])
    ev, mc = run(g, msample=400)
    res = {"m": mc, "by": {}}
    for y in (2024, 2025):
        for what in sorted({k["what"] for k, _ in ev}):
            rs = [(k["S"], bs[0] - bs[1]) for k, bs in ev if k["year"] == y and k["what"] == what]
            mx = max(v for _, v in rs)
            first_max = next(S for S, v in rs if v == mx)
            res["by"][f"{y}/{what}"] = {"max_value": mx, "first_salary_at_max": first_max,
                                       "at": {S: v for S, v in rs if S in (20000, 30000, 50000, 80000, 120000, 200000)}}
    return res


# ---------------------------------------------------------------- K12 gifts and the 61 € threshold; K13 home help
def k1213():
    g = Grid("k12")
    for y in YEARS:
        for S in range(15000, 60001, 100):
            b = L.single(y, **{"1AJ": S})
            opts = [[(y, b)]]
            for G in (2, 10, 50, 100, 200, 300):
                opts.append([(y, {**b, "7UD": G})])        # aid organisations, 75 %
            for G in (2, 10, 50, 100, 200, 300):
                opts.append([(y, {**b, "7UF": G})])        # other gifts, 66 %
            opts.append([(y, {**b, "7DB": 2000})])         # home help 2 000 €
            g.add({"year": y, "S": S}, opts)
    ev, mc = run(g, msample=400)
    gifts = [("7UD", G) for G in (2, 10, 50, 100, 200, 300)] + [("7UF", G) for G in (2, 10, 50, 100, 200, 300)]
    res = {"m": mc, "by": {}}
    for y in YEARS:
        rs = [(k, bs) for k, bs in ev if k["year"] == y]
        # net cost of a gift G = G - (burden without - burden with); negative = the gift pays the giver
        best = []
        for k, bs in rs:
            for j, (box, G) in enumerate(gifts, start=1):
                saving = bs[0] - bs[j]
                best.append((G - saving, k["S"], box, G, bs[0], bs[j]))
        neg = [x for x in best if x[0] < 0]
        hh = [(bs[0] - bs[-1], k["S"], bs[0]) for k, bs in rs]
        res["by"][y] = {"n_gift_options_net_negative_cost": len(neg), "n": len(best),
                        "most_negative": sorted(neg)[:5],
                        "salary_range_negative": [min(x[1] for x in neg), max(x[1] for x in neg)] if neg else None,
                        "home_help_2000_saving_min_max": [min(hh), max(hh)]}
    for key, opts in g.rows:
        if key["year"] == 2025 and key["S"] in (21500,):
            example("k12", key, [opts[0], opts[1], opts[3]])
    return res


# ---------------------------------------------------------------- K14 micro regimes: flat levy (VL) vs ordinary micro
def k14():
    g = Grid("k14")
    for y in YEARS:
        for S in range(0, 150001, 5000):
            for T in (10000, 30000, 60000):
                for cat, (vl, mi) in {"services": ("5TB", "5KP"), "bnc": ("5TE", "5HQ"), "sales": ("5TA", "5KO")}.items():
                    b = L.single(y, **({"1AJ": S} if S else {}))
                    g.add({"year": y, "S": S, "T": T, "cat": cat}, [[(y, {**b, mi: T})], [(y, {**b, vl: T})]])
    ev, mc = run(g, msample=500)
    rows = summarise(ev, ["ordinary micro", "flat levy"])
    res = {"m": mc, "by": {}}
    for y in YEARS:
        for cat in ("services", "bnc", "sales"):
            for T in (10000, 30000, 60000):
                rs = [r for r in rows if (r["year"], r["cat"], r["T"]) == (y, cat, T)]
                vl_better = [r["S"] for r in rs if r["burden"][1] < r["burden"][0]]
                mx = max(rs, key=lambda r: r["burden"][0] - r["burden"][1])
                mn = min(rs, key=lambda r: r["burden"][0] - r["burden"][1])
                res["by"][f"{y}/{cat}/T{T}"] = {"vl_better_from_S": min(vl_better) if vl_better else None,
                                               "max_vl_saving": [mx["S"], mx["burden"][0] - mx["burden"][1]],
                                               "max_vl_cost": [mn["S"], mn["burden"][1] - mn["burden"][0]]}
    return res


ITEMS = {"k1": k1, "k2": k2, "k3": k3, "k4": k4, "k5": k5, "k67": k67, "k1213": k1213, "k14": k14}

if __name__ == "__main__":
    which = sys.argv[1:] or list(ITEMS)
    for it in which:
        r = ITEMS[it]()
        json.dump(r, open(f"{OUT}/known_{it}.json", "w"), indent=1, default=str)
        print(it, "done", json.dumps(r.get("m"), default=str)[:300], flush=True)
    with open(f"{OUT}/known_examples_{'_'.join(which)}.jsonl", "w") as f:
        for e in EXAMPLES:
            f.write(json.dumps(e) + "\n")
