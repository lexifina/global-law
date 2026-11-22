import TaxKernel.Global2.Basket

/-!
# TaxKernel.Global2.CorpRule (2.1.0): CIT with floored and capped minimum taxes, profit rounding, taxable share (1200)

`CorpRule` wraps a 2.0 `CorpRegime` (rates, small-business schedule, losses, interest limitation, participation
exemption: all unchanged) and adds:

* `minTax : Option MinimumTax`: a minimum tax `fixed + bp × turnover (or assets)`, at least `floor`, at most `cap`
  (−1: none), the higher of the regular and the minimum tax due (OHADA "minimum forfaitaire": SN CGI art. 40 0,5 %
  capped at 5 000 000; TG art. 120 1 % with a floor of 20 000; MG Ar fixed + share). `none`: the regime's own 2.0
  `minimumTax` (`ofRegime_tax`: a bare regime gives exactly `CorpRegime.citTax`).
* `step`: the taxable profit rounded down to a multiple (OHADA codes: "toute fraction … inférieure à mille francs est
  négligée": 1000).
* a **taxable share** of the profit (SA/QA: CIT on the non-Saudi/non-Qatari owners' share, zakat on the rest), read
  from the entity's line: `shareKey` the field name (`""`: the whole profit), `shareComplement` when the field gives
  the share that is **not** taxable (SA `"zakatShareBp"`, QA `"exemptShareBp"`). Clamped to 0 … 10 000 bp. The
  minimum tax is not scaled by the share.

    taxable = round_step (share × taxableProfit)        CIT = max (schedule(taxable), minimum)

The charge (`citCharge`) has `base = beforeLosses`, `relieved = taxable`, as 2.0 `CorpRegime.citCharge` and
`R4.citCharge`. Theorems: `ofRegime_tax`, `ofRegime_taxable`, `tax_ge_minimum`, `tax_ge_regular`,
`MinimumTax.amount_le_cap`, `MinimumTax.amount_ge_floor`, `roundStep_le`, `shareOf_le`, `shareOf_nonneg`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-- A minimum tax: `fixed + bp × turnover (or assets)`, at least `floor`, at most `cap` (−1: no cap). -/
structure MinimumTax where
  bp : Int := 0
  onAssets : Bool := false
  fixed : Int := 0
  floor : Int := 0
  cap : Int := -1
  deriving Repr, Inhabited

def MinimumTax.amount (m : MinimumTax) (co : Company) : Int :=
  let x := max (m.fixed + divR .down (m.bp * pos (if m.onAssets then co.assets else co.turnover)) BP) m.floor
  if m.cap < 0 then x else min x m.cap

structure CorpRule where
  regime : CorpRegime
  /-- `none`: the regime's own `minimumTax`; `some m`: this minimum instead -/
  minTax : Option MinimumTax := none
  /-- taxable profit rounded down to a multiple of `step` (≤ 1: no rounding) -/
  step : Int := 1
  /-- the entity's field giving the taxable share of the profit, bp (`""`: all of it) -/
  shareKey : String := ""
  /-- the field gives the share that is not taxable -/
  shareComplement : Bool := false
  deriving Repr, Inhabited

/-- Rounded down to a multiple of `step` (≤ 1: unchanged). -/
def roundStep (step x : Int) : Int := if step ≤ 1 then x else (x / step) * step

namespace CorpRule

def ofRegime (r : CorpRegime) : CorpRule := { regime := r }

/-- The taxable share of the entity's profit, bp. -/
def shareOf (c : CorpRule) (g : CanonGlobal) : Int :=
  if c.shareKey == "" then BP
  else if c.shareComplement then BP - max 0 (min BP (intField g.raw c.shareKey 0))
  else max 0 (min BP (intField g.raw c.shareKey BP))

/-- Taxable profit for a share (bp) of the profit, rounded to the step. -/
def taxable (c : CorpRule) (share : Int) (co : Company) : Int :=
  roundStep c.step (if share = BP then c.regime.taxableProfit co else divR .down (share * c.regime.taxableProfit co) BP)

def regular (c : CorpRule) (share : Int) (co : Company) : Int :=
  (if c.regime.isSmall co then c.regime.smallSched else c.regime.sched).tax c.regime.round (c.taxable share co)

def minimum (c : CorpRule) (co : Company) : Int :=
  match c.minTax with
  | none => c.regime.minimumTax co
  | some m => m.amount co

/-- CIT due: the higher of the regular and the minimum tax. -/
def tax (c : CorpRule) (share : Int) (co : Company) : Int := max (c.regular share co) (c.minimum co)

/-- The CIT charge for an entity (its taxable share read from its line). -/
def citCharge (c : CorpRule) (g : CanonGlobal) (statute : String) (credit : Int := 0) : Charge :=
  let co := g.company
  let sh := c.shareOf g
  charge .cit c.regime.name (c.regime.beforeLosses co) (fun _ => c.taxable sh co) (fun _ => c.tax sh co) credit
    (statute := statute)

/-- 1200 family: the CIT, the statutory withholding on payments abroad, and any extra company charges. -/
def family (c : CorpRule) (name statute : String) (w : Wht) (extra : Company → List Charge := fun _ => []) : Family :=
  { name := s!"1200 {name}", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [c.citCharge g statute] ++ w.charges g.company ++ extra g.company }

end CorpRule

/-! ## Theorems -/

theorem MinimumTax.amount_le_cap (m : MinimumTax) (co : Company) (h : 0 ≤ m.cap) : m.amount co ≤ m.cap := by
  unfold MinimumTax.amount; simp only; split <;> omega

theorem MinimumTax.amount_ge_floor (m : MinimumTax) (co : Company) (h : m.cap < 0 ∨ m.floor ≤ m.cap) :
    m.floor ≤ m.amount co := by
  unfold MinimumTax.amount; simp only; split <;> omega

theorem roundStep_le (step x : Int) : roundStep step x ≤ x := by
  unfold roundStep; split
  · omega
  · have h1 : 0 < step := by omega
    have := Int.ediv_mul_le x (Int.ne_of_gt h1)
    exact this

theorem CorpRule.ofRegime_taxable (r : CorpRegime) (co : Company) :
    (CorpRule.ofRegime r).taxable BP co = r.taxableProfit co := by
  simp [CorpRule.ofRegime, CorpRule.taxable, roundStep]

/-- A bare 2.0 regime as a rule gives exactly the 2.0 CIT. -/
theorem CorpRule.ofRegime_tax (r : CorpRegime) (co : Company) : (CorpRule.ofRegime r).tax BP co = r.citTax co := by
  simp [CorpRule.tax, CorpRule.regular, CorpRule.minimum, CorpRule.ofRegime_taxable, CorpRegime.citTax,
    CorpRegime.regularTax]
  all_goals rfl

theorem CorpRule.tax_ge_minimum (c : CorpRule) (sh : Int) (co : Company) : c.minimum co ≤ c.tax sh co := by
  unfold CorpRule.tax; omega

theorem CorpRule.tax_ge_regular (c : CorpRule) (sh : Int) (co : Company) : c.regular sh co ≤ c.tax sh co := by
  unfold CorpRule.tax; omega

theorem CorpRule.shareOf_le (c : CorpRule) (g : CanonGlobal) : c.shareOf g ≤ BP := by
  unfold CorpRule.shareOf; simp only [BP]; split
  · omega
  · split <;> omega

theorem CorpRule.shareOf_nonneg (c : CorpRule) (g : CanonGlobal) : 0 ≤ c.shareOf g := by
  unfold CorpRule.shareOf; simp only [BP]; split
  · omega
  · split <;> omega

end TaxKernel.Global
