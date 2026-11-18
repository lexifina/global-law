"""Step 4: bounded novel search (income 2025). Writes ../runs/novel_*.json and prints summaries.
N1  value of each lever in three CDHR zones (none / smoothing band / above the band)
N2  joint vs one-at-a-time choice of four options on random households (non-separability)
N3  allocations familiales x income tax x contributions: effective marginal rates on pay; 2OP vs AF resources
N5  quotient (163-0 A) scan: where the option costs more than ordinary taxation; CDHR quarter rule
N6  the global cap (200-0 A) with credits the CDHR takes back
"""
import json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib as L

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
which = sys.argv[1:] or ["N1", "N2", "N3", "N5", "N6"]
S = {"0AC": 1, "0DA": 1975}
C = {"0AM": 1, "0DA": 1975, "0DB": 1977}


def B(*ds, **kw):
    o = {}
    for d in ds:
        o.update(d)
    o.update(kw)
    return o


def save(name, obj):
    json.dump(obj, open(os.path.join(RUNS, name), "w"), indent=1)


# ------------------------------------------------------------------ N1
if "N1" in which:
    zones = {
        "single, no CDHR (salary 120k)": B(S, **{"1AJ": 120000}),
        "single, CDHR band (30k + 290k div.)": B(S, **{"1AJ": 30000, "2DC": 290000, "2BH": 290000}),
        "single, CDHR above band (150k + 800k div.)": B(S, **{"1AJ": 150000, "2DC": 800000, "2BH": 800000}),
        "couple, no CDHR (salary 250k)": B(C, **{"1AJ": 250000}),
        "couple, CDHR band (60k + 600k div.)": B(C, **{"1AJ": 60000, "2DC": 600000, "2BH": 600000}),
        "couple, CDHR above band (300k + 1.5M div.)": B(C, **{"1AJ": 300000, "2DC": 1500000, "2BH": 1500000}),
    }
    levers = [  # name, box delta, extra, nominal outlay or amount
        ("attach adult child (0DJ)", {"0DJ": 1}, None),
        ("alimony to adult child 6 855 (6EL)", {"6EL": 6855}, None),
        ("PER 10 000 (6NS, ceiling 10 000)", {"6NS": 10000, "APS": 10000}, None),
        ("deficit foncier 10 700 (4BC)", {"4BC": 10700}, None),
        ("overtime 7 500 exempt (1GH) instead of salary", {"1GH": 7500, "1AJ": -7500}, None),
        ("gifts 10 000 (7UF)", {"7UF": 10000}, None),
        ("home help 12 000 (7DB)", {"7DB": 12000}, None),
        ("Pinel reduction 5 000", {}, {"PIN": 5000}),
        ("IR-PME 50 000 (9 000)", {}, {"PME": 50000}),
        ("Girardin reduction 20 000", {}, {"GIR": 20000}),
        ("prestation compensatoire capital 30 500 (7 625)", {}, {"PC": 30500}),
        ("scale option 2OP", {"2OP": 1}, None),
    ]
    cases = []
    for zi, (zn, zb) in enumerate(zones.items()):
        cases.append((f"z{zi}", 2025, zb, None))
        for li, (ln, lb, lx) in enumerate(levers):
            b = dict(zb)
            for k, v in lb.items():
                b[k] = b.get(k, 0) + v
            cases.append((f"z{zi}l{li}", 2025, b, lx))
    R = L.run(cases)
    tab = {}
    for zi, (zn, zb) in enumerate(zones.items()):
        base = L.burden(zb, R[f"z{zi}"])
        tab[zn] = {"base": base, "cdhr": R[f"z{zi}"]["CDHR"]}
        for li, (ln, lb, lx) in enumerate(levers):
            o = R[f"z{zi}l{li}"]
            tab[zn][ln] = base - L.burden(cases[0][2] if False else dict(zb, **lb), o)
    save("novel_n1.json", tab)
    print("N1 saving by lever (euros) per zone")
    for zn, row in tab.items():
        print(" ", zn, "base", row["base"], "cdhr", row["cdhr"])
        for k, v in row.items():
            if k not in ("base", "cdhr"):
                print(f"     {v:>8}  {k}")

# ------------------------------------------------------------------ N2
if "N2" in which:
    random.seed(11)
    HH = []
    for h in range(20000):
        couple = random.random() < 0.6
        b = dict(C if couple else S)
        sal = int(random.lognormvariate(10.6, 0.7))
        b["1AJ"] = sal
        if couple and random.random() < 0.7:
            b["1BJ"] = int(random.lognormvariate(10.2, 0.7))
        if random.random() < 0.6:
            b["0CF"] = random.choice([1, 2, 3])
        div = int(random.lognormvariate(8.5, 1.5)) if random.random() < 0.8 else 0
        intr = int(random.lognormvariate(7.5, 1.3)) if random.random() < 0.5 else 0
        if div:
            b["2DC"] = div
        if intr:
            b["2TR"] = intr
        if div + intr:
            b["2BH"] = div + intr
        rents = int(random.uniform(3000, 15000)) if random.random() < 0.5 else 0
        rexp = random.uniform(0.05, 0.6)
        fexp = int(sal * random.uniform(0.02, 0.2))
        HH.append(dict(b=b, rents=rents, rexp=rexp, fexp=fexp, child=random.random() < 0.5))
    OPTS = ["2OP", "alimony", "realexp", "realrent"]

    def build(h, o):
        b = dict(h["b"])
        if o[0] and ("2DC" in b or "2TR" in b):
            b["2OP"] = 1
        if h["child"]:
            if o[1]:
                b["6EL"] = 6855
            else:
                b["0DJ"] = 1
        if o[2]:
            b["1AK"] = h["fexp"]
        if h["rents"]:
            if o[3]:
                b["4BA"] = int(h["rents"] * (1 - h["rexp"]))
            else:
                b["4BE"] = h["rents"]
        return b

    combos = [(a, c, d, e) for a in (0, 1) for c in (0, 1) for d in (0, 1) for e in (0, 1)]
    cases = []
    for i, h in enumerate(HH):
        for j, o in enumerate(combos):
            cases.append((f"{i}_{j}", 2025, build(h, o), None))
    t0 = time.time()
    R = L.run(cases)
    res = []
    for i, h in enumerate(HH):
        val = {}
        for j, o in enumerate(combos):
            b = build(h, o)
            # the child's own return when alimony is paid: 6 855 less 10 % = 6 169, nil tax (LOOPHOLES finding 1)
            val[o] = L.burden(b, R[f"{i}_{j}"])
        best = min(val.values())
        # one-at-a-time: start from the default (PFU, attach, 10 %, micro), flip each option alone if it helps
        # (decided against the default), then apply all the flips together
        d0 = (0, 0, 0, 0)
        flips = [k for k in range(4) if val[tuple(1 if x == k else 0 for x in range(4))] < val[d0]]
        greedy = tuple(1 if k in flips else 0 for k in range(4))
        # sequential improvement: flip options one by one in the fixed order, keeping a flip if it helps
        cur = list(d0)
        for k in range(4):
            t = list(cur); t[k] = 1 - t[k]
            if val[tuple(t)] < val[tuple(cur)]:
                cur = t
        res.append(dict(i=i, best=best, default=val[d0], separate=val[greedy], sequential=val[tuple(cur)],
                        argbest=[k for k, v in val.items() if v == best][0], greedy=greedy, seq=tuple(cur)))
    gaps = [r["separate"] - r["best"] for r in res]
    gseq = [r["sequential"] - r["best"] for r in res]
    nz = sorted([g for g in gaps if g > 0])
    worst = sorted(res, key=lambda r: r["best"] - r["separate"])[:15]
    save("novel_n2.json", dict(n=len(res), separate_gap_count=len(nz), separate_gap_max=max(gaps),
                               separate_gap_median=nz[len(nz) // 2] if nz else 0,
                               sequential_gap_count=len([g for g in gseq if g > 0]), sequential_gap_max=max(gseq),
                               worst=[dict(r, hh=HH[r["i"]]) for r in worst]))
    print(f"N2 {len(res)} households, {len(cases)} returns, {time.time() - t0:.0f}s")
    print("   options decided separately miss the joint optimum for", len(nz), "households; max", max(gaps),
          "median", nz[len(nz) // 2] if nz else 0)
    print("   sequential (fixed order) misses for", len([g for g in gseq if g > 0]), "max", max(gseq))
    for r in worst[:6]:
        print("   ", r["best"] - r["separate"], "best", r["argbest"], "separate", r["greedy"], HH[r["i"]])

# ------------------------------------------------------------------ N3
if "N3" in which:
    out = {}
    fams = {"couple 2 children (6, 11)": [6, 11], "couple 2 children (15, 17)": [15, 17],
            "couple 3 children (4, 8, 15)": [4, 8, 15], "couple 4 children": [3, 6, 9, 15]}
    step = 100
    for fn, ages in fams.items():
        for split in (1.0, 0.5):
            cases, meta = [], []
            for g in range(20000, 200001, step):
                g1, g2 = int(g * split), g - int(g * split)
                b = B(C, **{"0CF": len(ages)})
                b["1AJ"] = L.taxable_salary(g1)
                if g2:
                    b["1BJ"] = L.taxable_salary(g2)
                cases.append((f"{g}", 2025, b, None))
                meta.append((g, g1, g2, b))
            R = L.run(cases)
            prev = None
            bands = []
            for g, g1, g2, b in meta:
                o = R[f"{g}"]
                c1, c2 = L.contrib(g1), L.contrib(g2)
                res = o["RNG"]  # salaries only: the adapter's AF resources (grossGlobal + flatBase) = RNG here
                af = L.af_net(res, ages)
                net = g - c1[0] - c1[1] - c2[0] - c2[1] - o["IMPNET"] + af
                if prev:
                    emtr = 1 - (net - prev[1]) / (g - prev[0])
                    if emtr > 0.75:
                        bands.append((prev[0], g, round(emtr, 3), af - prev[2], o["IMPNET"] - prev[3]))
                prev = (g, net, af, o["IMPNET"])
            # merge consecutive steps
            merged = []
            for a, z, e, daf, dt in bands:
                if merged and merged[-1][1] == a:
                    m = merged[-1]
                    merged[-1] = [m[0], z, max(m[2], e), m[3] + daf, m[4] + dt]
                else:
                    merged.append([a, z, e, daf, dt])
            out[f"{fn}, split {split}"] = merged
            print("N3", fn, "split", split, "bands EMTR>75 %:", [(m[0], m[1], m[2]) for m in merged][:8])
    # 2OP lowers the AF resources: dividends taxed at the scale count after the 40 % allowance (net categorial),
    # under PFU in full (adapter: grossGlobal + flatBase). Grid: couple 2 children, wages, dividends.
    cases, meta = [], []
    for g in range(60000, 110001, 1000):
        for dv in range(1000, 30001, 1000):
            ts = L.taxable_salary(g)
            for opt in (0, 1):
                b = B(C, **{"0CF": 2, "1AJ": ts, "2DC": dv, "2BH": dv})
                if opt:
                    b["2OP"] = 1
                cases.append((f"{g}_{dv}_{opt}", 2025, b, None))
                meta.append((g, dv, opt))
    R = L.run(cases)
    flips = []
    for g in range(60000, 110001, 1000):
        for dv in range(1000, 30001, 1000):
            v = {}
            for opt in (0, 1):
                o = R[f"{g}_{dv}_{opt}"]
                csg = round(dv * 0.068) if opt else 0
                res = o["RNG"] + csg + (0 if opt else dv)    # grossGlobal + flatBase
                v[opt] = (o["IMPNET"] + o["PSNET"], L.af_net(res, [6, 11]))
            tax_pref = 1 if v[1][0] < v[0][0] else 0
            tot = {k: v[k][0] - v[k][1] for k in v}
            tot_pref = 1 if tot[1] < tot[0] else 0
            if tax_pref != tot_pref:
                flips.append(dict(gross=g, dividends=dv, tax_pfu=v[0][0], tax_2op=v[1][0], af_pfu=v[0][1],
                                  af_2op=v[1][1], gain=abs(tot[1] - tot[0])))
    out["2OP_AF_flips"] = flips
    print("N3 2OP chosen only because of the AF resources:", len(flips), "grid points; max gain",
          max([f["gain"] for f in flips], default=0))
    for f in sorted(flips, key=lambda f: -f["gain"])[:5]:
        print("   ", f)
    save("novel_n3.json", out)

# ------------------------------------------------------------------ N5
if "N5" in which:
    cases, meta = [], []
    fam = {"single": S, "couple": C, "couple 2 ch.": B(C, **{"0CF": 2}), "single T 1 ch.": B(S, **{"0CF": 1, "0BT": 1}),
           "single over 65": B(S, **{"0DA": 1950})}
    for fn, fb in fam.items():
        for base in list(range(0, 60001, 2000)) + list(range(60000, 400001, 20000)):
            for E in list(range(1000, 20001, 1000)) + list(range(25000, 400001, 25000)):
                bq = B(fb, **{"5QC": base}) if base else dict(fb)
                cases.append((f"{fn}|{base}|{E}|q", 2025, bq, {"EXC": E}))
                cases.append((f"{fn}|{base}|{E}|o", 2025, B(bq, **{"5QC": base + E}), None))
    R = L.run(cases)
    worse = []
    for c in cases:
        if c[0].endswith("|q"):
            k = c[0][:-2]
            q, o = R[k + "|q"], R[k + "|o"]
            d = L.burden(c[2], q) - L.burden({}, o)
            if d > 0:
                worse.append((k, d, q["IMPNET"], o["IMPNET"]))
    worse.sort(key=lambda x: -x[1])
    save("novel_n5.json", dict(n=len(cases) // 2, worse=worse[:200], n_worse=len(worse)))
    print("N5", len(cases) // 2, "pairs; quotient costs more than ordinary in", len(worse), "; top:", worse[:8])

# ------------------------------------------------------------------ N6
if "N6" in which:
    CD2 = B(S, **{"1AJ": 150000, "2DC": 800000, "2BH": 800000})
    NO = B(S, **{"1AJ": 150000})
    rows = []
    for nm, base in (("no CDHR", NO), ("CDHR payer", CD2)):
        for hh in (0, 6000, 12000, 15000):
            for pme in (0, 50000):
                b = B(base, **({"7DB": hh} if hh else {}))
                rows.append((nm, hh, pme, b, {"PME": pme} if pme else None))
    R = L.run([(f"{i}", 2025, r[3], r[4]) for i, r in enumerate(rows)])
    tab = []
    for i, r in enumerate(rows):
        tab.append(dict(zone=r[0], homehelp=r[1], pme=r[2], burden=L.burden(r[3], R[f"{i}"]), red=R[f"{i}"]["ITRED"],
                        cr=R[f"{i}"]["CITOT"], cdhr=R[f"{i}"]["CDHR"]))
    save("novel_n6.json", tab)
    print("N6 cap x CDHR")
    for t in tab:
        print("   ", t)
