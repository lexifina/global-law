"""T7: the candidate's dollars recomputed from the statute text (not from the Lean).

Facts (FINDINGS, scenario `qtip`): H is dead; $100M sits in a QTIP trust for W (basis = value), no reverse election,
remainder to a family trust for the child C and then the grandchildren. W dies in year 10, C in year 25.
Stated assumptions taken as inputs: 7%/yr growth booked as x1.403 per 5 years; exclusion $15M indexed x1.13 per
5 years, rounded to $10,000; 23.8% income tax on built-in gain; deaths use the exclusion of the start of their
5-year period (the model's convention; `exact=True` uses the year of death instead).

Statute steps used:
  s.2001(c) rate table; s.2502/s.2505 gift tax = tentative tax on cumulative gifts less the credit on the exclusion.
  s.2519 + s.2511: giving up the income interest = gift of the whole trust value (`netgift` applies Reg. 25.2519-1(c)(4)).
  s.2513: with consent each spouse is the donor of half.  s.2207A(b): the trust bears the gift tax.
  s.2652(a)(1)(B),(a)(2): each donor is transferor of his half; s.2632(c): unused GST exemption is allocated.
  s.2632(e): at W's death her unused exemption goes to the trust of which she is transferor.
  s.2044/s.2207A(a)/s.1014(b)(10): QTIP still held at W's death is in her estate, bears its tax, basis stepped up.
  s.2612(a), s.2641, s.2642: at C's death a taxable termination, 40% x inclusion ratio; s.2654(a)(2) basis step-up
  limited by the inclusion ratio.
"""
from fractions import Fraction as F
import json
import sys

G5 = F(1403, 1000)
ITAX = F(238, 1000)


def tent(x):
    table = [(10000, 0, F(18, 100)), (20000, 1800, F(20, 100)), (40000, 3800, F(22, 100)), (60000, 8200, F(24, 100)),
             (80000, 13000, F(26, 100)), (100000, 18200, F(28, 100)), (150000, 23800, F(30, 100)),
             (250000, 38800, F(32, 100)), (500000, 70800, F(34, 100)), (750000, 155800, F(37, 100)),
             (1000000, 248300, F(39, 100))]
    lo = 0
    for hi, base, rate in table:
        if x <= hi:
            return base + (x - lo) * rate
        lo = hi
    return 345800 + (x - 1000000) * F(40, 100)


def excl(period, base=15_000_000, idx=F(113, 100)):
    v = base * idx ** period
    return int((v + 5000) // 10000) * 10000


def gift_tax(cum_before, gift, exclusion):
    raw = tent(cum_before + gift) - tent(cum_before)
    return max(F(0), raw - tent(exclusion)) if cum_before == 0 else None


class Trust:
    """One transferor's share: value, basis, GST-exempt fraction."""
    def __init__(self, v, b, exempt):
        self.v, self.b = F(v), F(b)
        self.af = min(F(1), F(exempt) / self.v) if self.v else F(0)

    def grow(self, n=1):
        self.v *= G5 ** n

    def allocate(self, e):
        self.af = min(F(1), self.af + F(e) / self.v)

    def terminate(self):
        """C dies: taxable termination. Returns (net to grandchildren after built-in income tax, GST tax)."""
        ir = 1 - self.af
        tax = self.v * ir * F(40, 100)
        b = self.b + (self.v - self.b) * ir                # s.2654(a)(2)
        assert tax <= b                                     # paid out of full-basis property, nothing sold
        v, b = self.v - tax, b - tax
        return v - (v - b) * ITAX, tax


def run(plan, V=100_000_000, release_period=0, base=15_000_000, netgift=False, growth=True, exact=False):
    global G5
    G5 = F(1403, 1000) if growth else F(1)
    idx = F(113, 100) if growth else F(1)
    ex = lambda p: excl(p, base, idx)
    V = F(V) * G5 ** release_period
    xfer = F(0)
    w_death_p, c_death_p = 1, 4            # deaths at the END of these periods (years 10 and 25)
    w_death_ex = ex(2 if exact else 1)
    trusts = []
    if plan == "hold":
        q = V * G5 ** (w_death_p + 1 - release_period)
        tax = max(F(0), tent(q) - tent(w_death_ex))        # s.2044, s.2001, s.2010
        xfer += tax
        rem = q - tax                                       # s.2207A(a)
        t = Trust(rem, rem, min(w_death_ex, rem))           # s.1014(b)(10); s.2632(e)
        t.grow(c_death_p - w_death_p)
        trusts = [t]
    else:
        e0 = ex(release_period)
        donors = 2 if plan == "married" else 1
        half = V / donors
        if netgift:
            # Reg. 25.2519-1(c)(4): gift reduced by the tax the trust bears: T = 0.4 (half - T - e0) for half > e0
            tax1 = max(F(0), (half - e0) * F(40, 100) / F(140, 100))
        else:
            tax1 = max(F(0), tent(half) - tent(e0))
        xfer += tax1 * donors
        rest = V - tax1 * donors
        periods_to_w = w_death_p + 1 - release_period
        for i in range(donors):
            t = Trust(rest / donors, rest / donors, min(e0, rest / donors))
            t.grow(periods_to_w)
            if i == 0:                                      # W: s.2632(e) at her death
                unused = w_death_ex - min(e0, rest / donors)
                t.allocate(min(F(unused), t.v * (1 - t.af)))
            t.grow(c_death_p - w_death_p)
            trusts.append(t)
    wealth = F(0)
    for t in trusts:
        net, tax = t.terminate()
        wealth += net
        xfer += tax
    return float(wealth), float(xfer)


if __name__ == "__main__":
    lean = {"hold": (218551878, 191188579), "unmarried": (233157839, 142742786), "married": (269507610, 117172745)}
    out = {}
    print("scenario qtip, release in year 0, model conventions")
    for p in ("hold", "unmarried", "married"):
        w, x = run(p)
        out[p] = {"python_wealth": round(w), "lean_wealth": lean[p][0], "diff": round(w) - lean[p][0],
                  "python_xfer": round(x), "lean_xfer": lean[p][1]}
        print(f"  {p:10s} wealth {w:15.0f} (Lean {lean[p][0]}, diff {w - lean[p][0]:+.0f})   transfer tax {x:15.0f} (Lean {lean[p][1]}, diff {x - lean[p][1]:+.0f})")
    g = run("married")[0] - run("unmarried")[0]
    print(f"  gain from the later spouse: {g:,.0f} (Lean {lean['married'][0] - lean['unmarried'][0]:,})")
    out["gain_yr0"] = round(g)
    # FINDINGS check 1: H dies in year 5 (basis stepped up), W gives up the interest in year 5
    lean5 = {"unmarried": 226135352, "married": 256570861}
    for p in ("unmarried", "married"):
        w, x = run(p, release_period=1)
        print(f"  check 1, yr-5 release {p:10s} wealth {w:15.0f} (Lean {lean5[p]}, diff {w - lean5[p]:+.0f})")
        out[p + "_yr5"] = {"python_wealth": round(w), "lean_wealth": lean5[p]}
    g5 = run("married", release_period=1)[0] - run("unmarried", release_period=1)[0]
    print(f"  check 1 gain: {g5:,.0f} (Lean {lean5['married'] - lean5['unmarried']:,})")
    out["gain_check1"] = round(g5)
    print("sensitivities (Python only)")
    for label, kw in (("no growth", dict(growth=False)), ("net gift per Reg. 25.2519-1(c)(4)", dict(netgift=True)),
                      ("exclusion of the year of death", dict(exact=True)), ("$30M severed trust", dict(V=30_000_000)),
                      ("$30M severed trust, no growth", dict(V=30_000_000, growth=False))):
        a, b, c = run("hold", **kw)[0], run("unmarried", **kw)[0], run("married", **kw)[0]
        print(f"  {label:38s} hold {a:13,.0f}  unmarried {b:13,.0f}  married {c:13,.0f}  gain {c - b:12,.0f}")
        out["sens_" + label] = {"hold": round(a), "unmarried": round(b), "married": round(c), "gain": round(c - b)}
    json.dump(out, open(sys.argv[1], "w"), indent=1) if len(sys.argv) > 1 else None
