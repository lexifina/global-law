"""Blind search over the moves a family controls, scored by after-tax family wealth at the parents' death.

    python tools/taxcode/loopholes/family_search.py [rounds] [procs]

The move set is listed in `moves()`; each move is one thing families and their advisers choose (an amount, in a window
of years). Amounts and windows are "natural" values the position offers: bracket and band edges of the rate tables,
the annual gift exclusion, a child's wage cap, a child's standard deduction, round amounts. They are not values picked
with a plan in mind, and nothing here names or targets a strategy: the score is the only judge.

Search: (1) every single move against doing nothing; (2) greedy forward selection: add the best move, re-try every
move on top, repeat; (3) every pair of the strongest single moves, to measure interaction (pair minus both singles).
Writes DATA/singles.json, DATA/greedy.json, DATA/pairs.json.
"""
import copy, itertools, json, sys, time
from family_lib import FAMILIES, DATA, blank_plan, run

# natural taxable-income targets for a joint return (2025): tops of the 10/12/22/24/32/35% rows; top of the 0% and
# 15% capital-gain bands; and the §1411 threshold (which is MAGI, used as a target anyway)
TI_JOINT = [23850, 96700, 96950, 206700, 250000, 394600, 501050, 600050, 751600]
TI_SINGLE = [15750, 48350, 48475, 103350]       # a child's: standard deduction, 0% band, 12% row top, 22% row top
TI_TRUST = [3150, 3250, 11450, 15650, 15900]    # §1(e) rows and §1(h) bands for a trust
AMTS = [10000, 25000, 50000, 100000, 200000]
GIFT_LUMPS = [100000, 250000, 500000, 1000000, 2000000]
TRUST_FUND = [250000, 1000000, 3000000]


def events(s):
    """Years at which something in the family changes (ages of parents and children)."""
    H = s["horizon"]; h = s["head"]; ev = {0, H}
    for a in (h["retireAge"], 65, h["ssAge"], h["rmdAge"]):
        y = a - h["age"]
        if 0 < y < H: ev.add(y)
    for k in s["kids"]:
        for a in (18, 19, k["studentThrough"] + 1, 24):
            y = a - k["age"]
            if 0 < y < H: ev.add(y)
    return sorted(ev)


def windows(s):
    ev = events(s)
    w = set()
    for i in range(len(ev) - 1):
        w.add((ev[i], ev[i + 1]))
        if i + 2 < len(ev): w.add((ev[i], ev[i + 2]))
    w.add((0, s["horizon"]))
    return sorted(w)


def moves(s):
    W = windows(s); out = []
    for (a, b) in W:
        for t in TI_JOINT: out.append(("convTo", a, b, t))
        for x in AMTS: out.append(("convAmt", a, b, x))
        for t in TI_JOINT: out.append(("harvestTo", a, b, t))
        out.append(("giftAnnual", a, b, 38000))
        out.append(("mfs", a, b, 1))
        out.append(("form8814", a, b, 1))
        for t in TI_SINGLE: out.append(("kidHarvestTo", a, b, t))
        if s["business"] > 0:
            for x in (7000, 15750, 99999999):           # Roth limit, child's standard deduction, the reasonable cap
                for roth in (0, 1): out.append(("kidWage", a, b, x, roth))
    for (a, _) in W:
        for x in GIFT_LUMPS: out.append(("giftLump", a, a + 1, x))
    for x in TRUST_FUND:
        for when in ("never", "always", "adult19", "adult24"):
            for bp in (5000, 10000):
                if when == "never" and bp != 10000: continue
                for th in [0] + TI_TRUST:
                    for dni in (0, 1):
                        out.append(("trust", 0, 1, x, when, bp, th, dni))
    for k in (2, 3, 5):
        for sh in (0, 1): out.append(("bunch", 0, s["horizon"], k, sh))
    out.append(("bunch", 0, s["horizon"], 1, 1))
    seen, uniq = set(), []
    for m in out:
        if tuple(m) not in seen: seen.add(tuple(m)); uniq.append(tuple(m))
    return uniq


def apply(s, plan, m):
    kind = m[0]; a, b = m[1], m[2]; n = len(s["kids"]); H = s["horizon"]
    if kind == "trust":
        _, _, _, x, when, bp, th, dni = m
        plan[0]["trustFund"] = x
        for y in range(H):
            ages = [k["age"] + y for k in s["kids"]]
            ok = [when == "always" or (when == "adult19" and g >= 19) or (when == "adult24" and g >= 24) for g in ages]
            plan[y]["trustDistBp"] = [bp if o else 0 for o in ok]
            plan[y]["trustHarvestTo"] = th
        return "dni" if dni else None
    if kind == "bunch":
        k, sh = m[3], m[4]
        for y in range(H):
            plan[y]["charity"] = s["charity"] * k if y % k == 0 else 0
            plan[y]["charityShares"] = bool(sh)
        return None
    for y in range(a, min(b, H)):
        p = plan[y]
        if kind == "convTo": p["convTo"] = m[3]; p["convH"] = p["convS"] = 0
        elif kind == "convAmt": p["convH"] = m[3] // 2; p["convS"] = m[3] - m[3] // 2; p["convTo"] = 0
        elif kind == "harvestTo": p["harvestTo"] = m[3]
        elif kind == "giftAnnual": p["gifts"] = [m[3]] * n
        elif kind == "giftLump": p["gifts"] = [m[3] // n] * n
        elif kind == "mfs": p["mfs"] = True
        elif kind == "form8814": p["form8814"] = [True] * n
        elif kind == "kidHarvestTo": p["kidHarvestTo"] = [m[3]] * n
        elif kind == "kidWage": p["kidWage"] = [m[3]] * n; p["kidRoth"] = [bool(m[4])] * n
    return None


def build(fam, ms):
    s = FAMILIES[fam]; plan = blank_plan(s); name = fam
    for m in ms:
        if apply(s, plan, m) == "dni": name = fam + "+dni"
    return name, plan


def specs():
    d = dict(FAMILIES)
    for k, v in FAMILIES.items():
        v2 = dict(v); v2["gainsInDni"] = True; d[k + "+dni"] = v2
    return d


def lever(m):
    return {"giftAnnual": "gift", "giftLump": "gift", "convAmt": "conv", "convTo": "conv"}.get(m[0], m[0])


def evaluate(fam_moves, procs, tag):
    jobs = [build(f, ms) + (False,) for f, ms in fam_moves]
    return run(specs(), jobs, procs=procs, tag=tag)


def main():
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    DATA.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    base = {f: o for f, o in zip(FAMILIES, evaluate([(f, []) for f in FAMILIES], procs, "base"))}
    print({f: base[f]["wealth"] for f in base})
    # 1. singles
    todo = [(f, [m]) for f in FAMILIES for m in moves(FAMILIES[f])]
    print(f"{len(todo)} single moves"); sys.stdout.flush()
    res = evaluate(todo, procs, "single")
    singles = [{"family": f, "move": ms[0], "gain": o["wealth"] - base[f]["wealth"],
                "taxPaid": o["taxPaid"] - base[f]["taxPaid"], "estateTax": o["estateTax"] - base[f]["estateTax"],
                "latent": o["kidsLatentTax"] - base[f]["kidsLatentTax"]} for (f, ms), o in zip(todo, res)]
    json.dump({"base": base, "singles": singles}, open(DATA / "singles.json", "w"))
    print(f"singles done {time.time() - t0:.0f}s"); sys.stdout.flush()
    # 2. greedy
    greedy = {}
    for f in FAMILIES:
        cur, curW, path = [], base[f]["wealth"], []
        # moves that alone cost more than 1% of the family's wealth are not re-tried on top (they stay in the singles)
        keep = {tuple(x["move"]) for x in singles if x["family"] == f and x["gain"] > -base[f]["wealth"] // 100}
        for r in range(rounds):
            cand = [(f, cur + [m]) for m in moves(FAMILIES[f]) if m not in cur and m in keep]
            out = evaluate(cand, procs, f"greedy_{f}_{r}")
            best = max(range(len(cand)), key=lambda i: out[i]["wealth"])
            if out[best]["wealth"] - curW < 1000: break
            cur = cand[best][1]
            path.append({"move": cur[-1], "wealth": out[best]["wealth"], "step": out[best]["wealth"] - curW})
            curW = out[best]["wealth"]
            print(f, r, cur[-1], curW - base[f]["wealth"]); sys.stdout.flush()
        greedy[f] = {"moves": cur, "path": path, "gain": curW - base[f]["wealth"]}
        json.dump(greedy, open(DATA / "greedy.json", "w"))
    # 3. pairs of the strongest singles (best per lever-and-window, top 30 per family)
    pairs = []
    for f in FAMILIES:
        ss = sorted([x for x in singles if x["family"] == f], key=lambda x: -x["gain"])
        top, seen = [], set()
        for x in ss:
            key = (lever(x["move"]), x["move"][1], x["move"][2])
            if key in seen or x["gain"] <= 0: continue
            seen.add(key); top.append(x)
            if len(top) == 30: break
        cand = [(f, [a["move"], b["move"]]) for a, b in itertools.combinations(top, 2)]
        if not cand: continue
        out = evaluate(cand, procs, f"pairs_{f}")
        g = {tuple(x["move"]): x["gain"] for x in top}
        for (ff, ms), o in zip(cand, out):
            pg = o["wealth"] - base[f]["wealth"]
            pairs.append({"family": f, "moves": ms, "gain": pg, "synergy": pg - g[tuple(ms[0])] - g[tuple(ms[1])]})
    json.dump(pairs, open(DATA / "pairs.json", "w"))
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()


def load_greedy():
    return json.load(open(DATA / "greedy.json"))
