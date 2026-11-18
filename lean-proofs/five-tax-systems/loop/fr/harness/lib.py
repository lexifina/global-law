"""Runners for the French loophole catalogue (~/cmp/loop/fr). frloop = frtax + FrLoop.Extra additions.

Burden = net income tax + CEHR + CDHR + social levies assessed on the return + micro flat levy (as
~/fr/harness/loop_lib.py). The family-benefit part is a Python port of ~/cmp/compare/lean/Compare/Fr.lean
(contributions on pay, allocations familiales 2025); the port reproduces that file's #guard values (selftest()).
"""
import os, subprocess, concurrent.futures as cf

EXE = os.path.expanduser("~/cmp/loop/fr/lean/.lake/build/bin/frloop")
NCPU = 8
KEYS = ("RNG", "RNI", "IDRS", "IDEC", "ITRED", "CITOT", "PFU", "IDRS4", "IAVCR", "IMPNET", "REVKIRE", "PSNET",
        "CHRAPRES", "CDHR")


def line(cid, year, boxes, extra=None):
    s = f"{cid};{year};" + ",".join(f"{k}={int(v)}" for k, v in boxes.items())
    if extra:
        s += ";" + ",".join(f"{k}={int(v)}" for k, v in extra.items())
    return s


def _chunk(t):
    return subprocess.run([EXE], input=t, capture_output=True, text=True).stdout


def run(cases, jobs=NCPU):
    """cases: (id, year, boxes[, extra]). Returns {id: {KEY: value}}."""
    lines = [line(*c) for c in cases]
    out = {}
    if not lines:
        return out
    k = max(400, len(lines) // jobs + 1)
    chunks = ["\n".join(lines[i:i + k]) + "\n" for i in range(0, len(lines), k)]
    with cf.ThreadPoolExecutor(min(jobs, len(chunks))) as ex:
        for s in ex.map(_chunk, chunks):
            for ln in s.splitlines():
                p = ln.split(";")
                if p[0] == "ERR":
                    continue
                d = {}
                for kv in p[1:]:
                    a, _, v = kv.partition("=")
                    if a in KEYS:
                        d[a] = int(v)
                    elif a == "NBPT":
                        d[a] = v
                out[p[0]] = d
    return out


def one(boxes, extra=None, year=2025):
    return run([("x", year, boxes, extra)])["x"]


def vl_paid(b):
    def pct(p, x):
        return (2 * p * x + 10000) // 20000
    g = b.get
    return (pct(100, g("5TA", 0) + g("5UA", 0) + g("5VA", 0)) + pct(170, g("5TB", 0) + g("5UB", 0) + g("5VB", 0))
            + pct(220, g("5TE", 0) + g("5UE", 0) + g("5VE", 0)))


def burden(b, o):
    return o["IMPNET"] + o["CHRAPRES"] + o["CDHR"] + o["PSNET"] + vl_paid(b)


def tax3(o):
    """income tax + CEHR + CDHR (no levies)."""
    return o["IMPNET"] + o["CHRAPRES"] + o["CDHR"]


# ---------------------------------------------------------------- port of Compare/Fr.lean (2025)
PASS = 47100


def rnd(n, d):
    return (2 * n + d) // (2 * d)


def contrib(g):
    """(ssc, csgCrds, csgDeductible) in euros on annual gross pay g."""
    g = max(0, g)
    t1 = min(g, PASS)
    t2 = max(0, min(g, 8 * PASS) - PASS)
    bc = lambda r, x: rnd(r * x, 100)  # cents
    cents = (bc(690, t1) + bc(40, g) + bc(315, t1) + bc(864, t2) + bc(86, t1) + bc(108, t2)
             + (bc(14, t1 + t2) if g > PASS else 0))
    base = 100 * g - rnd(175 * min(g, 4 * PASS), 100)
    ded, non, crds = rnd(680 * base, 10000), rnd(240 * base, 10000), rnd(50 * base, 10000)
    return rnd(cents, 100), rnd(ded + non + crds, 100), rnd(ded, 100)


def taxable_salary(g):
    s, _, d = contrib(g)
    return max(0, g) - s - d


def _monthly(bmaf, tier, n, k):
    if n < 2:
        return 0
    r2, r3, ra = {1: (3200, 4100, 1600), 2: (1600, 2050, 800), 3: (800, 1025, 400)}[tier]
    return rnd(r2 * bmaf, 10000) + (n - 2) * rnd(r3 * bmaf, 10000) + k * rnd(ra * bmaf, 10000)


def _month(bmaf, r, n, k):
    c1, c2 = 62474 + 6246 * n, 87430 + 6246 * n
    tier = 1 if r <= c1 else 2 if r <= c2 else 3
    m = _monthly(bmaf, tier, n, k)
    comp = lambda c: max(0, (100 * c + 12 * m - 100 * r) // 12)
    return m + (comp(c1) if tier == 2 else comp(c2) if tier == 3 else 0)


def allocations(r, ages):
    kids = [a for a in ages if a < 20]
    n = len(kids)
    k0 = len([a for a in kids if a >= 14])
    k = k0 - 1 if n == 2 and k0 > 0 else k0
    return rnd(3 * _month(46644, r, n, k) + 9 * _month(47437, r, n, k), 100)


def af_net(r, ages):
    a = allocations(r, ages)
    return a - rnd(50 * a, 10000)


def selftest():
    assert contrib(45964)[0] == 5199 and contrib(45964)[1] == 4380, contrib(45964)
    assert contrib(76761)[0] == 8436
    assert allocations(40000, [6, 11]) == 1814 and rnd(50 * 1814, 10000) == 9
    return True


if __name__ == "__main__":
    print(selftest(), one({"0AC": 1, "1AJ": 50000}))
