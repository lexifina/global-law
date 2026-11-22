import TaxKernel.Global.Capital

/-!
# TaxKernel.Global.Property (2.0.0): recurrent property tax (OECD 4100), net wealth tax (4200)

**Two-stage local taxes** (`twoStage`): value × a statutory ratio ("Steuermesszahl", assessment ratio) = a basic
amount; basic amount × a local multiplier ("Hebesatz", mill rate, taux voté) = the tax. DE GrStG §§ 13, 15, 25 and
GewStG §§ 11, 16 have exactly this form; US property taxes are assessed value × ratio × mill rate.

**Recurrent property tax** (`PropertyTax`): the statutory value (assessed where given, else market value × a ratio),
less an exempt value (homestead), through a schedule (flat, or progressive on annual value as SG), times a local
multiplier; an owner-occupied home may have its own schedule.

**Net wealth tax** (`WealthTax`): each asset counted at a share of its (statutory or market) value, exempt kinds, an
exempt part of the main home, debts deducted, an allowance, an entry threshold (FR IFI-style: no tax below it, the
schedule from 0 above), a schedule, and a cap on income-related taxes + wealth tax as a share of income that may
not remove more than a share of the wealth tax (ES Ley 19/1991 art. 31: 60 % of the taxable income, reduction at most
80 %).

Theorems: `twoStage_mono`, `PropertyTax.amount_mono`, `WealthTax.capped_le`, `WealthTax.capped_ge_floor`;
the entry threshold notch is checked by `#guard` in `examples/Global.lean`.
-/

namespace TaxKernel.Global
open TaxKernel

/-- `value × num/den` (the statutory ratio) then `× multiplierBp`, rounded by `r`; e.g. Grundsteuerwert × 0.31 ‰ ×
Hebesatz 810 % is `twoStage r 31 100000 81000 value`. -/
def twoStage (r : Rule) (num den multiplierBp value : Int) : Int :=
  r.ofTicks (multiplierBp * divR .down (pos value * num) den)

theorem twoStage_mono (r : Rule) (num den m : Int) (hn : 0 ≤ num) (hd : 0 < den) (hm : 0 ≤ m) (hs : 0 < r.step)
    (hmode : r.mode.isMonotoneMode) {x y : Int} (h : x ≤ y) : twoStage r num den m x ≤ twoStage r num den m y := by
  unfold twoStage
  apply Rule.ofTicks_mono _ hs hmode
  apply Int.mul_le_mul_of_nonneg_left _ hm
  apply divR_mono .down den hd (Or.inl rfl)
  exact Int.mul_le_mul_of_nonneg_right (pos_mono h) hn

structure PropertyTax where
  name : String := "property tax"
  /-- statutory ratio on the value (assessment ratio), `ratioNum / ratioDen` -/
  ratioNum : Int := 1
  ratioDen : Int := 1
  /-- exempt value subtracted after the ratio (homestead) -/
  exempt : Int := 0
  /-- rate schedule on the base (bp) -/
  sched : Schedule
  /-- owner-occupied home schedule, if different -/
  homeSched : Option Schedule := none
  /-- local multiplier, bp (Hebesatz 810 % = 81000; 10000 = none) -/
  multiplierBp : Int := 10000
  /-- tax the annual value instead of the capital value -/
  onAnnualValue : Bool := false
  kinds : List AssetKind := [.home, .realEstate, .land]
  round : Rule := {}
  deriving Inhabited

namespace PropertyTax
def value (p : PropertyTax) (a : Asset) : Int :=
  if p.onAnnualValue ∧ 0 ≤ a.annualValue then a.annualValue else a.statutoryValue

def base (p : PropertyTax) (a : Asset) : Int := pos (divR .down (pos (p.value a) * p.ratioNum) p.ratioDen - p.exempt)

def schedFor (p : PropertyTax) (a : Asset) : Schedule :=
  match a.kind, p.homeSched with
  | .home, some s => s
  | _, _ => p.sched

def amount (p : PropertyTax) (a : Asset) : Int :=
  if p.kinds.contains a.kind then p.round.ofTicks (divR .down (p.multiplierBp * (p.schedFor a).ticks (p.base a)) BP)
  else 0

def charges (p : PropertyTax) (as : List Asset) (statute : String) (level : Level := .local) : List Charge :=
  (as.zipIdx.filter fun (a, _) => p.kinds.contains a.kind).map fun (a, i) =>
    charge .propertyRecurrent p.name (p.value a) (fun _ => p.base a) (fun _ => p.amount a)
      (event := s!"asset {i + 1}") (level := level) (statute := statute)
end PropertyTax

/-- With non-negative rates, ratio and multiplier, the tax rises with the base. -/
theorem PropertyTax.amount_mono_base (p : PropertyTax) (s : Schedule) (hr : s.RatesNonneg) (hm : 0 ≤ p.multiplierBp)
    (hs : 0 < p.round.step) (hmode : p.round.mode.isMonotoneMode) {x y : Int} (h : x ≤ y) :
    p.round.ofTicks (divR .down (p.multiplierBp * s.ticks x) BP)
      ≤ p.round.ofTicks (divR .down (p.multiplierBp * s.ticks y) BP) := by
  apply Rule.ofTicks_mono _ hs hmode
  apply divR_mono .down BP (by unfold BP; omega) (Or.inl rfl)
  exact Int.mul_le_mul_of_nonneg_left (Schedule.ticks_mono s hr h) hm

/-! ## Net wealth tax -/

structure WealthTax where
  name : String := "net wealth tax"
  /-- share of the value counted, bp, per asset kind -/
  valuation : AssetKind → Int := fun _ => 10000
  /-- value assets at their statutory value where given -/
  useAssessed : Bool := true
  exemptKinds : List AssetKind := []
  /-- exempt part of the main home's counted value -/
  homeExempt : Int := 0
  deductDebts : Bool := true
  allowance : Int := 0
  /-- no tax unless the base reaches this (−1: none); above it the schedule runs from 0 -/
  entryThreshold : Int := -1
  sched : Schedule
  round : Rule := {}
  /-- cap: income-related taxes + wealth tax ≤ `capBp` of income (−1: none) -/
  capBp : Int := -1
  /-- the cap reduces the wealth tax by at most this share of it, bp -/
  capMaxReliefBp : Int := 10000

namespace WealthTax
def counted (w : WealthTax) (a : Asset) : Int :=
  if w.exemptKinds.contains a.kind then 0 else
  let v := divR .down (w.valuation a.kind * (if w.useAssessed then a.statutoryValue else a.value)) BP
  if a.kind == .home then pos (v - w.homeExempt) else v

def netWealth (w : WealthTax) (as : List Asset) : Int :=
  isum (as.map w.counted) - (if w.deductDebts then isum (as.map (·.debt)) else 0)

def base (w : WealthTax) (as : List Asset) : Int :=
  let n := w.netWealth as
  if 0 ≤ w.entryThreshold ∧ n < w.entryThreshold then 0 else pos (n - w.allowance)

def gross (w : WealthTax) (as : List Asset) : Int := w.sched.tax w.round (w.base as)

/-- The tax after the cap, given the income-related taxes and the income the cap reads. -/
def capped (w : WealthTax) (gross incomeTaxes income : Int) : Int :=
  if w.capBp < 0 then gross else
  gross - min (pos (gross - pos (divR .down (w.capBp * pos income) BP - incomeTaxes)))
    (divR .down (w.capMaxReliefBp * pos gross) BP)
end WealthTax

theorem WealthTax.capped_le (w : WealthTax) (g t i : Int) (hm : 0 ≤ w.capMaxReliefBp) : w.capped g t i ≤ g := by
  unfold WealthTax.capped
  split
  · omega
  · have := Int.mul_nonneg hm (pos_nonneg g)
    simp only [divR, BP]
    generalize w.capMaxReliefBp * pos g = y at *
    simp only [pos] at *; omega

/-- The cap never removes more than `capMaxReliefBp` of the tax (ES: at least 20 % of it remains). -/
theorem WealthTax.capped_ge_floor (w : WealthTax) (g t i : Int) (hm : 0 ≤ w.capMaxReliefBp) :
    g - divR .down (w.capMaxReliefBp * pos g) BP ≤ w.capped g t i := by
  have := Int.mul_nonneg hm (pos_nonneg g)
  unfold WealthTax.capped
  split
  · simp only [divR, BP]
    generalize w.capMaxReliefBp * pos g = y at *
    omega
  · omega

end TaxKernel.Global
