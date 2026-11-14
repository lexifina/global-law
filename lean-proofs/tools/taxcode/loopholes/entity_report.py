"""Summarise the entity search (DATA/search.json) and pick plans for the kernel re-check.

    python tools/taxcode/loopholes/entity_report.py

Prints, per scenario and exit: the baseline, the best plans with distinct structures, what each lever of the best plan
is worth (the plan with that lever removed, re-run in Lean), and the largest one-step jumps between neighbouring
switch years (cliffs). Writes DATA/report.json and DATA/found.json.
"""
import copy, json
from entity_lib import SCENARIOS, DATA, run

def sig(p):
    return (tuple(tuple(f) for f in p["forms"]), tuple((g["year"], g["bp"], g["toTrusts"]) for g in p["gifts"]))

def describe(p):
    fs = " → ".join(f"{f}@{y}" for y, f in p["forms"]) or "u"
    g = "; ".join(f"gift {x['bp']/100:.0f}% to {'trusts' if x['toTrusts'] else 'children'} @{x['year']}" for x in p["gifts"])
    return f"{fs}, salary {p['salary']}, payout {p['payoutBp']/100:.0f}%{', ' + g if g else ''}, {p['exit']}"

def without(p, lever):
    q = copy.deepcopy(p)
    if lever == "gift": q["gifts"] = []
    elif lever == "form": q["forms"] = []
    elif lever == "switch": q["forms"] = q["forms"][:1]
    elif lever == "salary": q["salary"] = 10 ** 9
    elif lever == "payout": q["payoutBp"] = 10000
    elif lever == "toTrusts":
        for g in q["gifts"]: g["toTrusts"] = False
    return q

def main():
    keep = json.load(open(DATA / "search.json"))
    summ = json.load(open(DATA / "search_summary.json"))
    nog = {}
    for extra in ("search_venture", "search_nogift", "search_nogift_venture"):
        if not (DATA / f"{extra}.json").exists(): continue
        k2 = json.load(open(DATA / f"{extra}.json")); s2 = json.load(open(DATA / f"{extra}_summary.json"))
        if "nogift" in extra:
            for key, rows in k2.items(): nog[key] = rows
            for nm, v in s2.items(): summ.setdefault(nm, v)
        else:
            keep.update(k2); summ.update(s2)
    report, found, jobs, meta = {}, [], [], []
    for key, rows in keep.items():
        name, ex = key.split("/")
        base = summ[name]["base"][ex]
        tops, seen = [], set()
        for r in rows:
            sg = sig(r["plan"])
            if sg in seen: continue
            seen.add(sg); tops.append(r)
            if len(tops) == 8: break
        best = tops[0]
        for lever in ("gift", "toTrusts", "form", "switch", "salary", "payout"):
            q = without(best["plan"], lever)
            if q != best["plan"]:
                jobs.append((name, q, False)); meta.append((key, lever))
        report[key] = {"base": base["wealth"], "baseTax": base["taxPaid"] + base["exitTax"] + base["estateTax"],
                       "tops": [{"gain": t["gain"], "plan": describe(t["plan"]), "raw": t["plan"], "qsbs": t["qsbs"],
                                 "estateTax": t["estateTax"], "exitTax": t["exitTax"], "taxPaid": t["taxPaid"]} for t in tops],
                       "levers": {}}
    # cliffs: the best plan with its change-of-form year (or its gift year) moved through every year
    for key in list(report):
        name, ex = key.split("/")
        bp = report[key]["tops"][0]["raw"]
        H = SCENARIOS[name]["horizon"]
        for k in range(1, H):
            if len(bp["forms"]) > 1:
                q = copy.deepcopy(bp); q["forms"][1][0] = k; jobs.append((name, q, False)); meta.append((key, f"switch@{k}"))
            if bp["gifts"]:
                q = copy.deepcopy(bp); q["gifts"][0]["year"] = k; jobs.append((name, q, False)); meta.append((key, f"gift@{k}"))
    outs = run(SCENARIOS, jobs, procs=8, tag="levers")
    for (key, lever), (name, q, _), o in zip(meta, jobs, outs):
        if "@" in lever:
            report[key].setdefault("sweep", {})[lever] = o["wealth"] - report[key]["base"]
        else:
            report[key]["levers"][lever] = report[key]["tops"][0]["gain"] - (o["wealth"] - report[key]["base"])
    for key, r in report.items():
        sw = r.get("sweep", {})
        jumps = []
        for kind in ("switch", "gift"):
            ks = sorted(int(x.split("@")[1]) for x in sw if x.startswith(kind))
            for a, b in zip(ks, ks[1:]):
                jumps.append((sw[f"{kind}@{b}"] - sw[f"{kind}@{a}"], f"{kind} {a}->{b}"))
        r["cliffs"] = sorted(jumps, key=lambda j: -abs(j[0]))[:4]
    # best plan that changes the entity alone (no gifts), per scenario and exit
    for key, rows in keep.items():
        ng = nog.get(key) or [r for r in rows if not r["plan"]["gifts"]]
        if ng:
            report[key]["bestNoGift"] = {"gain": ng[0]["gain"], "plan": describe(ng[0]["plan"]), "raw": ng[0]["plan"],
                                         "qsbs": ng[0]["qsbs"]}
        q = sorted([r for r in rows + nog.get(key, []) if r["qsbs"] > 0], key=lambda r: -r["gain"])
        if q:
            report[key]["bestQsbs"] = {"gain": q[0]["gain"], "plan": describe(q[0]["plan"]), "raw": q[0]["plan"],
                                       "qsbs": q[0]["qsbs"]}
    json.dump(report, open(DATA / "report.json", "w"), indent=1)
    # the plans whose figures the kernel re-checks (Found.lean)
    found = []
    def add(label, name, p, wealth, note):
        found.append(dict(label=label, scenario=name, plan=p, wealth=wealth, note=note))
    for name in summ:
        key = f"{name}/sale"
        if key not in report: continue
        r = report[key]
        add(f"{name}_base", name, {"forms": [], "salary": 0, "payoutBp": 10000, "gifts": [], "exit": "sale"}, r["base"],
            "Baseline: unincorporated throughout, no gift, sold at the horizon.")
        add(f"{name}_best", name, r["tops"][0]["raw"], r["base"] + r["tops"][0]["gain"], "Best plan found: " + r["tops"][0]["plan"])
        if "bestNoGift" in r:
            add(f"{name}_entity", name, r["bestNoGift"]["raw"], r["base"] + r["bestNoGift"]["gain"],
                "Best plan without a gift (entity choices alone): " + r["bestNoGift"]["plan"])
        if "bestQsbs" in r and name in ("startup", "venture"):
            add(f"{name}_qsbs", name, r["bestQsbs"]["raw"], r["base"] + r["bestQsbs"]["gain"],
                "Best plan with a §1202 exclusion: " + r["bestQsbs"]["plan"])
    json.dump(found, open(DATA / "found.json", "w"), indent=1)
    for key, r in report.items():
        print(f"== {key}: baseline wealth {r['base']:,}  (baseline taxes {r['baseTax']:,})")
        for t in r["tops"]:
            print(f"   {t['gain']:>12,}  {t['plan']}  qsbs {t['qsbs']:,}")
        print("   levers of the best (wealth lost without it):", {k: f"{v:,}" for k, v in r["levers"].items()})
        if "bestNoGift" in r: print("   best without a gift:", f"{r['bestNoGift']['gain']:,}", r["bestNoGift"]["plan"])
        if "bestQsbs" in r: print("   best with a §1202 exclusion:", f"{r['bestQsbs']['gain']:,}", r["bestQsbs"]["plan"], f"excluded {r['bestQsbs']['qsbs']:,}")
        print("   largest one-year steps:", [(f"{d:,}", w) for d, w in r.get("cliffs", [])])

if __name__ == "__main__":
    main()
