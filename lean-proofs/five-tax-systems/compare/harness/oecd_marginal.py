"""The OECD's marginal rates (net personal marginal tax rate of the principal earner, Taxing Wages 2026, 2025) against
the five models: the principal's gross pay raised by 1 % of AW and by 10 % of AW.

    python3 oecd_marginal.py -> charts/oecd_marginal_check.json

The OECD's rate includes what the models leave out: US state and local tax (Michigan 4.25 % + Detroit 2.4 % on pay,
identified in RESULTS.md, so 6.65 points; for the single parent also Michigan's EIC, 30 % of the federal one) and the
withdrawal of means-tested benefits (UK Universal Credit, French prime d'activité, Japan's 児童扶養手当 for the single
parent). The US column adds the 6.65 points (and for SP67 30 % of the federal EIC phase-out rate, 21.06 %).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import AW, COUNTRIES, ROOT, adult, household  # noqa: E402
import run as runner  # noqa: E402
from scenarios import CHILD_AGES  # noqa: E402

OECD = json.load(open(os.path.join(ROOT, "data", "oecd", "tw_marginal_2025.json")))
ISO3 = {"US": "USA", "FR": "FRA", "UK": "GBR", "DE": "DEU", "JP": "JPN"}
TYPES = {"S67": (1, False, (), 0.67, 0.0), "S100": (1, False, (), 1.00, 0.0), "S167": (1, False, (), 1.67, 0.0),
         "SP67": (1, False, CHILD_AGES, 0.67, 0.0), "M100_0": (2, True, CHILD_AGES, 1.00, 0.0),
         "M100_100": (2, True, CHILD_AGES, 1.00, 1.00), "M100_67": (2, True, CHILD_AGES, 1.00, 0.67),
         "M100_67nc": (2, True, (), 1.00, 0.67)}
STEPS = {"d1": 0.01, "d10": 0.10}


def gen(cs):
    out, meta = {}, {}
    for c in cs:
        hs = []
        for t, (n, married, kids, m1, m2) in TYPES.items():
            for sname, d in [("base", 0.0)] + list(STEPS.items()):
                hid = f"omr-{c}-{t}-{sname}"
                ads = [adult(wages=AW[c] * (m1 + d))] + ([adult(wages=AW[c] * m2)] if n == 2 else [])
                hs.append(household(hid, ads, married=married, children=kids))
                meta[hid] = {"type": t, "step": sname}
        out[c] = hs
    return out, meta


def main(cs):
    run_dir, rows, info = runner.run("oecd_marginal", cs, slim=True, gen=gen, elections=False)
    T = {(r["country"], r["type"], r["step"]): r for r in rows}
    res = {"source": "OECD Taxing Wages 2026, NPMTR_PE (2025), data/oecd/tw_marginal_2025.json; models via "
                     "harness/oecd_marginal.py", "run": run_dir, "rows": []}
    for c in cs:
        for t in TYPES:
            b = T.get((c, t, "base"))
            if not b:
                continue
            o = OECD[ISO3[c]][t].get("NPMTR_PE|PT_WG_EARN_G")
            row = {"country": c, "type": t, "oecd": o}
            for s in STEPS:
                x = T.get((c, t, s))
                m = ((x["gross"] - x["net"]) - (b["gross"] - b["net"])) / (x["gross"] - b["gross"])
                row[s] = round(100 * m, 2)
            adj = 0.0
            if c == "US":
                adj = 6.65 + (0.30 * 21.06 if t == "SP67" else 0.0)
            row["adjustment_for_oecd_scope"] = round(adj, 2)
            row["d10_adjusted_minus_oecd"] = None if o is None else round(row["d10"] + adj - o, 2)
            res["rows"].append(row)
    json.dump(res, open(os.path.join(ROOT, "charts", "oecd_marginal_check.json"), "w"), indent=1)
    for r in res["rows"]:
        print(r)


if __name__ == "__main__":
    main(sys.argv[1].split(",") if len(sys.argv) > 1 else COUNTRIES)
