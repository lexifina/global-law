import TaxKernel.Global2.Basket

/-!
# TaxKernel.Global2.ExciseRule (2.1.0; price tiers 2.4.0): excises as the statutes write them (OECD 5121)

`ExciseRule` keeps every field of the 2.0 `ExciseRate` (specific per canonical unit or per unit of pure alcohol, ad
valorem, minimum per unit) with the same meaning, and adds:

* **the value the ad valorem rate is levied on** (`valueBase`): `.retail` the tax-inclusive price (2.0 behaviour);
  `.netOfVat` the price net of VAT at `vatBp`; `.beforeTax` the value before excise and VAT (francophone CGIs
  "prix hors TVA et hors taxe elle-même", Commonwealth "excisable value", CN 消费税, VN SCT, TM art. 119, GCC). With
  VAT `v` charged on the excise-inclusive price and the specific parts `s` inside it,
  `p = (b + s + a·b)(1 + v)`, so `b = (p / (1 + v) − s) / (1 + a)` and the ad valorem duty is `a·b`. Rounded down at
  each step (`p/(1+v)`, then `b`, then `a·b`; as `R4.Exc`), or once (`roundOnce`: `a·(p − s(1+v))/((1+v)(1+a))`, as
  TM's `p·e/((1+e)(1+v))`). `withVat v` takes `vatBp` from a 2.0 `Vat`'s class for the good.
* **per mass** (`perKgNum / perKgDen` money per kg; per tonne: `perKgDen × 1000`): the line's `"massG"` if given,
  else the quantity × the statute's mass of one unit `mgPerUnit` (density in mg per litre, stick weight in mg);
* **per degree Plato** (`perPlatoNum / perPlatoDen` money per litre and degree; per hl: `perPlatoDen × 100`), the
  line's `"platoBp"`;
* **sugar bands** (`sugarBands`: `(from mg per 100 ml, num, den)` money per litre for lines at or above `from`; the
  highest band reached applies), the line's `"sugarMg100ml"`;
* **selection**: a sub-category `sub` (the line's `"sub"`, e.g. `"sweetenedDrinks"`, `"energyDrinks"`), a strength
  band `minAbvBp < abv ≤ maxAbvBp`, the origin `imported` (`none` any), and **dates** `validFrom ≤ date < validTo`
  (rates changing during the year; an undated line is taken for the share of the year in the window, by days);
* **price tiers** (2.4.0, R3-S4-1: MM Union Taxation Law 2025 s. 11, EG Table أولاً 1/ب/3): `minUnitPrice <
  price ≤ maxUnitPrice`, the price of `priceQty` thousandths of the canonical unit (a pack of 20 sticks: 20000) in
  money / `priceDen`, on `priceBase` (`.retail` by default). Compared exactly, `min·q < amount·priceQty·priceDen ≤
  max·q` (no rounded unit price: a pack at 800.50 is above 800). A rule without a tier (both −1, the default) selects
  as before (`appliesTo_noTier`); adjacent tiers never overlap (`priceIn_adjacent`). A line without a quantity is in
  no tier.

    duty = max (specific + per kg + per Plato + sugar band + ad valorem, minimum)

Charges (`exciseRuleCharges`): one per (line, matching rule) (`firstOnly`: only the first matching rule, as 2.0
`Excise.charges`). A `.retail` rule books `base = relieved = quantity` (as 2.0 `Excise.charges`); the others
`base = amount`, `relieved = the value taxed` (as `R4.exciseCharges`).

Theorems: `ofRate_dutyOn` (a 2.0 `ExciseRate` as a rule gives the same duty), `scaled_open`, `dutyOn_ge_min`,
`dutyOn_ge_mixed`, `value_beforeTax_le` (the value before tax is at most the price), `adValorem_nonneg`; 2.4.0:
`appliesTo_noTier`, `priceIn_noTier`, `hasPriceTier_default`, `priceIn_adjacent`, `priceIn_iff`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

inductive ValueBase where
  /-- the tax-inclusive price (2.0 `ExciseRate.adValoremBp`) -/
  | retail
  /-- the price net of VAT -/
  | netOfVat
  /-- the value before excise and VAT -/
  | beforeTax
  deriving Repr, DecidableEq, Inhabited, BEq

structure ExciseRule where
  good : Good
  name : String := "excise"
  /-- sub-category of the good the rule applies to (`""`: any) -/
  sub : String := ""
  /-- specific duty, `perUnitNum / perUnitDen` money per canonical unit (litre, stick, kWh) -/
  perUnitNum : Int := 0
  perUnitDen : Int := 1
  /-- the per-unit duty is per unit of pure alcohol (quantity × strength) -/
  onPureAlcohol : Bool := false
  /-- per kg: `perKgNum / perKgDen` money per kg (per tonne: `perKgDen × 1000`) -/
  perKgNum : Int := 0
  perKgDen : Int := 1
  /-- statutory mass of one canonical unit, mg (petrol 745 kg/m³ = 745000 mg per litre; a 0.7 g stick = 700) -/
  mgPerUnit : Int := 0
  /-- per litre and degree Plato: `perPlatoNum / perPlatoDen` (per hl and degree: `perPlatoDen × 100`) -/
  perPlatoNum : Int := 0
  perPlatoDen : Int := 1
  /-- `(from mg sugar per 100 ml, num, den)`: `num / den` money per litre at or above `from` (the highest reached) -/
  sugarBands : List (Int × Int × Int) := []
  adValoremBp : Int := 0
  valueBase : ValueBase := .retail
  /-- VAT on the excise-inclusive price, bp (`.netOfVat`, `.beforeTax`) -/
  vatBp : Int := 0
  roundOnce : Bool := false
  /-- minimum duty per canonical unit, `minNum / minDen` -/
  minNum : Int := 0
  minDen : Int := 1
  /-- strength band: `minAbvBp < abv ≤ maxAbvBp` -/
  minAbvBp : Int := -1
  maxAbvBp : Int := 100000
  /-- `none`: any origin; `some true`: imported only; `some false`: local production only -/
  imported : Option Bool := none
  /-- the rule applies to purchases on `validFrom ≤ date < validTo` (`""`: open) -/
  validFrom : String := ""
  validTo : String := ""
  statute : String := ""
  /-- price tier (2.4.0, R3-S4-1): the rule applies when `minUnitPrice < price ≤ maxUnitPrice` (−1: no bound), the
  price being that of `priceQty` thousandths of the canonical unit (1000: one litre or stick; a pack of 20 sticks:
  20000), in money / `priceDen` (piastres: 100), on `priceBase` (the tax-inclusive price by default) -/
  minUnitPrice : Int := -1
  maxUnitPrice : Int := -1
  priceQty : Int := 1000
  priceDen : Int := 1
  priceBase : ValueBase := .retail
  deriving Repr, Inhabited

namespace ExciseRule

/-- A 2.0 `ExciseRate` as a rule (same duty: `ofRate_dutyOn`). -/
def ofRate (e : ExciseRate) : ExciseRule :=
  { good := e.good, name := e.name, perUnitNum := e.perUnitNum, perUnitDen := e.perUnitDen,
    onPureAlcohol := e.onPureAlcohol, adValoremBp := e.adValoremBp, minNum := e.minNum, minDen := e.minDen,
    statute := e.statute }

/-- `vatBp` from a 2.0 `Vat`: the rate of the good's class. -/
def withVat (e : ExciseRule) (v : Vat) : ExciseRule := { e with vatBp := v.rateOf e.good }

def units (e : ExciseRule) (s : Spend) : Int :=
  if e.onPureAlcohol then divR .down (s.quantity * s.abvBp) BP else s.quantity

/-- Mass of the line in grams: given, or quantity × the statutory mass per unit. -/
def massG (e : ExciseRule) (s : Spend) (x : SpendX) : Int :=
  if 0 ≤ x.massG then x.massG else divR .down (s.quantity * e.mgPerUnit) 1000000

def perUnit (e : ExciseRule) (s : Spend) : Int := divR .down (e.units s * e.perUnitNum) (e.perUnitDen * 1000)
def perKg (e : ExciseRule) (s : Spend) (x : SpendX) : Int := divR .down (e.massG s x * e.perKgNum) (e.perKgDen * 1000)
def perPlato (e : ExciseRule) (s : Spend) (x : SpendX) : Int :=
  divR .down (s.quantity * x.platoBp * e.perPlatoNum) (e.perPlatoDen * 100000)

def sugarBand (e : ExciseRule) (x : SpendX) : Option (Int × Int) :=
  e.sugarBands.foldl (fun acc (f, n, d) => if f ≤ x.sugarMg100ml then some (n, d) else acc) none

def perSugar (e : ExciseRule) (s : Spend) (x : SpendX) : Int :=
  match e.sugarBand x with
  | some (n, d) => divR .down (s.quantity * n) (d * 1000)
  | none => 0

/-- Every specific part. -/
def specific (e : ExciseRule) (s : Spend) (x : SpendX) : Int :=
  e.perUnit s + e.perKg s x + e.perPlato s x + e.perSugar s x

def netOfVat (e : ExciseRule) (s : Spend) : Int := divR .down (pos s.amount * BP) (BP + e.vatBp)

/-- `p − s(1+v)` in bp of money (for `roundOnce`). -/
def onceNum (e : ExciseRule) (s : Spend) (x : SpendX) : Int := pos (pos s.amount * BP - e.specific s x * (BP + e.vatBp))

/-- The value the ad valorem rate is levied on. -/
def value (e : ExciseRule) (s : Spend) (x : SpendX) : Int :=
  match e.valueBase with
  | .retail => pos s.amount
  | .netOfVat => e.netOfVat s
  | .beforeTax =>
    if e.roundOnce then divR .down (e.onceNum s x * BP) ((BP + e.vatBp) * (BP + e.adValoremBp))
    else divR .down (pos (e.netOfVat s - e.specific s x) * BP) (BP + e.adValoremBp)

def adValorem (e : ExciseRule) (s : Spend) (x : SpendX) : Int :=
  match e.valueBase with
  | .beforeTax =>
    if e.roundOnce then divR .down (e.adValoremBp * e.onceNum s x) ((BP + e.vatBp) * (BP + e.adValoremBp))
    else divR .down (e.adValoremBp * e.value s x) BP
  | _ => divR .down (e.adValoremBp * e.value s x) BP

def minimum (e : ExciseRule) (s : Spend) : Int := divR .down (s.quantity * e.minNum) (e.minDen * 1000)

/-- The duty on one line (no date window applied). -/
def dutyOn (e : ExciseRule) (s : Spend) (x : SpendX) : Int := max (e.specific s x + e.adValorem s x) (e.minimum s)

/-! ### Dates -/

def openWindow (e : ExciseRule) : Bool := e.validFrom == "" && e.validTo == ""

def windowDays (e : ExciseRule) (year : Nat) : Nat := endDay year e.validTo - startDay year e.validFrom

/-- The line as the rule sees it: an undated line under a dated rule is the window's share of the year. -/
def scaled (e : ExciseRule) (year : Nat) (s : Spend) (x : SpendX) : Spend × SpendX :=
  if e.openWindow || (dayOfYear? year x.date).isSome then (s, x) else
  let d := e.windowDays year
  let n := daysInYear year
  ({ s with amount := scaleDays s.amount d n, quantity := scaleDays s.quantity d n },
   { x with massG := if 0 ≤ x.massG then scaleDays x.massG d n else x.massG })

def inWindow (e : ExciseRule) (year : Nat) (x : SpendX) : Bool :=
  e.openWindow ||
    match dayOfYear? year x.date with
    | some d => decide (startDay year e.validFrom ≤ d) && decide (d < endDay year e.validTo)
    | none => decide (0 < e.windowDays year)

/-- The selection of 2.1-2.3: good, sub-category, strength band, origin, date window. -/
def selects (e : ExciseRule) (year : Nat) (s : Spend) (x : SpendX) : Bool :=
  e.good == s.good && (e.sub == "" || e.sub == x.sub) && decide (e.minAbvBp < s.abvBp)
    && decide (s.abvBp ≤ e.maxAbvBp) && (match e.imported with | none => true | some b => b == x.imported)
    && e.inWindow year x

/-! ### Price tiers (2.4.0, R3-S4-1) -/

/-- The money the price tier reads: the tax-inclusive price, the price net of VAT, or the value before excise and VAT
(as the rule's own `.beforeTax` value). -/
def priceMoney (e : ExciseRule) (s : Spend) (x : SpendX) : Int :=
  match e.priceBase with
  | .retail => pos s.amount
  | .netOfVat => e.netOfVat s
  | .beforeTax => ({ e with valueBase := .beforeTax } : ExciseRule).value s x

/-- The price of `priceQty` thousandths of the unit, in money/`priceDen`, times the line's quantity:
`price × quantity` (compared exactly: no rounding of the unit price). -/
def priceTimesQty (e : ExciseRule) (s : Spend) (x : SpendX) : Int := e.priceMoney s x * e.priceQty * e.priceDen

def hasPriceTier (e : ExciseRule) : Bool := decide (0 ≤ e.minUnitPrice) || decide (0 ≤ e.maxUnitPrice)

/-- The line's unit price is in the tier `minUnitPrice < price ≤ maxUnitPrice`; a rule without a tier takes every line,
a rule with one no line without a quantity. -/
def priceIn (e : ExciseRule) (s : Spend) (x : SpendX) : Bool :=
  !e.hasPriceTier ||
    (decide (0 < s.quantity)
      && (decide (e.minUnitPrice < 0) || decide (e.minUnitPrice * s.quantity < e.priceTimesQty s x))
      && (decide (e.maxUnitPrice < 0) || decide (e.priceTimesQty s x ≤ e.maxUnitPrice * s.quantity)))

/-- The unit price (rounded down) as the tier reads it, for notes: money/`priceDen` per `priceQty` thousandths. -/
def unitPrice (e : ExciseRule) (s : Spend) (x : SpendX) : Int :=
  if s.quantity ≤ 0 then 0 else divR .down (e.priceTimesQty s x) s.quantity

def appliesTo (e : ExciseRule) (year : Nat) (s : Spend) (x : SpendX) : Bool :=
  e.selects year s x && e.priceIn s x

/-- The duty on a basket line in `year`. -/
def duty (e : ExciseRule) (year : Nat) (s : Spend) (x : SpendX) : Int :=
  let sx := e.scaled year s x
  e.dutyOn sx.1 sx.2

def toCharge (e : ExciseRule) (year : Nat) (s : Spend) (x : SpendX) : Charge :=
  let sx := e.scaled year s x
  let s' := sx.1
  let x' := sx.2
  let ev := if x.sub == "" then s.good.name else x.sub
  let note := if e.openWindow || (dayOfYear? year x.date).isSome then ""
    else s!"; {e.windowDays year}/{daysInYear year} of the year"
  if e.valueBase == .retail then
    charge .excise e.name s'.quantity id (fun _ => e.dutyOn s' x') (event := ev) (bearer := .consumer)
      (statute := e.statute ++ note)
  else
    charge .excise e.name s'.amount (fun _ => e.value s' x') (fun _ => e.dutyOn s' x') (event := ev)
      (bearer := .consumer) (statute := e.statute ++ note)

end ExciseRule

/-- Excise charges on the entity's basket: one per (line, matching rule); `firstOnly`: the first matching rule. -/
def exciseRuleCharges (rules : List ExciseRule) (g : CanonGlobal) (firstOnly : Bool := false) : List Charge :=
  (consumptionX g).flatMap fun (s, x) =>
    let ms := rules.filter (·.appliesTo g.year s x)
    (if firstOnly then ms.take 1 else ms).map (·.toCharge g.year s x)

/-- The 5121 family of a list of rules. -/
def exciseRuleFamily (name : String) (rules : List ExciseRule) (firstOnly : Bool := false) : Family :=
  { name := s!"5121 {name}", covers := [.excise], run := fun _ g _ => exciseRuleCharges rules g firstOnly }

/-! ## Theorems -/

theorem ExciseRule.ofRate_dutyOn (e : ExciseRate) (s : Spend) : (ExciseRule.ofRate e).dutyOn s {} = e.duty s := by
  simp [ExciseRule.ofRate, ExciseRule.dutyOn, ExciseRule.specific, ExciseRule.perUnit, ExciseRule.perKg,
    ExciseRule.perPlato, ExciseRule.perSugar, ExciseRule.sugarBand, ExciseRule.adValorem, ExciseRule.value,
    ExciseRule.minimum, ExciseRule.units, ExciseRule.massG, ExciseRate.duty, ExciseRate.specific,
    ExciseRate.adValorem, ExciseRate.minimum, ExciseRate.units, divR]
  all_goals rfl

/-- **A rule without a price tier selects exactly as before 2.4.0.** -/
theorem ExciseRule.appliesTo_noTier (e : ExciseRule) (y : Nat) (s : Spend) (x : SpendX) (h : e.hasPriceTier = false) :
    e.appliesTo y s x = e.selects y s x := by
  simp [ExciseRule.appliesTo, ExciseRule.priceIn, h]

theorem ExciseRule.priceIn_noTier (e : ExciseRule) (s : Spend) (x : SpendX) (h : e.hasPriceTier = false) :
    e.priceIn s x = true := by
  simp [ExciseRule.priceIn, h]

/-- The defaults have no tier (`−1`, `−1`). -/
theorem ExciseRule.hasPriceTier_default (g : Good) : ({ good := g } : ExciseRule).hasPriceTier = false := by
  simp [ExciseRule.hasPriceTier]

/-- **Adjacent tiers never overlap**: when one tier ends where the next begins (same price unit and base), no line
is in both. -/
theorem ExciseRule.priceIn_adjacent (e₁ e₂ : ExciseRule) (s : Spend) (x : SpendX) (hb : e₁.priceTimesQty s x = e₂.priceTimesQty s x)
    (hm : e₁.maxUnitPrice = e₂.minUnitPrice) (h0 : 0 ≤ e₂.minUnitPrice) :
    ¬ (e₁.priceIn s x = true ∧ e₂.priceIn s x = true) := by
  rintro ⟨h1, h2⟩
  have ht1 : e₁.hasPriceTier = true := by simp [ExciseRule.hasPriceTier]; omega
  have ht2 : e₂.hasPriceTier = true := by simp [ExciseRule.hasPriceTier]; omega
  simp only [ExciseRule.priceIn, ht1, ht2, Bool.not_true, Bool.false_or, Bool.and_eq_true, Bool.or_eq_true,
    decide_eq_true_eq] at h1 h2
  rw [hb, hm] at h1
  obtain ⟨⟨_, _⟩, h1c⟩ := h1
  obtain ⟨⟨_, h2b⟩, _⟩ := h2
  omega

/-- The same tier, read on the same line, with the bound and the price exact (no rounding of the unit price):
in the tier iff `min·q < p·Q·D ≤ max·q`. -/
theorem ExciseRule.priceIn_iff (e : ExciseRule) (s : Spend) (x : SpendX) (hq : 0 < s.quantity)
    (hmin : 0 ≤ e.minUnitPrice) (hmax : 0 ≤ e.maxUnitPrice) :
    e.priceIn s x = true ↔ e.minUnitPrice * s.quantity < e.priceTimesQty s x
      ∧ e.priceTimesQty s x ≤ e.maxUnitPrice * s.quantity := by
  have ht : e.hasPriceTier = true := by simp [ExciseRule.hasPriceTier]; omega
  simp only [ExciseRule.priceIn, ht, Bool.not_true, Bool.false_or, Bool.and_eq_true, Bool.or_eq_true,
    decide_eq_true_eq]
  constructor
  · rintro ⟨⟨_, h1⟩, h2⟩; omega
  · rintro ⟨h1, h2⟩; omega

theorem ExciseRule.scaled_open(e : ExciseRule) (y : Nat) (s : Spend) (x : SpendX) (h : e.openWindow = true) :
    e.scaled y s x = (s, x) := by
  simp [ExciseRule.scaled, h]

theorem ExciseRule.dutyOn_ge_min (e : ExciseRule) (s : Spend) (x : SpendX) : e.minimum s ≤ e.dutyOn s x := by
  unfold ExciseRule.dutyOn; omega

theorem ExciseRule.dutyOn_ge_mixed (e : ExciseRule) (s : Spend) (x : SpendX) :
    e.specific s x + e.adValorem s x ≤ e.dutyOn s x := by
  unfold ExciseRule.dutyOn; omega

theorem ExciseRule.netOfVat_le (e : ExciseRule) (s : Spend) (hv : 0 ≤ e.vatBp) : e.netOfVat s ≤ pos s.amount := by
  unfold ExciseRule.netOfVat
  simp only [divR, BP]
  have hp := pos_nonneg s.amount
  apply Int.ediv_le_of_le_mul (by omega)
  have : pos s.amount * 10000 ≤ pos s.amount * (10000 + e.vatBp) := Int.mul_le_mul_of_nonneg_left (by omega) hp
  exact this

/-- The value before excise and VAT never exceeds the price (non-negative rates and specific parts). -/
theorem ExciseRule.value_beforeTax_le (e : ExciseRule) (s : Spend) (x : SpendX) (hb : e.valueBase = .beforeTax)
    (ho : e.roundOnce = false) (hv : 0 ≤ e.vatBp) (ha : 0 ≤ e.adValoremBp) (hs : 0 ≤ e.specific s x) :
    e.value s x ≤ pos s.amount := by
  have hn := e.netOfVat_le s hv
  simp only [ExciseRule.value, hb, ho]
  simp only [divR, BP] at *
  generalize e.netOfVat s = n at *
  generalize e.specific s x = sp at *
  have hq : pos (n - sp) ≤ pos s.amount := by simp only [pos] at *; omega
  have hq0 := pos_nonneg (n - sp)
  apply Int.ediv_le_of_le_mul (by omega)
  have : pos (n - sp) * 10000 ≤ pos s.amount * (10000 + e.adValoremBp) := by
    have h1 : pos (n - sp) * 10000 ≤ pos s.amount * 10000 := Int.mul_le_mul_of_nonneg_right hq (by omega)
    have h2 : pos s.amount * 10000 ≤ pos s.amount * (10000 + e.adValoremBp) :=
      Int.mul_le_mul_of_nonneg_left (by omega) (pos_nonneg _)
    omega
  exact this

theorem ExciseRule.adValorem_nonneg (e : ExciseRule) (s : Spend) (x : SpendX) (hv : 0 ≤ e.vatBp)
    (ha : 0 ≤ e.adValoremBp) : 0 ≤ e.adValorem s x := by
  have hnv : 0 ≤ e.netOfVat s := by
    unfold ExciseRule.netOfVat; simp only [divR, BP]
    exact Int.ediv_nonneg (Int.mul_nonneg (pos_nonneg _) (by omega)) (by omega)
  have hval : 0 ≤ e.value s x := by
    unfold ExciseRule.value
    split
    · exact pos_nonneg _
    · exact hnv
    · split
      · simp only [divR, BP]
        exact Int.ediv_nonneg (Int.mul_nonneg (pos_nonneg _) (by omega)) (Int.mul_nonneg (by omega) (by omega))
      · simp only [divR, BP]; exact Int.ediv_nonneg (Int.mul_nonneg (pos_nonneg _) (by omega)) (by omega)
  unfold ExciseRule.adValorem
  split
  · split
    · simp only [divR, BP]
      exact Int.ediv_nonneg (Int.mul_nonneg ha (pos_nonneg _)) (Int.mul_nonneg (by omega) (by omega))
    · simp only [divR, BP]; exact Int.ediv_nonneg (Int.mul_nonneg ha hval) (by omega)
  · simp only [divR, BP]; exact Int.ediv_nonneg (Int.mul_nonneg ha hval) (by omega)

end TaxKernel.Global
