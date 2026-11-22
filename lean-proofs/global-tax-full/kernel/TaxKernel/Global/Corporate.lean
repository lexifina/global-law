import TaxKernel.Global.Master

/-!
# TaxKernel.Global.Corporate (2.0.0): corporate income tax at model level (OECD 1200)

    taxable profit = profit + add-backs − exempt income − participation exemption + disallowed interest
                     − loss offset (capped)
    CIT            = max (schedule(taxable profit), minimum tax)          (small-business schedule below a turnover limit)
    top-up         = max 0 (minRate × (income − carve-out) − covered taxes)    (domestic minimum top-up, model level)

Parts (each a plain function of `CorpRegime` and the entity's `Company`):
* `CorpRegime`: the rate schedule; a small-business schedule chosen by turnover (`smallTurnover`) and, from kernel
  2.3.0, also by the number of employees (`smallEmployees`: LT Pelno mokesčio įstatymas 5 str. 2 d.); a minimum tax on
  turnover or assets (pay the higher: KH, many African statutes); loss carry-forward with a cap (DE KStG § 8 (1) with
  EStG § 10d (2): in full up to 1 million, then a share of the excess); interest limitation by EBITDA with a de minimis
  that is either an allowance or an all-or-nothing threshold (DE EStG § 4h: 30 % of EBITDA, "Freigrenze" 3 million;
  ATAD art. 4); thin capitalisation by a debt/equity ratio; participation exemption of a share of dividends from a
  minimum stake (DE KStG § 8b (1) and (5): 95 % in effect).
* `topUp`: a QDMTT-style top-up to a minimum effective rate (model level: covered taxes and income given).
Trade/municipal profit taxes on a "base amount × local multiplier" (DE GewStG §§ 11, 16) are `twoStage`
(`Property.lean`). Where both an EBITDA rule and a thin-cap rule apply, this part takes the larger disallowance; a
statute that applies them in sequence writes its own order.

Theorems: `lossOffset_le_losses`, `lossOffset_le_income`, `citTax_ge_regular`, `citTax_ge_minimum`,
`interestDisallowed_nonneg`, `topUp_floor`, `topUp_nonneg`.
-/

namespace TaxKernel.Global
open TaxKernel

structure CorpRegime where
  name : String
  sched : Schedule
  round : Rule := {}
  /-- small-business schedule when turnover ≤ `smallTurnover` (−1: no such regime) -/
  smallTurnover : Int := -1
  smallSched : Schedule := Schedule.flat 0
  /-- minimum tax: bp of turnover (or of assets if `minOnAssets`), plus a fixed amount; the higher of the regular
  and the minimum tax is due -/
  minBp : Int := 0
  minOnAssets : Bool := false
  minFixed : Int := 0
  /-- losses offset in full up to `lossFull` of income (−1: no cap), then `lossExcessBp` of the excess -/
  lossFull : Int := -1
  lossExcessBp : Int := 10000
  /-- interest limitation: net interest above `interestCapBp` of EBITDA not deductible (−1: none) -/
  interestCapBp : Int := -1
  interestSafe : Int := 0
  /-- `true`: all interest deductible when it is below `interestSafe` (threshold); `false`: `interestSafe` is an allowance -/
  safeIsThreshold : Bool := false
  /-- thin cap: interest on debt above `thinCapPct` % of equity not deductible (−1: none) -/
  thinCapPct : Int := -1
  /-- participation exemption: bp of dividends exempt when the stake ≥ `participationMinBp` -/
  participationBp : Int := 0
  participationMinBp : Int := 0
  /-- kernel 2.3.0: the small-business schedule also needs `company.employees ≤ smallEmployees` (−1: no employee
  test, as before). With `smallTurnover = −1` the employee test alone decides. -/
  smallEmployees : Int := -1
  deriving Repr, Inhabited

namespace CorpRegime

def ebitdaOf (co : Company) : Int := if co.ebitda = 0 then co.profit + co.interestExpense else co.ebitda

def interestDisallowed (r : CorpRegime) (co : Company) : Int :=
  let i := pos co.interestExpense
  let cap := divR .down (r.interestCapBp * pos (ebitdaOf co)) BP
  let byEbitda :=
    if r.interestCapBp < 0 then 0
    else if r.safeIsThreshold then (if i < r.interestSafe then 0 else pos (i - cap))
    else pos (i - max r.interestSafe cap)
  let byThin :=
    if r.thinCapPct < 0 ∨ co.debt ≤ 0 then 0
    else divR .down (i * pos (co.debt - divR .down (r.thinCapPct * pos co.equity) 100)) co.debt
  max (pos byEbitda) (pos byThin)

def participationExempt (r : CorpRegime) (co : Company) : Int :=
  if r.participationMinBp ≤ co.participationBp then divR .down (r.participationBp * pos co.dividendsReceived) BP else 0

def beforeLosses (r : CorpRegime) (co : Company) : Int :=
  co.profit + co.addBacks - co.exemptIncome - r.participationExempt co + r.interestDisallowed co

end CorpRegime

/-- Losses brought forward that may be set against `income`: in full up to `full` (−1: no cap), then `excessBp` of
the income above it, never more than the losses. -/
def lossOffset (full excessBp income losses : Int) : Int :=
  if full < 0 then min (pos losses) (pos income)
  else min (pos losses) (min (pos income) full + divR .down (excessBp * pos (pos income - full)) BP)

namespace CorpRegime

def taxableProfit (r : CorpRegime) (co : Company) : Int :=
  let b := r.beforeLosses co
  pos (b - lossOffset r.lossFull r.lossExcessBp b co.lossesForward)

/-- The small-business test: every limit that is set (≥ 0) is met, and at least one is set. -/
def isSmall (r : CorpRegime) (co : Company) : Bool :=
  (decide (0 ≤ r.smallTurnover) || decide (0 ≤ r.smallEmployees))
  && (decide (r.smallTurnover < 0) || decide (co.turnover ≤ r.smallTurnover))
  && (decide (r.smallEmployees < 0) || decide ((co.employees : Int) ≤ r.smallEmployees))

def regularTax (r : CorpRegime) (co : Company) : Int :=
  (if r.isSmall co then r.smallSched else r.sched).tax r.round (r.taxableProfit co)

def minimumTax (r : CorpRegime) (co : Company) : Int :=
  divR .down (r.minBp * pos (if r.minOnAssets then co.assets else co.turnover)) BP + r.minFixed

/-- The CIT due: the higher of the regular and the minimum tax. -/
def citTax (r : CorpRegime) (co : Company) : Int := max (r.regularTax co) (r.minimumTax co)

/-- The CIT as a charge (base = profit before losses, relieved = taxable profit). -/
def citCharge (r : CorpRegime) (co : Company) (statute : String) (credit : Int := 0) : Charge :=
  charge .cit r.name (r.beforeLosses co) (fun _ => r.taxableProfit co) (fun _ => r.citTax co) credit
    (statute := statute)

end CorpRegime

/-- Domestic minimum top-up (model level): raises covered taxes to `minBp` of the income above a carve-out. -/
def topUp (minBp income carveOut covered : Int) : Int :=
  pos (divR .down (minBp * pos (income - carveOut)) BP - covered)

/-! ## Theorems -/

theorem lossOffset_le_losses (full e income losses : Int) : lossOffset full e income losses ≤ pos losses := by
  unfold lossOffset; split <;> omega

theorem bp_share_le (e x : Int) (he' : e ≤ BP) (hx : 0 ≤ x) : divR .down (e * x) BP ≤ x := by
  have h1 : e * x ≤ BP * x := Int.mul_le_mul_of_nonneg_right he' hx
  simp only [divR, BP] at *
  generalize e * x = y at *
  omega

/-- The offset never exceeds the income when the excess share is at most 100 %. -/
theorem lossOffset_le_income (full e income losses : Int) (he' : e ≤ BP) :
    lossOffset full e income losses ≤ pos income := by
  unfold lossOffset
  have hp := pos_nonneg income
  have hq := pos_nonneg (pos income - full)
  have := bp_share_le e (pos (pos income - full)) he' hq
  split
  · omega
  · generalize divR .down (e * pos (pos income - full)) BP = s at *
    simp only [pos] at *; omega

/-- Kernel 2.3.0: without an employee test (the default) the small-business test is the turnover test of 2.0-2.2. -/
theorem CorpRegime.isSmall_turnoverOnly (r : CorpRegime) (co : Company) (h : r.smallEmployees < 0) :
    r.isSmall co = (decide (0 ≤ r.smallTurnover) && decide (co.turnover ≤ r.smallTurnover)) := by
  unfold CorpRegime.isSmall
  by_cases h1 : 0 ≤ r.smallTurnover <;> by_cases h2 : co.turnover ≤ r.smallTurnover <;>
    simp [h, h1, h2] <;> omega

/-- A small company meets the employee limit when one is set. -/
theorem CorpRegime.isSmall_employees (r : CorpRegime) (co : Company) (hs : r.isSmall co = true)
    (he : 0 ≤ r.smallEmployees) : (co.employees : Int) ≤ r.smallEmployees := by
  simp [CorpRegime.isSmall] at hs
  omega

/-- A small company meets the turnover limit when one is set. -/
theorem CorpRegime.isSmall_turnover (r : CorpRegime) (co : Company) (hs : r.isSmall co = true)
    (ht : 0 ≤ r.smallTurnover) : co.turnover ≤ r.smallTurnover := by
  simp [CorpRegime.isSmall] at hs
  omega

theorem citTax_ge_regular (r : CorpRegime) (co : Company) : r.regularTax co ≤ r.citTax co := by
  unfold CorpRegime.citTax; omega

theorem citTax_ge_minimum (r : CorpRegime) (co : Company) : r.minimumTax co ≤ r.citTax co := by
  unfold CorpRegime.citTax; omega

theorem interestDisallowed_nonneg (r : CorpRegime) (co : Company) : 0 ≤ r.interestDisallowed co := by
  unfold CorpRegime.interestDisallowed; simp only [pos]; omega

/-- Covered taxes plus the top-up reach the minimum on the excess profit. -/
theorem topUp_floor (minBp income carveOut covered : Int) :
    divR .down (minBp * pos (income - carveOut)) BP ≤ covered + topUp minBp income carveOut covered := by
  unfold topUp; simp only [pos]; omega

theorem topUp_nonneg (minBp income carveOut covered : Int) : 0 ≤ topUp minBp income carveOut covered :=
  pos_nonneg _

end TaxKernel.Global
