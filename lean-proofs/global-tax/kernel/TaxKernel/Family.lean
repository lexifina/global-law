import TaxKernel.Schedule
import TaxKernel.Allowance
import TaxKernel.Credit

/-!
# TaxKernel.Family (added in 1.2 for the 38): child scales, income attribution, allowances given at the lowest rates, allowances that spill into another levy, stepped withdrawals

**Child scales.** Amounts that depend on how many children there are, written three ways in the statutes:
* by rank (`perChildByRank [a1, a2, a3] n`: the first child a1, the second a2, every later one the last entry;
  HR Zakon o porezu na dohodak čl. 14 (factors 0.5, 0.7, 1.0, 1.4 … of the basic allowance), SI ZDoh-2 čl. 115);
* by family size (`perChildByCount [b1, b2, b3] n`: every child gets the entry for the family's size; HU Szja tv.
  29/A: the family tax base allowance per child per month is larger for two and for three or more children);
* as cumulative totals (`familyTotal [t1, t2, t3, t4] extra n`: the statute prints the total for 1, 2, 3, 4
  children and an amount for each further child; BE CIR 92 art. 132 supplements to the tax-free sum).

**Income attribution between spouses** (`attributeIncome a b pct cap`, BE CIR 92 art. 87-88 "quotient conjugal"):
part of the higher earner's income is taxed as the other spouse's: `pct` of the couple's combined income minus the
spouse's own, never negative, at most `cap`. Returns the two incomes after the transfer (their sum is unchanged,
`attributeIncome_sum`).

**An allowance given at the lowest rates** (`lowBandReduction s exempt`, BE CIR 92 art. 131 and 134: the tax on the
"quotité du revenu exemptée d'impôt", computed on the brackets from the lowest, is subtracted from the tax on the
whole income): the reduction is `s.ticks exempt`. Unlike a zero band in front of the schedule (`withZeroBand`,
DE/AT/LU Grundfreibetrag), it is worth the same to every taxpayer who can use it; for a convex schedule with no
tax on nothing, the zero band is never worth less (`lowBand_le_zeroBand`: `s.ticks (x - a) ≤ s.ticks x - s.ticks a`).

**An allowance that spills into another levy** (`spillAllowance allowance income rate`, HU Szja tv. 29/A-29/B and
Tbj. 26 §: the family tax base allowance the income cannot absorb reduces the employee's contributions by 15 % of
the unused part): returns the taxable income and the value of the unused part at `rate`.

**A stepped withdrawal** (`SteppedTaper`): an amount reduced by `perStep` for every *complete* `step` of income
above `start` (GR ΚΦΕ ν. 4172/2013 art. 16: "μειώνεται κατά είκοσι (20) ευρώ ανά χίλια (1.000) ευρώ"), never below
`floor`. `toTaper` gives the proportional reading (`perStep/step` of every unit, a `Taper`); whether a statute
means steps or proportion is a reading question to settle with the official calculator. A stepped taper is a
staircase: each step boundary is a notch of `perStep` (`SteppedTaper.stepped_notch`), and it never withdraws
more than the proportional reading (`SteppedTaper.proportional_le_stepped`).

**Phase-in from a threshold** (FI TVL 105 § ansiotulovähennys, earned-income deductions): use `Credit.value c
(earn - phaseStart) inc` (the phase-in base is `pos earn`), the same `Credit` with a shifted base; the same holds for
a deduction rather than a credit.

**A contribution base reduced by a taper** (HR Zakon o doprinosima, 2024: the pension base reduced by a fixed
amount at low pay, withdrawn by half of the excess): `reducedBase t earn = pos (earn − t.amount earn)`, then charge
the `Contribution` on it; inside the taper band the marginal contribution rate rises by `num/den` (as `taper_marginal`).
-/

namespace TaxKernel

/-- Total of per-child amounts by rank (the `i`-th child gets `amounts[i]`, later children the last entry). -/
def perChildByRank (amounts : List Int) (n : Nat) : Int :=
  (List.range n).foldl (fun acc i => acc + amounts.getD i (amounts.getLastD 0)) 0

/-- Total when every child gets the amount for the family's size (`byCount[n-1]`, the last entry beyond the list). -/
def perChildByCount (byCount : List Int) (n : Nat) : Int :=
  if n = 0 then 0 else (n : Int) * byCount.getD (n - 1) (byCount.getLastD 0)

/-- Cumulative totals for 1, 2, … children and `extra` for each child beyond the list. -/
def familyTotal (totals : List Int) (extra : Int) (n : Nat) : Int :=
  if n = 0 then 0
  else if n ≤ totals.length then totals.getD (n - 1) 0
  else totals.getLastD 0 + extra * ((n - totals.length : Nat) : Int)

/-- BE quotient conjugal: the amount moved from `a` to `b` (`pct` bp of `a + b` less `b`, in `[0, cap]`). -/
def attributedAmount (a b pct cap : Int) : Int := min (pos cap) (pos (pct * (a + b) / BP - b))

/-- The two incomes after attribution. -/
def attributeIncome (a b pct cap : Int) : Int × Int :=
  (a - attributedAmount a b pct cap, b + attributedAmount a b pct cap)

/-- The reduction for a tax-free amount taxed on the lowest bands (ticks). -/
def lowBandReduction (s : Schedule) (exempt : Int) : Int := s.ticks (pos exempt)

/-- Tax (ticks) on `income` less the low-band reduction for `exempt`, never below 0. -/
def taxAfterLowBand (s : Schedule) (exempt income : Int) : Int := pos (s.ticks income - lowBandReduction s exempt)

/-- The taxable income and the value (units, rounded down) at `rate` bp of the part of `allowance` that `income`
cannot absorb. -/
def spillAllowance (allowance income rate : Int) : Int × Int :=
  (taxableAfter allowance income, rate * unusedAllowance allowance income / BP)

/-- A contribution base reduced by a (tapered) amount. -/
def reducedBase (t : Taper) (earn : Int) : Int := pos (earn - t.amount earn)

structure SteppedTaper where
  full : Int
  start : Int := 0
  /-- removed for each complete step -/
  perStep : Int
  /-- step width, units (> 0) -/
  step : Int := 1
  floor : Int := 0
  deriving Repr, DecidableEq, Inhabited

namespace SteppedTaper
def steps (t : SteppedTaper) (inc : Int) : Int := pos (inc - t.start) / t.step
def amount (t : SteppedTaper) (inc : Int) : Int := max t.floor (t.full - t.perStep * t.steps inc)
/-- The proportional reading: `perStep/step` of every unit above `start`. -/
def toTaper (t : SteppedTaper) : Taper :=
  { full := t.full, start := t.start, num := t.perStep, den := t.step, floor := t.floor }
def WellFormed (t : SteppedTaper) : Prop := 0 < t.step ∧ 0 ≤ t.perStep ∧ t.floor ≤ t.full
end SteppedTaper

end TaxKernel
