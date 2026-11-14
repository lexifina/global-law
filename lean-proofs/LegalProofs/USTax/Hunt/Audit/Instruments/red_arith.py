"""T7. Independent arithmetic for CANDIDATE 1, written from the statute text, not from the Lean.

Facts: $100,000 of fund shares held (basis 100,000, bought day 5 of year 1); the market is flat in year 1 and the
position is worth 105,000 at the end of year 2, when it is sold. Other short-term gain 50,000 a year.
A RIC pays a capital gain dividend of 10,000 on a 100,000 purchase (ex-date day 130).
Rates (2025, top bracket): ordinary 37% (s.1(j)); net capital gain 20% (s.1(h)(1)(D)); s.1411 3.8% on both.
Tax of year 1 is carried to the end of year 2 at 4%.
"""
from fractions import Fraction as F

ORD, LT, NIIT = F(37, 100), F(20, 100), F(38, 1000)


def year_tax(st, lt):
    """ss.1222, 1(h), 1211(b): net the two baskets; a net loss is deductible up to 3,000 against ordinary income."""
    if st >= 0 and lt >= 0:
        return st * (ORD + NIIT) + lt * (LT + NIIT)
    net = st + lt
    if net >= 0:  # one basket negative: what is left keeps the character of the positive basket
        return net * ((LT + NIIT) if st < 0 else (ORD + NIIT))
    return -min(3000, -net) * ORD  # carryover ignored: not reached below


def fv(y1, y2):
    return y1 * F(104, 100) + y2


def scenario(name, st1, lt1, st2, lt2):
    t = fv(year_tax(st1, lt1), year_tax(st2, lt2))
    print(f"{name:66s} y1 ST {st1:>7} LT {lt1:>6} | y2 ST {st2:>6} LT {lt2:>5} | tax FV {float(t):>10.2f}")
    return t


G = 50000
DIV = 10000
# Baseline: nothing sold until the end of year 2; held more than 1 year: 5,000 long-term (s.1222(3)).
base = scenario("hold the fund", G, 0, G, 5000)

# Sold the day after the ex-date (held 1 day): dividend LT (s.852(b)(3)(B)); loss 10,000 on "such share", held 6 months
# or less: long-term to the extent of the dividend (s.852(b)(4)(A)). Replacement fund held day 130..729 = 599 days.
sold1 = scenario("buy the dividend, sell next day", G, DIV - DIV, G, 5000)

# Sold after 33 days without a wash sale: same, 33 days is still 6 months or less.
sold33 = scenario("buy the dividend, sell after 33 days", G, DIV - DIV, G, 5000)

# Held 201 days (more than 6 months, s.852(b)(4)(A)(ii) not met; 1 year or less, s.1222(2)): short-term loss.
hold201 = scenario("buy the dividend, hold 201 days", G - DIV, DIV, G, 5000)

# The plan. Day 129 buy at 100,000. Day 130 (ex): dividend 10,000 LT. Sell at 90,000: loss 10,000, LT under (b)(4)(A),
# but a share is bought the same day so no deduction (s.1091(a)); new share basis = 100,000 + (90,000 - 90,000)
# (s.1091(d)); holding period includes the 1 day (s.1223(3)). Day 162: sell new share at 90,000: loss 10,000, held
# 33 days (short-term, s.1222(2)); the new share received no capital gain dividend so (b)(4)(A)(i) is not met.
# No acquisition within 30 days before/after day 162 (replacement bought day 130; the first purchase, day 129, is
# 33 days back). Then the first fund again: day 162..729 = 567 days, long-term.
plan = scenario("PLAN: wash sale on the ex-date, sell the replacement day 162", G - DIV, DIV, G, 5000)

# Closed gap: the (b)(4)(A) amount follows the s.1091(d) basis: loss on the replacement is long-term.
closed = scenario("PLAN under the closed-gap rule", G, DIV - DIV, G, 5000)

print()
print(f"baseline tax FV            {float(base):.2f}   (Lean: 42806)")
print(f"plan tax FV                {float(plan):.2f}   (Lean: 41038)")
print(f"saving, future value       {float(base - plan):.2f}   (Lean: 1768)")
print(f"saving, in year-1 dollars  {float((base - plan) / F(104, 100)):.2f}   = dividend x (40.8% - 23.8%) = {float(DIV * (ORD - LT)):.2f}")
print(f"hold 201 days saving       {float(base - hold201):.2f}   (identical: the plan adds no dollars to the known variant)")
print(f"closed-gap saving          {float(base - closed):.2f}")
assert int(base) == 42806 and int(plan) == 41038 and int(base) - int(plan) == 1768 and closed == base and hold201 == plan

# --- Is there an economic gain at all? ---------------------------------------------------------------------------
print("\nEconomics, per 100,000 invested for 33 days (dividend rate d of the purchase price):")
save_rate = ORD - LT  # 17 points, only if there is short-term gain to absorb the loss
for d in (F(2, 100), F(5, 100), F(10, 100), F(20, 100)):
    gross = 100000 * d * save_rate
    # round trips: buy, sell+rebuy, sell = 4 trades of ~100,000 notional (ETF), half-spread + fees per trade c
    for c_bp in (0, 2, 5, 10):
        cost = 4 * 100000 * F(c_bp, 10000)
        print(f"  d={float(d):4.0%}  cost/trade {c_bp:>2}bp  gross {float(gross):8.2f}  costs {float(cost):7.2f}  net {float(gross - cost):8.2f}")
print("break-even dividend rate at c bp per trade: d* = 4c/17  ->", ", ".join(f"{c}bp: {float(F(4*c,10000)/save_rate):.3%}" for c in (2, 5, 10, 25)))
print("with no short-term gain to absorb: the ST loss nets against the LT dividend itself -> saving 0 (Lean g=0: 1190 = 1190)")
print("taxpayer in the 0%/15% capital-gain brackets, ordinary 24%: saving = d x (24% - 15%) = 9 points")
