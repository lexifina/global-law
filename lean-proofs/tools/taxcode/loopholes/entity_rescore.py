"""Re-evaluate the kept plans of DATA/search.json (and the baselines) with the current Lean model, after a model fix
that can only lower wealth. A plan outside the kept 3,000 per scenario and exit cannot overtake a kept one, so the
ranking of the kept set is the ranking of the whole search.

    python tools/taxcode/loopholes/entity_rescore.py [procs]
"""
import json, sys
from entity_lib import SCENARIOS, DATA, plan, run

def main():
    procs = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    keep = json.load(open(DATA / "search.json"))
    summ = json.load(open(DATA / "search_summary.json"))
    jobs, where = [], []
    for name in SCENARIOS:
        for ex in ("sale", "assetSale", "death"):
            jobs.append((name, plan(exit=ex), False)); where.append(("base", name, ex))
    for key, rows in keep.items():
        name, _ = key.split("/")
        for i, r in enumerate(rows):
            jobs.append((name, r["plan"], False)); where.append((key, i))
    outs = run(SCENARIOS, jobs, procs=procs, tag="rescore")
    base = {}
    for w, o in zip(where, outs):
        if w[0] == "base":
            base[(w[1], w[2])] = o
            summ[w[1]]["base"][w[2]] = {k: v for k, v in o.items() if k != "log"}
    for w, o in zip(where, outs):
        if w[0] == "base": continue
        key, i = w; name, ex = key.split("/"); b = base[(name, ex)]; r = keep[key][i]
        r.update(wealth=o["wealth"], gain=o["wealth"] - b["wealth"], estateTax=o["estateTax"] - b["estateTax"],
                 exitTax=o["exitTax"] - b["exitTax"], taxPaid=o["taxPaid"] - b["taxPaid"], corpTax=o["corpTaxPaid"],
                 payroll=o["payroll"] - b["payroll"], latent=o["kidsLatent"] - b["kidsLatent"], qsbs=o["qsbsExcluded"],
                 finalForm=o["finalForm"])
    for key in keep:
        keep[key].sort(key=lambda r: -r["gain"])
        name, ex = key.split("/")
        summ[name][ex]["best"] = keep[key][0]["gain"]
        print(key, keep[key][0]["gain"], keep[key][0]["plan"])
    json.dump(keep, open(DATA / "search.json", "w"))
    json.dump(summ, open(DATA / "search_summary.json", "w"), indent=1)

if __name__ == "__main__":
    main()
