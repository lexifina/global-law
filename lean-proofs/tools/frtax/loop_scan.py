"""Loophole hunt, step 2a: effective marginal rates along income rays, every year, family type and income mix.

For each template (year, family, background, moving income box) the moving income x runs from 0 to 150 000 € in
steps of 7 € and from 150 000 € to 800 000 € in steps of 50 €. The burden (net income tax incl. refunds, CEHR, CDHR,
social levies on the return, the micro flat levy) is computed by the Lean model at every point. Steps whose rate
(Δburden / Δx) is above 60 % or below 0 are merged into intervals; the steps with a rate above 100 % (and the first
steps of each interval) are refined euro by euro, with the outputs that moved (the cause).

usage: loop_scan.py [years]       writes runs/loop/scan_intervals.jsonl, runs/loop/scan_notches.jsonl
"""
import json, os, sys, subprocess, itertools, multiprocessing as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loop_lib as L

OUT = os.path.expanduser("~/fr/runs/loop")
POS = {"IMPNET": 13, "PSNET": 15, "CHRAPRES": 16, "CDHR": 17}
NAMES = ["NBPT", "RNG", "RNI", "IDRSFULL", "IDRSCAP", "IDRS", "IDEC", "ITRED", "CITOT", "PFU", "IDRS4", "IAVCR",
         "IMPNET", "REVKIRE", "PSNET", "CHRAPRES", "CDHR"]


def families(y):
    k = lambda b, **kw: L.kids(b, y, **kw)
    return {
        "S": L.single(y),
        "S_T1": k(L.single(y, **{"0BT": 1}), nf=1),
        "S_T2": k(L.single(y, **{"0BT": 1}), nf=2),
        "S_H2": k(L.single(y, **{"0BT": 1}), nh=2),
        "S_L": L.single(y, 1960, **{"0AL": 1}),
        "S_P": L.single(y, **{"0AP": 1}),
        "W1": k({"0AV": 1, "0DA": 1975}, nf=1),
        "S65": L.single(y, 1950),
        "C0": L.couple(y),
        "C1": k(L.couple(y), nf=1),
        "C2": k(L.couple(y), nf=2),
        "C3": k(L.couple(y), nf=3),
        "C65": L.couple(y, 1950, 1950),
        "C2_P": k(L.couple(y, **{"0AP": 1}), nf=2),
    }


def templates(years):
    out = []
    for y in years:
        for fam, fb in families(y).items():
            old = fam in ("S65", "C65")
            cpl = fam.startswith("C")
            earn = "1AS" if old else "1AJ"
            # moving earnings, with a background
            bgs = {"none": {}, "homehelp": {"7DB": 3000}, "gift": {"7UF": 300}, "vl": {"5TB": 15000},
                   "div": {"2DC": 5000, "2BH": 5000}, "rent": {"4BE": 8000}, "per": {"6NS": 2000, "APS": 4500, "DPS": 0, "CPS": 0, "BPS": 0}}
            for bg, bb in bgs.items():
                for sp in ((0, 20000) if cpl else (None,)):
                    b = {**fb, **bb}
                    if sp:
                        b["1BS" if old else "1BJ"] = sp
                    out.append({"year": y, "fam": fam, "bg": bg, "spouse": sp, "move": earn, "base": b})
            # moving investment / other income on top of earnings E
            for mv in ("2DC", "2DC_2OP", "2TR", "4BE", "5TB", "5KP", "3VG", "2DC_src"):
                for E in (0, 25000, 60000, 150000):
                    b = dict(fb)
                    if E:
                        if cpl:
                            b[earn] = E // 2
                            b["1BS" if old else "1BJ"] = E - E // 2
                        else:
                            b[earn] = E
                    if mv == "2DC_2OP":
                        b["2OP"] = 1
                    out.append({"year": y, "fam": fam, "bg": f"E{E}", "spouse": None, "move": mv, "base": b})
    for i, t in enumerate(out):
        t["tid"] = i
    return out


XS = list(range(0, 150000, 7)) + list(range(150000, 800001, 50))


def boxes_at(t, x):
    b = dict(t["base"])
    mv = t["move"]
    if mv in ("2DC_2OP",):
        b["2DC"] = b.get("2DC", 0) + x
    elif mv == "2DC_src":                       # dividends with the social levies withheld at source (2BH)
        b["2DC"] = b.get("2DC", 0) + x
        b["2BH"] = b.get("2BH", 0) + x
    else:
        b[mv] = b.get(mv, 0) + x
    return {k: v for k, v in b.items() if v != 0 or k in ("DPS", "CPS", "BPS")}


def src_ps(t, b):
    """Social levies withheld at source on 2BH (not on the return): 17.2 %."""
    return 0.172 * b.get("2BH", 0)


def burden_line(t, b, fields):
    return (fields["IMPNET"] + fields["PSNET"] + fields["CHRAPRES"] + fields["CDHR"] + L.vl_paid(b) + src_ps(t, b))


def eval_points(t, xs):
    lines = []
    bxs = []
    for i, x in enumerate(xs):
        b = boxes_at(t, x)
        bxs.append(b)
        lines.append(L.line(str(i), t["year"], b))
    s = subprocess.run([L.LEAN], input="\n".join(lines) + "\n", capture_output=True, text=True).stdout
    res = [None] * len(xs)
    for ln in s.splitlines():
        p = ln.split(";")
        if p[0] == "ERR":
            continue
        i = int(p[0])
        f = {n: float(p[1 + j].split("=")[1]) for j, n in enumerate(NAMES)}
        res[i] = (burden_line(t, bxs[i], f), f)
    return res, bxs


def scan(t):
    res, bxs = eval_points(t, XS)
    flagged = []
    for i in range(len(XS) - 1):
        if res[i] is None or res[i + 1] is None:
            continue
        dx = XS[i + 1] - XS[i]
        db = res[i + 1][0] - res[i][0]
        r = db / dx
        if r > 0.6 or r < -1e-9:
            flagged.append((i, r, db))
    # merge consecutive flagged steps into intervals
    intervals = []
    for i, r, db in flagged:
        if intervals and intervals[-1]["i_hi"] == i and (r > 1) == (intervals[-1]["rmax"] > 1) and (r < 0) == (intervals[-1]["rmin"] < 0):
            iv = intervals[-1]
            iv["i_hi"] = i + 1; iv["sum_db"] += db; iv["rmax"] = max(iv["rmax"], r); iv["rmin"] = min(iv["rmin"], r)
            iv["steps"].append(i)
        else:
            intervals.append({"i_lo": i, "i_hi": i + 1, "sum_db": db, "rmax": r, "rmin": r, "steps": [i]})
    notches = []
    for iv in intervals:
        x_lo, x_hi = XS[iv["i_lo"]], XS[iv["i_hi"]]
        iv.update({"x_lo": x_lo, "x_hi": x_hi, "mean_rate": iv["sum_db"] / (x_hi - x_lo)})
        refine = [s for s in iv["steps"] if abs(res[s + 1][0] - res[s][0]) > (XS[s + 1] - XS[s])] or []
        refine = (iv["steps"][:2] + refine[:6] + [s for s in iv["steps"] if res[s + 1][0] < res[s][0]][:4])
        for s in sorted(set(refine)):
            xs = list(range(XS[s], XS[s + 1] + 1))
            rr, bb = eval_points(t, xs)
            best = None
            for j in range(len(xs) - 1):
                if rr[j] is None or rr[j + 1] is None:
                    continue
                d = rr[j + 1][0] - rr[j][0]
                if best is None or abs(d) > abs(best[1]):
                    best = (j, d)
            if best is None:
                continue
            j, d = best
            f0, f1 = rr[j][1], rr[j + 1][1]
            moved = {k: [f0[k], f1[k]] for k in NAMES if f0[k] != f1[k]}
            notches.append({"tid": t["tid"], "year": t["year"], "fam": t["fam"], "bg": t["bg"], "spouse": t["spouse"],
                            "move": t["move"], "x": xs[j], "d_burden_per_euro": d, "moved": moved,
                            "boxes": bb[j], "burden0": rr[j][0], "burden1": rr[j + 1][0]})
        del iv["steps"]
    meta = {k: t[k] for k in ("tid", "year", "fam", "bg", "spouse", "move")}
    return [{**meta, **{k: v for k, v in iv.items() if k not in ("i_lo", "i_hi")}} for iv in intervals], notches


if __name__ == "__main__":
    years = [int(a) for a in sys.argv[1:]] or [2020, 2021, 2022, 2023, 2024, 2025]
    ts = templates(years)
    print("templates", len(ts), "points each", len(XS), flush=True)
    with mp.Pool(L.NCPU) as pool, open(f"{OUT}/scan_intervals.jsonl", "w") as fi, open(f"{OUT}/scan_notches.jsonl", "w") as fn:
        for k, (ivs, ns) in enumerate(pool.imap_unordered(scan, ts, chunksize=1)):
            for iv in ivs:
                fi.write(json.dumps(iv) + "\n")
            for n in ns:
                fn.write(json.dumps(n) + "\n")
            if k % 100 == 0:
                print("done", k, flush=True)
    print("SCAN-DONE", flush=True)
