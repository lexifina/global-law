# RED T7: the plan's dollars recomputed from the statute text, not from the Lean.
# Facts (scenario S4): age 30, compensation $300,000, $30,000 spare cash, $100,000 pre-tax rollover IRA, an empty
# Trump account kept from childhood, IRA deduction denied by s.219(g), no Roth contribution (s.408A(c)(3)).
from fractions import Fraction as F

LIMIT = 7000          # s.219(b)(5)(A) as indexed for 2025; s.408(a)(1) caps what the account may accept
R_NOW, R_LATER, PREMIUM = F(35, 100), F(24, 100), F(25, 100)


def taxable_part(distribution, basis, year_end_value):
    """s.72(e)(8) with s.408(d)(2)(C) and the flush sentence: basis is spread over the year-end value of the
    contract plus the year's distributions."""
    excluded = distribution * F(basis, year_end_value + distribution)
    return distribution - excluded


# --- the plan: two non-deductible contributions (s.408(o)) to the Trump account, then convert it (s.408A(d)(3)(C))
contrib = [LIMIT, LIMIT]
ta_basis = sum(contrib)                     # s.72(e)(6): investment in the contract
converted = sum(contrib)
# s.530A(h)(4): s.408(d)(2) "applied separately with respect to Trump Accounts and other individual retirement
# plans" -> the contract is the Trump account alone; it is empty at the close of the year
plan_income = taxable_part(converted, ta_basis, 0)

# --- the same dollars through the ordinary IRA: one contract with the $100,000 (s.408(d)(2)(A))
ordinary_income = taxable_part(converted, sum(contrib), 100000)

# --- closing (h)(4) after 18: the Trump account joins that one contract -> same figure
closed_income = ordinary_income


def worth(cash, roth, pretax, basis, income):
    """The findings file's stated objective: tax-free money at 1+premium, pre-tax at (1+premium)(1-later rate),
    cash and basis at par, less tax now on income recognised."""
    return cash + (1 + PREMIUM) * roth + (1 + PREMIUM) * (1 - R_LATER) * pretax + basis - R_NOW * income


start = worth(30000, 0, 100000, 0, 0)
plan = worth(30000 - converted, converted, 100000, 0, plan_income)
ordinary = worth(30000 - converted, converted, 100000 - ordinary_income, sum(contrib) - (converted - ordinary_income),
                 ordinary_income)
print('income recognised, plan                :', float(plan_income))
print('income recognised, ordinary IRA / closed:', float(ordinary_income), '(Lean, whole dollars: 12281)')
print('tax at 35% avoided on the conversion    :', float(R_NOW * ordinary_income))
print('worth at start (baseline)               :', float(start))
print('worth after the plan                    :', float(plan), ' gain', float(plan - start))
print('worth after the ordinary backdoor/closed:', float(ordinary), ' gain', float(ordinary - start))
print('gain with no growth premium             :',
      float((30000 - 14000) + 14000 + (1 - R_LATER) * 100000 - (30000 + (1 - R_LATER) * 100000)))
# realistic account: $5,000 of seed money and growth, which s.530A(d)(2) keeps out of basis
seed = 5000
inc = taxable_part(converted + seed, ta_basis, 0)
start5 = worth(30000, 0, 100000 + seed, 0, 0)
plan5 = worth(30000 - converted, converted + seed, 100000, 0, inc)
print('with $5,000 pre-tax in the Trump account: income', float(inc), ' gain', float(plan5 - start5))
assert plan_income == 0 and plan - start == 3500 and start == 125000
assert round(ordinary_income) == 12281 and plan5 - start5 == 3250
print('agrees with Lean: baseline 125000, plan 128500, +3500, closed-rule income 12281, seeded account +3250')
