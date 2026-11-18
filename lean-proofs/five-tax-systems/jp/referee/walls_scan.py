"""Scan household net income as one person's salary varies (the 年収の壁), using jptax.
For each scenario, salaries from 0 to 3,000,000 yen in 1,000-yen steps plus each statutory threshold and +1 yen;
net = gross - incomeTax - surtaxes - localIncomeTax - employeeSocial + benefits (contract definition).
Reports every step where net income falls, with the components that moved.
usage: python3 walls_scan.py <jptax binary> > walls.txt"""
import sys, json, subprocess

JPTAX = sys.argv[1]

THRESH = [651000, 1056000, 1100000, 1230000, 1300000, 1500000, 1550000, 1600000, 1650000, 1700000, 1750000,
          1800000, 1850000, 1880000, 1900000, 1903999, 1971999, 2015999, 2340000]


def grid():
    pts = set(range(0, 3000001, 1000))
    for t in THRESH:
        for d in (-1, 0, 1):
            pts.add(t + d)
    return sorted(pts)


SCEN = {
    "spouse (secondary earner; primary 6,000,000, age 40/38, 2 children 8 and 5)":
        lambda w: {"adults": [{"age": 40, "wages": 6000000}, {"age": 38, "wages": w}], "married": True,
                   "children": [{"age": 8}, {"age": 5}]},
    "single person, age 30":
        lambda w: {"adults": [{"age": 30, "wages": w}], "married": False, "children": []},
    "student aged 20 working (parents: 6,000,000 + 0)":
        lambda w: {"adults": [{"age": 50, "wages": 6000000}, {"age": 48, "wages": 0}], "married": True,
                   "children": [{"age": 20, "wages": w}]},
    "high-school child aged 17 working (parents: 6,000,000 + 0)":
        lambda w: {"adults": [{"age": 50, "wages": 6000000}, {"age": 48, "wages": 0}], "married": True,
                   "children": [{"age": 17, "wages": w}]},
    "single parent (mother, age 35, one child aged 6)":
        lambda w: {"adults": [{"age": 35, "wages": w}], "married": False, "children": [{"age": 6}]},
}


def run(hs):
    inp = "\n".join(json.dumps(h, ensure_ascii=False) for h in hs) + "\n"
    out = subprocess.run([JPTAX], input=inp.encode(), capture_output=True).stdout.decode()
    return [json.loads(l) for l in out.splitlines() if l.strip()]


def gross(h):
    return sum(a.get("wages", 0) for a in h["adults"]) + sum(c.get("wages", 0) for c in h["children"])


for name, mk in SCEN.items():
    ws = grid()
    hs = []
    for i, w in enumerate(ws):
        h = mk(w)
        h.update({"id": "w%d" % i, "year": 2025})
        hs.append(h)
    outs = run(hs)
    rows = []
    for h, o in zip(hs, outs):
        comp = {"it": o["incomeTax"], "fk": o["surtaxes"]["復興特別所得税"], "lt": o["localIncomeTax"],
                "ss": o["employeeSocial"], "bf": o["benefits"]}
        net = gross(h) - comp["it"] - comp["fk"] - comp["lt"] - comp["ss"] + comp["bf"]
        rows.append((h, net, comp))
    print("=" * 100)
    print(name)
    drops = []
    for (h0, n0, c0), (h1, n1, c1), w0, w1 in zip(rows, rows[1:], ws, ws[1:]):
        if n1 < n0:
            moved = {k: c1[k] - c0[k] for k in c0 if c1[k] != c0[k]}
            drops.append((w0, w1, n1 - n0, moved))
    print("  steps where net income falls: %d" % len(drops))
    big = drops
    for w0, w1, dn, moved in sorted(big):
        print("   %9d -> %9d  net %+8d  (%s)" % (w0, w1, dn, ", ".join("%s %+d" % kv for kv in moved.items())))
    # net income at a few points
    for t in (1030000, 1060000, 1230000, 1300000, 1500000, 1600000, 1880000, 2000000):
        for (h, n, c), w in zip(rows, ws):
            if w == t:
                print("   at %9d: net %d  (it %d, fk %d, local %d, social %d, benefits %d)" %
                      (w, n, c["it"], c["fk"], c["lt"], c["ss"], c["bf"]))
