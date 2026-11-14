"""Second stage: greedy refinement of the grid search's best plans with moves the grid leaves out.

    python tools/taxcode/loopholes/entity_greedy.py [rounds] [procs]

From the best plan of each scenario and exit (DATA/search.json), try one more move of each kind — a further change of
form at any natural year, a further gift (any size, either donee, any natural year), a different wage or payout — and
keep the best; repeat. Writes DATA/greedy.json.
"""
import copy, json, sys
from entity_lib import SCENARIOS, DATA, run
from entity_search import switch_years, salaries

def extra_moves(s, p):
    H = s["horizon"]; out = []
    last = p["forms"][-1][0] if p["forms"] else 0
    cur = p["forms"][-1][1] if p["forms"] else "u"
    for k in switch_years(H):
        if k > last:
            for f in "usc":
                if f != cur:
                    q = copy.deepcopy(p); q["forms"] = (q["forms"] or [[0, "u"]]) + [[k, f]]; out.append(q)
    years = sorted({0, 1, 2, 3, H // 2, H - 5, H - 3, H - 1} | {f[0] for f in p["forms"]})
    for gy in years:
        for bp in (1000, 2500, 5000, 9000):
            for tt in (False, True):
                q = copy.deepcopy(p); q["gifts"] = q["gifts"] + [dict(year=gy, bp=bp, toTrusts=tt)]; out.append(q)
    for sal in salaries(s["biz"]):
        if sal != p["salary"]:
            q = copy.deepcopy(p); q["salary"] = sal; out.append(q)
    for pay in (0, 2500, 5000, 7500, 10000):
        if pay != p["payoutBp"]:
            q = copy.deepcopy(p); q["payoutBp"] = pay; out.append(q)
    return out

def main():
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    keep = json.load(open(DATA / "search.json"))
    summ = json.load(open(DATA / "search_summary.json"))
    res = {}
    for key, rows in keep.items():
        name, ex = key.split("/")
        s = SCENARIOS[name]; base = summ[name]["base"][ex]["wealth"]
        cur = rows[0]["plan"]; curW = rows[0]["wealth"]; path = []
        for r in range(rounds):
            cands = extra_moves(s, cur)
            outs = run(SCENARIOS, [(name, c, False) for c in cands], procs=procs, tag=f"g_{name}_{ex}_{r}")
            i = max(range(len(cands)), key=lambda j: outs[j]["wealth"])
            if outs[i]["wealth"] - curW < 1000: break
            path.append({"plan": cands[i], "step": outs[i]["wealth"] - curW})
            cur, curW = cands[i], outs[i]["wealth"]
            print(key, r, outs[i]["wealth"] - base, cur); sys.stdout.flush()
        res[key] = {"plan": cur, "gain": curW - base, "gridGain": rows[0]["gain"], "path": path}
        json.dump(res, open(DATA / "greedy.json", "w"), indent=1)

if __name__ == "__main__":
    main()
