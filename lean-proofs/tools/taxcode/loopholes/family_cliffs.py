"""Cliff scan: on top of each family's greedy plan, sweep one amount finely and look for jumps.

    python tools/taxcode/loopholes/family_cliffs.py [procs]

For every lever that takes an amount (a child's wage, a lump gift, a conversion amount, a harvest target for a child,
in every window between two events (and the whole horizon), the amount is swept in fine steps and the after-tax wealth at
the horizon recorded. A "cliff" is a step where a small change in the amount moves wealth by much more than the
change itself: |Δwealth| / Δamount above 1 (one dollar more of the lever is worth more than a dollar). The sweep does
not know where any threshold is.
Writes DATA/cliffs.json.
"""
import json, sys
from family_lib import FAMILIES, DATA
from family_search import events, evaluate, load_greedy

STEPS = {
    "kidWage": list(range(0, 30001, 500)),
    "giftLump": list(range(0, 400001, 20000)),
    "convAmt": list(range(0, 300001, 10000)),
    "kidHarvestTo": list(range(0, 120001, 2500)),
}


def main():
    procs = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    G = load_greedy()
    out = []
    for f, s in FAMILIES.items():
        base = [tuple(m) for m in G[f]["moves"]]
        ev = events(s)
        for (a, b) in list(zip(ev, ev[1:])) + [(0, s["horizon"])]:
            for kind, grid in STEPS.items():
                if kind == "kidWage" and s["business"] == 0: continue
                mk = (lambda x: (kind, a, a + 1, x)) if kind == "giftLump" else \
                     (lambda x: (kind, a, b, x, 1)) if kind == "kidWage" else (lambda x: (kind, a, b, x))
                cands = [(f, [m for m in base if m[0] != kind] + [mk(x)]) for x in grid]
                res = evaluate(cands, procs, f"cliff_{f}")
                w = [o["wealth"] for o in res]
                for i in range(1, len(grid)):
                    d = w[i] - w[i - 1]; dx = grid[i] - grid[i - 1]
                    if abs(d) > dx:
                        out.append({"family": f, "kind": kind, "window": [a, b], "from": grid[i - 1], "to": grid[i],
                                    "dw": d, "ratio": d / dx})
                print(f, kind, (a, b), "max", max(w) - w[0], "at", grid[w.index(max(w))]); sys.stdout.flush()
                json.dump(out, open(DATA / "cliffs.json", "w"))


if __name__ == "__main__":
    main()
