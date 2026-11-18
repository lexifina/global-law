"""Germany at one-euro resolution: how often, and by how much, one more euro of wages lowers a single employee's net
income because § 32a (1) Satz 6 EStG rounds the tax down to the euro (the €10 scan in analyses.py cannot see this).

    python3 de_euro_dips.py [lo hi]   (default 12,000 to 120,000 euros of wages) -> charts/de_euro_dips.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EXES, ROOT, adult, gross, household, net, run_exe  # noqa: E402


def main(lo=12000, hi=120000):
    cmd, cwd = EXES["DE"]
    hs = [household(f"w{w}", [adult(wages=w)]) for w in range(lo, hi + 1)]
    outs, dt = run_exe(cmd, cwd, hs)
    nets = [net(o, gross(h)) for h, o in zip(hs, outs)]
    dips = [(lo + i + 1, round(nets[i + 1] - nets[i], 2)) for i in range(len(nets) - 1) if nets[i + 1] < nets[i] - 1e-9]
    worst = min(dips, key=lambda x: x[1]) if dips else None
    res = {"title": "Germany, single employee, wages in one-euro steps: falls in net income for one more euro",
           "range": [lo, hi], "steps": len(nets) - 1, "falls": len(dips),
           "share_of_steps": round(len(dips) / (len(nets) - 1), 4), "worst": worst,
           "falls_by_size": {k: sum(1 for _, d in dips if -k - 0.05 < d <= -k + 0.05) for k in (0.1, 0.2, 0.3)},
           "first_falls": dips[:20], "exe": cmd[0], "seconds": round(dt, 1)}
    json.dump(res, open(os.path.join(ROOT, "charts", "de_euro_dips.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("first_falls",)}))


if __name__ == "__main__":
    a = [int(x) for x in sys.argv[1:3]]
    main(*a) if a else main()
