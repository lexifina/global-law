"""Rank what the family search found.

    python tools/taxcode/loopholes/family_report.py

Reads DATA/singles.json, greedy.json, pairs.json. For each family prints the best single move of each kind (lever),
the greedy path, and the pairs whose gain is most out of line with their two parts (synergy). "Out of proportion" is
the gain per dollar the move touches: the dollars converted, realised, given, paid or distributed over the years
(re-run with the year log by `size()`).
"""
import json, sys
from family_lib import DATA, FAMILIES
from family_search import build, specs, lever, run


def load(name):
    p = DATA / name
    return json.load(open(p)) if p.exists() else None


def size(f, ms):
    """Dollars a plan touches: conversions + harvested gain (from the year log) + gifts + trust funding + children's
    wages + charity moved between years."""
    name, plan = build(f, ms)
    o = run(specs(), [(name, plan, True)], procs=1, tag="size")[0]
    s = FAMILIES[f]
    touched = sum(l["conv"] + l["harvest"] for l in o["log"])
    for y, p in enumerate(plan):
        touched += sum(p["gifts"]) + p["trustFund"] + sum(min(w, 20000) for w in p["kidWage"])
        if p["charity"] >= 0: touched += abs(p["charity"] - s["charity"])
    return touched, o


def fmt(m):
    return " ".join(str(x) for x in m)


def main():
    S = load("singles.json"); G = load("greedy.json"); P = load("pairs.json")
    base = S["base"]
    for f in FAMILIES:
        print(f"\n=== {f}: baseline after-tax wealth ${base[f]['wealth']:,}")
        ss = [x for x in S["singles"] if x["family"] == f]
        best = {}
        for x in ss:
            k = lever(x["move"])
            if k not in best or x["gain"] > best[k]["gain"]: best[k] = x
        for k, x in sorted(best.items(), key=lambda kv: -kv[1]["gain"]):
            print(f"  {k:14s} {x['gain']:>+12,}  {fmt(x['move'])}")
        if G and f in G:
            print(f"  greedy: {G[f]['gain']:+,}")
            for st in G[f]["path"]:
                print(f"     {st['step']:>+12,}  {fmt(st['move'])}")
        if P:
            pp = sorted([x for x in P if x["family"] == f], key=lambda x: -x["synergy"])[:5]
            for x in pp:
                print(f"  synergy {x['synergy']:>+10,} (pair {x['gain']:+,}): {fmt(x['moves'][0])} + {fmt(x['moves'][1])}")
    if "--size" in sys.argv:
        print("\nout of proportion (gain per dollar touched), best single per lever:")
        for f in FAMILIES:
            ss = [x for x in S["singles"] if x["family"] == f and x["gain"] > 0]
            best = {}
            for x in ss:
                k = lever(x["move"])
                if k not in best or x["gain"] > best[k]["gain"]: best[k] = x
            for k, x in best.items():
                t, _ = size(f, [tuple(x["move"])])
                print(f"  {f:10s} {k:14s} gain {x['gain']:>+12,} touched {t:>12,}  ratio {x['gain'] / max(t, 1):.3f}")


if __name__ == "__main__":
    main()
