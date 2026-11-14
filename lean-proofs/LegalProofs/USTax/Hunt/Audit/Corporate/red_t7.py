# T7: the plan and the baselines recomputed from the statute text (26 U.S.C. 1202, 351, 358, 1(h), 1411, 11, 301, 316).
# Written from the words, not from the Lean. Amounts in $ thousands, exact fractions.
from fractions import Fraction as F

SHARES, BASIS = 400, F(1000)
CASH, ASSET_FMV, ASSET_BASIS, EP = F(10000), F(30000), F(0), F(10000)
VALUE = CASH + ASSET_FMV                       # one class, no discount
PER_SHARE, BASIS_PS = VALUE / SHARES, BASIS / SHARES
LT = F(20, 100) + F(38, 1000)                  # 1(h)(1)(D) + 1411(a)(1)
CORP = F(21, 100)                              # 11(b)
DOLLAR = F(15000)                              # 1202(b)(4)(B): stock acquired after the applicable date
PCT = F(1)                                     # 1202(a)(5): held 5 years or more -> 100%

def limit(prior_years_gain, basis_disposed_this_year):
    # 1202(b)(1): greater of (A) the dollar limit less eligible gain of prior years (b)(4)(B)(i), (B) 10 x basis disposed
    return max(DOLLAR - min(DOLLAR, prior_years_gain), 10 * basis_disposed_this_year)

def tax_on_sales(sales, prior=F(0)):
    """sales: list of (amount, basis) of ONE issuer's stock in ONE year. Returns (tax, gain taken into account)."""
    gain = sum(a - b for a, b in sales)
    taken = min(gain, limit(prior, sum(b for _, b in sales)))
    excluded = taken * PCT
    return (gain - excluded) * LT, taken       # at 100% there is no "section 1202 gain" (1(h)(7))

# --- the plan
n1 = SHARES // 5
t1, used_C = tax_on_sales([(n1 * PER_SHARE, n1 * BASIS_PS)])
n2 = SHARES - n1
assert F(n2, SHARES) >= F(80, 100)             # 1202(h)(4)(D) / 368(c): P holds control of C
p_basis = n2 * BASIS_PS                        # 358(a)(1)
p_value = n2 * PER_SHARE
built_in = p_value - p_basis                   # 1202(h)(4)(B): gain that 351 left unrecognised at the transfer
p_gain = p_value - p_basis
assert p_gain <= built_in                      # the (h)(4)(B) limit does not bind on an immediate sale
# reading under attack: P is "such corporation" in 1202(b)(1), so nothing of C's limit has been used
t2_sep, _ = tax_on_sales([(p_value, p_basis)])
# closed reading: P stock counts as stock issued by C
t2_same, _ = tax_on_sales([(n1 * PER_SHARE, n1 * BASIS_PS), (p_value, p_basis)])
plan = t1 + t2_sep
one_issuer, _ = tax_on_sales([(VALUE, BASIS)])
# 351 fails (prearranged sale, control not held "immediately after"): the exchange is a taxable sale of C stock
fail351, _ = tax_on_sales([(n1 * PER_SHARE, n1 * BASIS_PS), (p_value, p_basis)])

# --- plain exit: asset sale, then everything out as a dividend
corp_tax = (ASSET_FMV - ASSET_BASIS) * CORP
dist = CASH + ASSET_FMV - corp_tax
ep = EP + (ASSET_FMV - ASSET_BASIS) - corp_tax       # 312, 316(a)(2)
dividend = min(dist, ep)
plain = corp_tax + dividend * LT + max(F(0), dist - dividend - BASIS) * LT

# --- the known alternative: dollar limit in year 1, ten times basis in year 2 (1202(b)(1)(B))
def two_year(sh1):
    ta, used = tax_on_sales([(sh1 * PER_SHARE, sh1 * BASIS_PS)])
    r = SHARES - sh1
    tb, _ = tax_on_sales([(r * PER_SHARE, r * BASIS_PS)], prior=used)
    return ta + tb
best2 = min((two_year(s), s) for s in range(0, SHARES + 1))
lean2 = two_year(160)                           # the split the Lean search printed: 1/5 then 1/4 of the rest in year 1

f = lambda x: f"{float(x):,.1f}"
print("plan, P a separate issuer      ", f(plan), " (Lean 3,855)")
print("one-issuer sale                ", f(one_issuer), " (Lean 5,712)")
print("plan, P stock counted as C's   ", f(t2_same), " (Lean closed-gap 5,712)")
print("plan, section 351 fails        ", f(fail351))
print("plain asset sale + dividend    ", f(plain), " (Lean 14,320)")
print("two-year sale, Lean's split    ", f(lean2), " (Lean 4,283)")
print("two-year sale, best whole-share", f(best2[0]), "selling", best2[1], "shares in year 1")
print("claimed gain vs one-issuer     ", f(one_issuer - plan))
print("gain vs the known two-year plan", f(lean2 - plan), "/", f(best2[0] - plan))
print("extra gain excluded            ", f(used_C + min(p_gain, limit(0, p_basis)) - DOLLAR))
