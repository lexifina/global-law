"""Tables for the four panels, from versions.tsv, extract.py's output and the citations.

    python analyze.py

Writes p1_heat.tsv, p1_survival.tsv, p2_complexity.tsv, p3_credit.tsv, p4_event.tsv, p4_effect.json, moved.tsv
"""
import bisect, math, collections, glob, json, os, random, re

HOME = os.path.expanduser("~/Documents/us-caselaw-lean-work")
VERS = os.path.join(HOME, "usc", "versions.tsv")
OUT = os.path.dirname(os.path.abspath(__file__))
XR = os.path.join(HOME, "uses", "xrefs", "by_year.tsv")


def w(name, rows):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")


def congress(label):
    return int(re.match(r"Pub\. L\. (\d+)-", label).group(1))


def main():
    rows = [l.rstrip("\n").split("\t") for l in open(VERS, encoding="utf-8")]
    st = {}
    for l in open(os.path.join(OUT, "vstats.tsv"), encoding="utf-8"):
        i, wd, xr = map(int, l.split("\t"))
        st[i] = (wd, xr)
    vers = collections.defaultdict(list)  # path -> [(day, row, kind, label, blob)]
    for i, f in enumerate(rows):
        vers[f[0]].append((int(f[4]), i, f[2], f[3], f[5]))
    for p in vers:
        vers[p].sort()

    LATE = {"title-7", "title-28", "title-39"}  # the record starts these with the 1995 edition (dated 1996-01-16)

    def state(p, day):
        """the version in force on day (None if none or deleted); titles the record starts late carry their first
        version back"""
        vs = vers[p]
        k = bisect.bisect_right(vs, (day, 10 ** 9)) - 1
        if k < 0 and p.split("/")[0] in LATE and vs[0][0] == 19960116:
            k = 0
        if k < 0 or not vs[k][4]:
            return None
        return vs[k]

    # ---- panel 1: share of sections a law of each Congress changed, by title
    tot = collections.Counter(); chg = collections.Counter()
    for p, vs in vers.items():
        t = p.split("/")[0][6:]
        for c in range(104, 120):
            a, b = (1789 + 2 * (c - 1)) * 10000 + 103, (1789 + 2 * c) * 10000 + 103
            alive = state(p, a) is not None or any(a <= v[0] < b and v[4] for v in vs)
            changed = any(v[2] == "law" and congress(v[3]) == c for v in vs)
            if alive or changed:
                tot[(t, c)] += 1; tot[("all", c)] += 1
            if changed:
                chg[(t, c)] += 1; chg[("all", c)] += 1
    w("p1_heat.tsv", [(t, c, chg[(t, c)], n, round(chg[(t, c)] / n, 4)) for (t, c), n in sorted(tot.items())])

    # ---- panel 2: complexity at the end of each year (version in force on 1 Feb of the next year, so that year's
    # edition, dated in January, is in); 2026 = the record today
    comp = []
    for y in range(1994, 2027):
        day = (y + 1) * 10000 + 201 if y < 2026 else 99999999
        words = secs = xr = 0
        for p in vers:
            v = state(p, day)
            if v:
                secs += 1; words += st[v[1]][0]; xr += st[v[1]][1]
        comp.append((y, words, secs, xr))
    w("p2_complexity.tsv", comp)

    # ---- panel 3: today's words by who wrote them
    cred = [l.rstrip("\n").split("\t") for l in open(os.path.join(OUT, "credit.tsv"), encoding="utf-8")]
    w("p3_credit.tsv", cred)

    # ---- panel 4: event study
    cites = collections.Counter()  # (path, sub, year) -> citations
    secy = collections.Counter()
    for fn in glob.glob(os.path.join(HOME, "usc", "cites", "*.usc.tsv")):
        for l in open(fn, encoding="utf-8"):
            f = l.rstrip("\n").split("\t")
            p = f"title-{f[2]}/{f[3]}.md"
            y = int(f[1][:4])
            cites[(p, f[4], y)] += 1
    units = collections.defaultdict(lambda: collections.Counter())
    for (p, s, y), n in cites.items():
        units[(p, s)][y] += n
    ev = collections.defaultdict(set)
    evlaw = {}
    for l in open(os.path.join(OUT, "events.tsv"), encoding="utf-8"):
        p, s, y, law = l.rstrip("\n").split("\t")
        ev[(p, s)].add(int(y)); evlaw[(p, s, int(y))] = law
    lawyears = {p: {v[0] // 10000 for v in vs if v[2] == "law"} for p, vs in vers.items()}
    R = range(-5, 6)
    treated = []
    for (p, s), ys in ev.items():
        for Y in ys:
            if not 2000 <= Y <= 2015:
                continue
            if any(abs(z - Y) <= 5 and z != Y for z in ys):
                continue  # rewritten again within five years: ambiguous
            c = units.get((p, s), {})
            pre = sum(c.get(Y + k, 0) for k in range(-5, 0))
            if pre >= 5:
                treated.append((p, s, Y, pre))
    # controls: cited (section, sub) units in the same title, section untouched by any law within Y-5..Y+5
    bytitle = collections.defaultdict(list)
    for (p, s), c in units.items():
        bytitle[p.split("/")[0]].append((p, s))
    rnd = random.Random(1)
    pairs = []
    for p, s, Y, pre in treated:
        best = []
        for q, s2 in bytitle[p.split("/")[0]]:
            if q == p or any(Y - 5 <= z <= Y + 5 for z in lawyears.get(q, ())):
                continue
            c = units[(q, s2)]
            pre2 = sum(c.get(Y + k, 0) for k in range(-5, 0))
            if pre2 == 0:
                continue
            tc = units[(p, s)]
            c1 = c.get(Y - 1, 0)
            if c1 == 0:
                continue
            t1 = max(tc.get(Y - 1, 0), 1)
            # same pre-period shape (each pre year relative to Y-1) and similar level
            shape = sum(abs(c.get(Y + k, 0) / c1 - tc.get(Y + k, 0) / t1) for k in range(-5, -1))
            best.append((shape + abs(math.log(pre2 / pre)), rnd.random(), q, s2))
        if not best:
            continue
        best.sort()
        ctrl = [(q, s2) for _, _, q, s2 in best[:5]]  # five nearest controls
        pairs.append(((p, s, Y), ctrl))

    def series(unit, Y):
        c = units[unit]
        return [c.get(Y + k, 0) for k in R]
    T = [0.0] * 11; C = [0.0] * 11
    per = []
    for (p, s, Y), ctrl in pairs:
        t = series((p, s), Y)
        cs = [series(u, Y) for u in ctrl]
        cm = [sum(x[k] for x in cs) / len(cs) for k in range(11)]
        for k in range(11):
            T[k] += t[k]; C[k] += cm[k]
        per.append((t, cm))
    ti = [x / T[4] * 100 for x in T]; ci = [x / C[4] * 100 for x in C]
    w("p4_event.tsv", [(k, round(T[i], 1), round(C[i], 1), round(ti[i], 1), round(ci[i], 1)) for i, k in enumerate(R)])

    def did(sample):
        tp = sum(sum(t[:5]) for t, c in sample); tq = sum(sum(t[6:]) for t, c in sample)
        cp = sum(sum(c[:5]) for t, c in sample); cq = sum(sum(c[6:]) for t, c in sample)
        return (tq / tp) / (cq / cp), tq / tp, cq / cp
    def idx(sample):
        t1 = sum(t[4] for t, c in sample); c1 = sum(c[4] for t, c in sample)
        tq = sum(sum(t[6:]) for t, c in sample) / 5 / t1; cq = sum(sum(c[6:]) for t, c in sample) / 5 / c1
        tp = sum(sum(t[:4]) for t, c in sample) / 4 / t1; cp = sum(sum(c[:4]) for t, c in sample) / 4 / c1
        return tq / cq, tq, cq, tp / cp
    est, tr, cr = did(per)
    e2 = idx(per)
    b2 = sorted(idx([per[rnd.randrange(len(per))] for _ in per])[0] for _ in range(1000))
    boots = sorted(did([per[rnd.randrange(len(per))] for _ in per])[0] for _ in range(1000))
    eff = {"events": len(pairs), "treated_candidates": len(treated), "ratio": round(est, 3),
           "treated_post_pre": round(tr, 3), "control_post_pre": round(cr, 3),
           "ci95": [round(boots[25], 3), round(boots[974], 3)],
           "post_vs_Yminus1": {"ratio": round(e2[0], 3), "treated": round(e2[1], 3), "control": round(e2[2], 3),
                               "pre_ratio_Y-5..Y-2": round(e2[3], 3), "ci95": [round(b2[25], 3), round(b2[974], 3)]},
           "laws": len({evlaw[k] for k, _ in pairs}), "sections": len({k[0] for k, _ in pairs})}
    json.dump(eff, open(os.path.join(OUT, "p4_effect.json"), "w", encoding="utf-8", newline="\n"), indent=1)
    print(eff)

    # ---- moved phrases: 30-word runs inserted by two different laws
    by = collections.defaultdict(set)
    for l in open(os.path.join(OUT, "shingles.tsv"), encoding="utf-8"):
        h, law, p = l.rstrip("\n").split("\t")
        by[h].add((law, p))
    moved = [(h, len({x[0] for x in v}), sorted(v)[:4]) for h, v in by.items() if len({x[0] for x in v}) >= 2]
    moved.sort(key=lambda r: -r[1])
    w("moved.tsv", [(h, n, "; ".join(f"{a} {b}" for a, b in v)) for h, n, v in moved])
    print("moved runs", len(moved), "of", len(by))


if __name__ == "__main__":
    main()
