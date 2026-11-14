"""Blind search over the choices an owner family and its advisers control, scored by after-tax family wealth at the
parents' death (Entity/Driver.lean; every figure computed by Lean).

    python tools/taxcode/loopholes/entity_search.py [procs]

Choices (the product of all of them, de-duplicated where a choice cannot matter):
  * the form at the start (u / s / c) and at most one change of form, to any other form, at a year that is a natural
    edge: 1, 2, 3 years in, the middle, and 1-5 years before the horizon (holding periods count back from the exit);
  * the owner's wage in corporate years: 0, the reasonable-compensation band's ends and middle, the 2025 Social
    Security wage base, or everything (the driver clamps it to the band the law allows for the form);
  * a C corporation's payout: none, half, all of its after-tax income;
  * a gift of equity to the children or to trusts for them: none, or 25 / 50 / 90 percent of the parents' part at the
    start, at the change of form, or 3 years before the horizon;
  * the exit: a sale of interests or stock, a sale of assets, or holding until death.
Nothing here names or aims at a strategy: the score is the only judge. Results: DATA/search.json (the best 3,000 per
scenario and exit, every plan's lever values) and DATA/search_summary.json. With the argument `nogift`, only plans
without a gift (the entity choices alone): DATA/search_nogift.json.
"""
import itertools, json, sys, time
from entity_lib import SCENARIOS, DATA, plan, run

WAGE_BASE = 176100


def switch_years(H):
    return sorted({1, 2, 3, H // 2} | {H - d for d in range(1, 6)} - {0})


def paths(H):
    out = [((0, f),) for f in "usc"]
    for f0 in "usc":
        for f1 in "usc":
            if f1 == f0: continue
            for k in switch_years(H):
                if 0 < k < H: out.append(((0, f0), (k, f1)))
    return out


def salaries(b):
    return sorted({0, b["rcLo"], (b["rcLo"] + b["rcHi"]) // 2, b["rcHi"], WAGE_BASE, 10 ** 9})


def effective_salary(forms, sal, b):
    """What the driver will pay in S and C years (for de-duplication only)."""
    fs = {f for _, f in forms}
    return (max(b["rcLo"], sal) if "s" in fs else None, min(b["rcHi"], sal) if "c" in fs else None)


NOGIFT = "nogift" in sys.argv
ONLY = [a[5:] for a in sys.argv if a.startswith("only=")]


def candidates(name):
    s = SCENARIOS[name]; H = s["horizon"]; b = s["biz"]
    seen, out = set(), []
    for forms in paths(H):
        fs = {f for _, f in forms}
        k = forms[1][0] if len(forms) > 1 else 0
        gift_opts = [None] + ([] if NOGIFT else
                               [(gy, bp, tt) for gy in sorted({0, k, H - 3}) for bp in (2500, 5000, 9000) for tt in (False, True)])
        for sal in salaries(b):
            es = effective_salary(forms, sal, b)
            for pay in ((0, 5000, 10000) if "c" in fs else (10000,)):
                for g in gift_opts:
                    key = (forms, es, pay, g)
                    if key in seen: continue
                    seen.add(key)
                    out.append(dict(forms=[list(f) for f in forms], salary=sal, payoutBp=pay,
                                    gifts=[] if g is None else [dict(year=g[0], bp=g[1], toTrusts=g[2])]))
    return out


def main():
    procs = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 10
    out = ("search_nogift" if NOGIFT else "search") + ("_" + "_".join(ONLY) if ONLY else "")
    t0 = time.time()
    summary, keep = {}, {}
    for name in (ONLY or SCENARIOS):
        cands = candidates(name)
        jobs = [(name, dict(c, exit=ex), False) for c in cands for ex in ("sale", "assetSale", "death")]
        print(name, len(jobs), "plans"); sys.stdout.flush()
        res = run(SCENARIOS, jobs, procs=procs, tag=f"s_{name}")
        base = {}
        for (n, p, _), o in zip(jobs, res):
            if p["forms"] == [[0, "u"]] and not p["gifts"] and p["salary"] == 0:
                base[p["exit"]] = o
        rows = []
        for (n, p, _), o in zip(jobs, res):
            b = base[p["exit"]]
            rows.append(dict(plan=p, wealth=o["wealth"], gain=o["wealth"] - b["wealth"],
                             estateTax=o["estateTax"] - b["estateTax"], exitTax=o["exitTax"] - b["exitTax"],
                             taxPaid=o["taxPaid"] - b["taxPaid"], corpTax=o["corpTaxPaid"], payroll=o["payroll"] - b["payroll"],
                             latent=o["kidsLatent"] - b["kidsLatent"], qsbs=o["qsbsExcluded"], finalForm=o["finalForm"]))
        summary[name] = {"base": {ex: {k: v for k, v in b.items() if k != "log"} for ex, b in base.items()},
                         "plans": len(jobs), "seconds": round(time.time() - t0)}
        for ex in ("sale", "assetSale", "death"):
            rr = sorted([r for r in rows if r["plan"]["exit"] == ex], key=lambda r: -r["gain"])
            keep[f"{name}/{ex}"] = rr[:3000]
            summary[name][ex] = {"best": rr[0]["gain"], "worst": rr[-1]["gain"], "n": len(rr)}
            print(name, ex, "best", rr[0]["gain"], rr[0]["plan"]); sys.stdout.flush()
        json.dump(keep, open(DATA / f"{out}.json", "w"))
        json.dump(summary, open(DATA / f"{out}_summary.json", "w"), indent=1)
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
