import TaxCode.Individual.Household

/-!
# §§1401–1402 self-employment tax, §164(f), and the 0.9% additional Medicare tax (§3101(b)(2), §1401(b)(2))

**Units.** Net earnings from self-employment are kept exact in ten-thousandths of a dollar (`se * 9235` is 92.35%
of `se` dollars, i.e. §1402(a)(12)). Taxes are computed exactly and rounded once to the nearest dollar, half up.
Schedule SE and Form 8959 work in cents line by line; the difference is at most a dollar (see FINDINGS.md).

**Who earns what.** `Household` has one `seIncome` and does not say which spouse earned it; this file treats all of
it as the head's, and the head's wages as `wages - wagesSpouse` for the §1402(b)(1) wage-base coordination.
-/

namespace TaxCode.Individual.A
open TaxCode.Individual

/-- The contribution and benefit base under §230 of the Social Security Act for 2025 ($176,100; SSA announcement of
October 2024, printed on 2025 Schedule SE line 7), read by §1402(b)(1)(i). -/
def wageBase2025 : Int := 176100

/-- §1402(a)(12): in lieu of the §164(f) deduction, net earnings are reduced by the product of net earnings and
one-half of the §1401(a) and (b)(1) rates (12.4% + 2.9%)/2 = 7.65%; so net earnings are 92.35% of `se`. In
ten-thousandths of a dollar. -/
def nese10k (se : Int) : Int := se * 9235

/-- §1402(b)(2): self-employment income excludes net earnings "if such net earnings for the taxable year are less
than $400". (In ten-thousandths of a dollar.) -/
def seIncome10k (se : Int) : Int := if nese10k se < 400 * 10000 then 0 else nese10k se

/-- §1402(b)(1): for the §1401(a) tax, self-employment income excludes the part of net earnings in excess of the
contribution and benefit base "minus ... the amount of the wages paid to such individual". -/
def oasdiBase10k (se wages : Int) : Int := min (seIncome10k se) (10000 * max 0 (wageBase2025 - wages))

/-- §1401(a) 12.4% on the wage-base-limited amount plus §1401(b)(1) 2.9% on all self-employment income; rounded
to the nearest dollar (12.4% = 124/1000). -/
def seTaxCore (se wages : Int) : Int :=
  roundDollar (124 * oasdiBase10k se wages + 29 * seIncome10k se) 10000000

/-- §164(f)(1): "one-half of the taxes imposed by section 1401 (other than ... section 1401(b)(2))", exact half
rounded to the nearest dollar. -/
def halfSeTaxCore (se wages : Int) : Int :=
  roundDollar (124 * oasdiBase10k se wages + 29 * seIncome10k se) 20000000

/-- The head's wages, for §1402(b)(1). -/
def headWages (h : Household) : Int := h.wages - h.wagesSpouse

/-- Self-employment tax (§§1401(a), 1401(b)(1)) for the household. -/
def seTax (h : Household) : Int := seTaxCore h.seIncome (headWages h)

/-- §164(f) deduction (an adjustment under §62(a)(1) by §164(f)(2)). -/
def halfSeTax (h : Household) : Int := halfSeTaxCore h.seIncome (headWages h)

/-! ## Properties of the self-employment tax -/

theorem seTaxCore_nonneg (se w : Int) : 0 ≤ seTaxCore se w := by
  unfold seTaxCore oasdiBase10k seIncome10k nese10k roundDollar
  split <;> omega

/-- More self-employment profit never lowers the tax. -/
theorem seTaxCore_mono (se se' w : Int) (h : se ≤ se') : seTaxCore se w ≤ seTaxCore se' w := by
  unfold seTaxCore oasdiBase10k seIncome10k nese10k roundDollar
  split <;> split <;> omega

/-- Above the $400 floor the marginal rate is at most 15.3% × 92.35% ≈ 14.13 cents per dollar, so one dollar of
profit adds at most one dollar of tax (rounding included). -/
theorem seTaxCore_marginal (se w : Int) (h : 434 ≤ se) : seTaxCore (se + 1) w ≤ seTaxCore se w + 1 := by
  unfold seTaxCore oasdiBase10k seIncome10k nese10k roundDollar
  split <;> split <;> omega

/-- The §1402(b)(2) notch: $433 of profit (net earnings $399.88) owes nothing; $434 (net earnings $400.80) owes
$61. One extra dollar of profit costs $61 of tax. -/
theorem seTax_notch : seTaxCore 433 0 = 0 ∧ seTaxCore 434 0 = 61 := by decide

/-- Wage-base coordination: once the individual's wages reach the 2025 base, only the 2.9% tax remains. -/
theorem seTaxCore_above_base (se w : Int) (hw : wageBase2025 ≤ w) :
    seTaxCore se w = roundDollar (29 * seIncome10k se) 10000000 := by
  unfold seTaxCore oasdiBase10k seIncome10k nese10k wageBase2025 at *
  split <;> (congr 1; omega)

/-- Below the wage base (reviewer addition): above the $400 floor and with net earnings plus wages not over the base,
the tax is exactly 15.3% of 92.35% of profit, rounded once. A function that dropped the §1402(a)(12) factor, used
the wrong rates, or always returned 0 fails this. -/
theorem seTaxCore_below_base (se w : Int) (h400 : 400 * 10000 ≤ se * 9235)
    (hb : se * 9235 ≤ 10000 * (wageBase2025 - w)) :
    seTaxCore se w = roundDollar (153 * (se * 9235)) 10000000 := by
  unfold seTaxCore oasdiBase10k seIncome10k nese10k at *
  split
  · omega
  · congr 1; omega

/-- Wage-base coordination (reviewer addition): when wages are under the base but wages plus net earnings exceed
it, the 12.4% applies only to the unused part of the base (§1402(b)(1)) and the 2.9% to all net earnings. -/
theorem seTaxCore_straddle (se w : Int) (h400 : 400 * 10000 ≤ se * 9235) (hw : w ≤ wageBase2025)
    (hb : 10000 * (wageBase2025 - w) ≤ se * 9235) :
    seTaxCore se w = roundDollar (124 * (10000 * (wageBase2025 - w)) + 29 * (se * 9235)) 10000000 := by
  unfold seTaxCore oasdiBase10k seIncome10k nese10k at *
  split
  · omega
  · congr 1; omega

/-- §164(f) is one-half of the tax: the rounded half never differs from half the rounded tax by more than $1. -/
theorem halfSe_close (se w : Int) :
    2 * halfSeTaxCore se w ≤ seTaxCore se w + 2 ∧ seTaxCore se w ≤ 2 * halfSeTaxCore se w + 2 := by
  unfold halfSeTaxCore seTaxCore roundDollar
  generalize 124 * oasdiBase10k se w + 29 * seIncome10k se = t
  omega

/-! ## Additional Medicare tax: §3101(b)(2) on wages and §1401(b)(2) on self-employment income -/

/-- §3101(b)(2)(A)–(C) and §1401(b)(2)(A)(i)–(iii): $250,000 joint return; one-half of that ($125,000) for a married
taxpayer filing separately; $200,000 "in any other case" — which includes a qualifying surviving spouse. Not
indexed. -/
def amtThreshold : Filing → Int
  | .mfj => 250000
  | .mfs => 125000
  | _ => 200000

/-- 0.9% of wages over the threshold, plus 0.9% of self-employment income over the threshold "reduced (but not
below zero) by the amount of wages" (§1401(b)(2)(B)). `seInc10k` is self-employment income in ten-thousandths of a
dollar (already after the $400 floor; a loss is zero, Form 8959 line 8). Rounded once to the nearest dollar. -/
def additionalMedicareCore (f : Filing) (wages seInc10k : Int) : Int :=
  let t := amtThreshold f
  let wageExcess := max 0 (wages - t)
  let seExcess := max 0 (seInc10k - 10000 * max 0 (t - wages))
  roundDollar (9 * (10000 * wageExcess + seExcess)) 10000000

/-- Additional Medicare tax for the household: `wages` (both spouses, as the joint threshold is a combined one) and
self-employment income. `Household.wages` is Form W-2 box 1; the statute reads Medicare wages (box 5). -/
def additionalMedicare (h : Household) : Int :=
  additionalMedicareCore h.filing h.wages (seIncome10k h.seIncome)

/-- The two halves of the additional Medicare tax collapse to one rule: 0.9% of (wages + self-employment income)
over the threshold. So a dollar of wages and a dollar of self-employment income are interchangeable for this tax. -/
theorem additionalMedicare_combined (f : Filing) (w s : Int) (hs : 0 ≤ s) :
    additionalMedicareCore f w s =
      roundDollar (9 * max 0 (10000 * w + s - 10000 * amtThreshold f)) 10000000 := by
  unfold additionalMedicareCore
  dsimp only
  congr 1
  omega

theorem additionalMedicare_nonneg (f : Filing) (w s : Int) : 0 ≤ additionalMedicareCore f w s := by
  unfold additionalMedicareCore roundDollar
  dsimp only
  omega

/-- Under the threshold nothing is owed, whatever the mix of wages and self-employment income. -/
theorem additionalMedicare_below (f : Filing) (w s : Int) (hs : 0 ≤ s)
    (h : 10000 * w + s ≤ 10000 * amtThreshold f) : additionalMedicareCore f w s = 0 := by
  rw [additionalMedicare_combined f w s hs]
  unfold roundDollar
  omega

end TaxCode.Individual.A
