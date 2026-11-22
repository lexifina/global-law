import TaxKernel.Global.Transfers

/-!
# TaxKernel.Global.Consumption (2.0.0): VAT/GST (OECD 5111) and excises (5121), employer side and payroll (2200, 3000)

**VAT on a consumption basket.** Household spending is given tax-inclusive. The VAT inside an amount `p` at rate `r`
is `p × r / (1 + r)`; excises are inside the price too, and VAT is charged on the price including the excise (tax on
tax), so `embedded` of the full price is right for both. `Vat.basket` sums over the basket; each good's rate class
comes from the statute's annex (`classOf`).

**VAT on a business (transaction level).** Output VAT on taxable supplies (exports zero-rated), input VAT deductible
in the proportion of taxable (incl. zero-rated) to total supplies when some supplies are exempt (pro rata, EU VAT
Directive art. 173-174), nothing due at or below the registration/small-business threshold:

    net VAT = 0                                         if turnover ≤ threshold
            = Σ output − Σ input × pro-rata             otherwise          (negative: a refund)

**Excises.** Per good: a specific duty per unit (num/den money per canonical unit; or per unit of pure alcohol), an
ad valorem share of the retail price, and a minimum per unit (EU cigarettes, Directive 2011/64/EU art. 7-8); the
duty is the larger of (specific + ad valorem) and the minimum.

**Employer side and payroll.** Employer social contributions on each adult's wages are 1.x `Contribution`s booked
under 2200 with bearer `employer`; payroll taxes on the employer's wage bill with a threshold (allowance or
all-or-nothing) under 3000.

Theorems: `embedded_le`, `embedded_nonneg`, `Vat.net_below_threshold`, `ExciseRate.duty_ge_min`,
`ExciseRate.duty_ge_mixed`, `PayrollTax.ticks_nonneg`.
-/

namespace TaxKernel.Global
open TaxKernel

inductive RateClass where
  | standard | reduced | reduced2 | superReduced | zero | exempt
  deriving Repr, DecidableEq, Inhabited, BEq

structure Vat where
  name : String := "VAT"
  standard : Int
  reduced : Int := 0
  reduced2 : Int := 0
  superReduced : Int := 0
  classOf : Good → RateClass := fun _ => .standard
  /-- turnover at or below which a business is not liable (0: none) -/
  threshold : Int := 0
  round : Rule := {}

namespace Vat
def rate (v : Vat) : RateClass → Int
  | .standard => v.standard | .reduced => v.reduced | .reduced2 => v.reduced2
  | .superReduced => v.superReduced | .zero => 0 | .exempt => 0

def rateOf (v : Vat) (g : Good) : Int := v.rate (v.classOf g)

/-- VAT inside a tax-inclusive amount. -/
def embedded (v : Vat) (s : Spend) : Int :=
  let r := v.rateOf s.good
  divR .down (pos s.amount * r) (BP + r)

def basket (v : Vat) (xs : List Spend) : Int := isum (xs.map v.embedded)

def basketCharge (v : Vat) (xs : List Spend) (statute : String) : Charge :=
  charge .vat v.name (isum (xs.map (·.amount))) id (fun _ => v.basket xs) (event := "basket") (bearer := .consumer)
    (statute := statute)

def outputTax (v : Vat) (sales : List Supply) : Int :=
  isum (sales.map fun s => if s.exported then 0 else divR .down (v.rateOf s.good * s.net) BP)

def inputTax (v : Vat) (inputs : List Supply) : Int := isum (inputs.map fun s => divR .down (v.rateOf s.good * s.net) BP)

/-- Deductible share of input VAT, bp: (taxable + zero-rated + exported supplies) / all supplies. -/
def proRataBp (v : Vat) (sales : List Supply) : Int :=
  let total := isum (sales.map (·.net))
  let taxable := isum ((sales.filter fun s => s.exported || v.classOf s.good != .exempt).map (·.net))
  if total ≤ 0 then BP else divR .up (BP * taxable) total

def net (v : Vat) (co : Company) : Int :=
  if co.turnover ≤ v.threshold then 0
  else v.outputTax co.sales - divR .down (v.inputTax co.inputs * v.proRataBp co.sales) BP

def businessCharge (v : Vat) (co : Company) (statute : String) : Charge :=
  charge .vat v.name (isum (co.sales.map (·.net))) id (fun _ => v.net co) (event := "supplies") (bearer := .consumer)
    (statute := statute)
end Vat

theorem embedded_nonneg (v : Vat) (s : Spend) (hr : 0 ≤ v.rateOf s.good) : 0 ≤ v.embedded s := by
  unfold Vat.embedded
  have := Int.mul_nonneg (pos_nonneg s.amount) hr
  simp only [divR, BP]
  exact Int.ediv_nonneg this (by omega)

/-- The VAT inside an amount never exceeds the amount. -/
theorem embedded_le (v : Vat) (s : Spend) (hr : 0 ≤ v.rateOf s.good) : v.embedded s ≤ pos s.amount := by
  unfold Vat.embedded
  simp only [divR, BP]
  have hp := pos_nonneg s.amount
  have h1 : pos s.amount * v.rateOf s.good ≤ pos s.amount * (10000 + v.rateOf s.good) :=
    Int.mul_le_mul_of_nonneg_left (by omega) hp
  apply Int.ediv_le_of_le_mul (by omega)
  exact h1

theorem Vat.net_below_threshold (v : Vat) (co : Company) (h : co.turnover ≤ v.threshold) : v.net co = 0 := by
  unfold Vat.net; simp [h]

/-! ## Excises -/

structure ExciseRate where
  good : Good
  name : String := "excise"
  /-- specific duty: `perUnitNum / perUnitDen` money units per canonical unit -/
  perUnitNum : Int := 0
  perUnitDen : Int := 1
  /-- the specific duty is per unit of pure alcohol (quantity × strength) -/
  onPureAlcohol : Bool := false
  adValoremBp : Int := 0
  /-- minimum duty per canonical unit, `minNum / minDen` -/
  minNum : Int := 0
  minDen : Int := 1
  statute : String := ""
  deriving Repr, Inhabited

namespace ExciseRate
def units (e : ExciseRate) (s : Spend) : Int := if e.onPureAlcohol then divR .down (s.quantity * s.abvBp) BP else s.quantity
def specific (e : ExciseRate) (s : Spend) : Int := divR .down (e.units s * e.perUnitNum) (e.perUnitDen * 1000)
def adValorem (e : ExciseRate) (s : Spend) : Int := divR .down (e.adValoremBp * pos s.amount) BP
def minimum (e : ExciseRate) (s : Spend) : Int := divR .down (s.quantity * e.minNum) (e.minDen * 1000)
def duty (e : ExciseRate) (s : Spend) : Int := max (e.specific s + e.adValorem s) (e.minimum s)
end ExciseRate

structure Excise where
  rates : List ExciseRate

def Excise.rateFor (x : Excise) (g : Good) : Option ExciseRate := x.rates.find? (·.good == g)

def Excise.duty (x : Excise) (s : Spend) : Int := match x.rateFor s.good with | some e => e.duty s | none => 0

def Excise.charges (x : Excise) (xs : List Spend) : List Charge :=
  (xs.filter fun s => (x.rateFor s.good).isSome).map fun s =>
    let e := (x.rateFor s.good).getD { good := s.good }
    charge .excise e.name s.quantity id (fun _ => e.duty s) (event := s.good.name) (bearer := .consumer)
      (statute := e.statute)

theorem ExciseRate.duty_ge_min (e : ExciseRate) (s : Spend) : e.minimum s ≤ e.duty s := by
  unfold ExciseRate.duty; omega

theorem ExciseRate.duty_ge_mixed (e : ExciseRate) (s : Spend) : e.specific s + e.adValorem s ≤ e.duty s := by
  unfold ExciseRate.duty; omega

/-! ## Employer side and payroll -/

/-- Employer contributions on each adult's wages (2200, borne by the employer). -/
def employerCharges (cs : List Contribution) (wages : List Int) (statute : String) : List Charge :=
  (wages.zipIdx.flatMap fun (w, i) => cs.map fun c =>
    charge .sscEmployer c.name w id (fun x => c.amount x) (event := s!"adult {i + 1}") (level := .social)
      (bearer := .employer) (statute := statute))

structure PayrollTax where
  name : String := "payroll tax"
  rateBp : Int
  threshold : Int := 0
  /-- `true`: the threshold is deducted (an allowance); `false`: nothing below it, the whole bill above it -/
  deduct : Bool := true
  round : Rule := {}
  deriving Repr, Inhabited

def PayrollTax.ticks (p : PayrollTax) (bill : Int) : Int :=
  p.rateBp * (if p.deduct then pos (bill - p.threshold) else if bill ≤ p.threshold then 0 else pos bill)

def PayrollTax.amount (p : PayrollTax) (bill : Int) : Int := p.round.ofTicks (p.ticks bill)

theorem PayrollTax.ticks_nonneg (p : PayrollTax) (bill : Int) (hr : 0 ≤ p.rateBp) : 0 ≤ p.ticks bill := by
  unfold PayrollTax.ticks
  apply Int.mul_nonneg hr
  split
  · exact pos_nonneg _
  · split
    · omega
    · exact pos_nonneg _

end TaxKernel.Global
