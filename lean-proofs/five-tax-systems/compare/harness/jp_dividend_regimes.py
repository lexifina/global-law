"""Japan: what an extra 10 % of AW of listed-share dividends costs a single wage earner under each of the three ways
the law offers (JP FINDINGS F16): final withholding (措置法第8条の5, the model's default), declared separately
(第8条の4) or taxed with the rest of income with the 配当控除 (所得税法第92条). Wages 0.2 to 2.5 AW in steps of 0.05.

    python3 jp_dividend_regimes.py  -> charts/jp_dividend_regimes.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import AW, EXES, ROOT, adult, gross, household, net, run_exe  # noqa: E402

REGIMES = ["separate", "declared", "aggregate"]


def main():
    cmd, cwd = EXES["JP"]
    aw = AW["JP"]
    d = round(0.1 * aw)
    levels = [round(0.05 * i, 2) for i in range(4, 51)]
    hs = []
    for lv in levels:
        hs.append(household(f"b{lv}", [adult(wages=lv * aw)]))
        for e in REGIMES:
            h = household(f"{e}{lv}", [adult(wages=lv * aw)], dividends=d)
            h["jpDividends"] = e
            hs.append(h)
    outs, _ = run_exe(cmd, cwd, hs)
    O = {h["id"]: (h, o) for h, o in zip(hs, outs)}

    def taxes(i):
        h, o = O[i]
        return gross(h) - net(o, gross(h))
    rows = []
    for lv in levels:
        b = taxes(f"b{lv}")
        r = {e: round((taxes(f"{e}{lv}") - b) / d, 4) for e in REGIMES}
        rows.append({"wages_aw": lv, "marginal_rate": r, "cheapest": min(r, key=r.get)})
    agg = [r["wages_aw"] for r in rows if r["cheapest"] == "aggregate"]
    switch = max(agg) if agg else None  # above this, the flat 20.315 % (withheld, or declared at the same rate) is cheapest
    res = {"title": "Japan: the rate on an extra 10 % of AW of listed dividends for a single wage earner, by regime",
           "regimes": {"separate": "final withholding 15.315 % + 5 % (措置法第8条の5; the model's default)",
                       "declared": "declared, taxed separately (措置法第8条の4)",
                       "aggregate": "taxed with other income, with the 配当控除 (所得税法第92条; 地方税法附則第5条)"},
           "extra_dividends_yen": d, "aw_yen": aw, "rows": rows, "aggregation_cheapest_up_to_aw": switch,
           "note": "above that level the flat rate is cheapest; declaring separately and withholding then differ by "
                   "rounding only (0.01 point)", "exe": cmd[0]}
    json.dump(res, open(os.path.join(ROOT, "charts", "jp_dividend_regimes.json"), "w"), indent=1, ensure_ascii=False)
    print("aggregation cheapest up to", switch, "AW")


if __name__ == "__main__":
    main()
