import TaxKernel.Global.Corporate

/-!
# TaxKernel.Global.Capital (2.0.0): capital income and capital gains (OECD 1100/1200), withholding at source

**Schedular and dual income.** The 1.x kernel already has `Dual` (separate earned and capital schedules with a
deficit credit) and `World.Cedula`/`overlayTax` (category taxes with an annual overlay). This file adds:
* `FlatCapital`: a final flat tax on capital income after an annual allowance and an inclusion share (DE EStG § 32d
  (1) with the Sparer-Pauschbetrag of § 20 (9); IT 26 %; partial inclusion as DE § 3 Nr. 40 at 60 %).
* `Imputation`: dividend gross-up and credit (CA, AU franking, UK pre-2016, CL integrated credit LIR art. 56 N° 3).

**Capital gains.** `GainRule` turns one `Disposal` into its taxable gain:

    gain      = proceeds − cost × index (if indexed) − costs
    taxable   = 0                                    if held ≥ exemptAfterMonths, or a main home fully exempt,
                                                     or shares below the minimum stake
              = inclusion(held) × (gain − main-home cap)   otherwise (losses keep their sign)

and `AnnualExempt` applies the year's exempt amount to the net of the year's gains, as an allowance (Freibetrag) or
an all-or-nothing threshold (Freigrenze: DE EStG § 23 (3) Satz 5, "weniger als 1 000 Euro").

**Withholding at source** (`Wht`): statutory (treaty-free) rates by payment kind and recipient type, with a stake
condition for parent-subsidiary rules; final or creditable (`afterCredit`).

Theorems: `taxable_exempt_after`, `indexedCost_ge`, `indexedGain_le`, `included_le`, `threshold_notch`,
`allowance_le`, `afterCredit_ge`, `flat_mono`, `imputation_credit_nonneg`.
-/

namespace TaxKernel.Global
open TaxKernel

/-! ## Flat schedular tax on capital income -/

structure FlatCapital where
  rateBp : Int
  allowance : Int := 0
  /-- share of the income (after the allowance) that is taxed, bp -/
  inclusionBp : Int := 10000
  round : Rule := {}
  deriving Repr, Inhabited

def FlatCapital.base (f : FlatCapital) (income : Int) : Int :=
  divR .down (f.inclusionBp * pos (income - f.allowance)) BP

def FlatCapital.tax (f : FlatCapital) (income : Int) : Int := f.round.ofTicks (f.rateBp * f.base income)

/-! ## Imputation -/

structure Imputation where
  /-- gross-up, bp of the cash dividend -/
  grossUpBp : Int
  /-- credit, bp of the cash dividend (CL: the first-category tax rate grossed up; CA: of the grossed-up amount
  folded into this number) -/
  creditBp : Int
  deriving Repr, Inhabited

def Imputation.grossed (i : Imputation) (div : Int) : Int := div + divR .down (i.grossUpBp * pos div) BP
def Imputation.credit (i : Imputation) (div : Int) : Int := divR .down (i.creditBp * pos div) BP

/-! ## Capital gains -/

structure GainRule where
  /-- a disposal held at least this many months is exempt (−1: never) -/
  exemptAfterMonths : Int := -1
  /-- from this holding the long inclusion applies (−1: always the short one) -/
  longAfterMonths : Int := -1
  inclusionShortBp : Int := 10000
  inclusionLongBp : Int := 10000
  /-- the cost is indexed by the factor given to `taxable` -/
  indexCost : Bool := false
  mainHomeExempt : Bool := false
  /-- exempt part of a main-home gain (−1: all of it) -/
  mainHomeCap : Int := -1
  /-- gains on shares are taxable only from this stake (0: always) -/
  minStakeBp : Int := 0
  deriving Repr, Inhabited

namespace GainRule

def indexedCost (r : GainRule) (num den : Int) (d : Disposal) : Int :=
  if r.indexCost ∧ 0 < den then divR .down (d.cost * num) den else d.cost

def gain (r : GainRule) (num den : Int) (d : Disposal) : Int := d.proceeds - r.indexedCost num den d - d.costs

def exempt (r : GainRule) (d : Disposal) : Bool :=
  (decide (0 ≤ r.exemptAfterMonths) && decide (r.exemptAfterMonths ≤ (d.heldMonths : Int)))
  || (r.mainHomeExempt && d.mainHome && decide (r.mainHomeCap < 0))
  || (d.kind.isShares && decide (d.stakeBp < r.minStakeBp))

def inclusion (r : GainRule) (d : Disposal) : Int :=
  if 0 ≤ r.longAfterMonths ∧ r.longAfterMonths ≤ (d.heldMonths : Int) then r.inclusionLongBp else r.inclusionShortBp

/-- Taxable gain (negative: an allowable loss) of one disposal; `num/den` is the indexation factor. -/
def taxable (r : GainRule) (num den : Int) (d : Disposal) : Int :=
  if r.exempt d then 0 else
  let g := r.gain num den d
  let g' := if r.mainHomeExempt ∧ d.mainHome ∧ 0 ≤ r.mainHomeCap ∧ 0 < g then pos (g - r.mainHomeCap) else g
  divR .towardZero (r.inclusion d * g') BP

end GainRule

/-- The year's exempt amount on the net gains: an allowance, or an all-or-nothing threshold ("less than"). -/
structure AnnualExempt where
  amount : Int := 0
  threshold : Bool := false
  deriving Repr, Inhabited

def AnnualExempt.apply (a : AnnualExempt) (net : Int) : Int :=
  if net ≤ 0 then 0
  else if a.threshold then (if net < a.amount then 0 else net)
  else pos (net - a.amount)

/-! ## Withholding at source (statutory, treaty-free) -/

structure WhtRule where
  kind : IncomeKind
  /-- `some true`: only to companies; `some false`: only to individuals; `none`: any recipient -/
  toCompany : Option Bool := none
  /-- applies only from this stake (parent-subsidiary rules) -/
  minStakeBp : Int := 0
  rateBp : Int
  final : Bool := true
  statute : String := ""
  deriving Repr, Inhabited

structure Wht where
  name : String := "withholding tax"
  rules : List WhtRule
  round : Rule := {}
  deriving Repr, Inhabited

def WhtRule.matches (w : WhtRule) (p : Payment) : Bool :=
  w.kind == p.kind && (match w.toCompany with | none => true | some b => b == p.toCompany) && decide (w.minStakeBp ≤ p.stakeBp)

/-- The first matching rule (write the most specific first). -/
def Wht.ruleFor (w : Wht) (p : Payment) : Option WhtRule := w.rules.find? (·.matches p)

def Wht.amount (w : Wht) (p : Payment) : Int :=
  match w.ruleFor p with
  | some r => w.round.ofTicks (r.rateBp * pos p.amount)
  | none => 0

/-- The charge for payment `p` of (0-based) index `i`: booked under 1100 or 1200 by the recipient's type. With no
matching rule it is a placeholder (due 0, statute `noWhtRule`), which `computeGlobal` drops for a company entity and
lists as grade C (kernel 2.3.0, `WhtRead`). -/
def Wht.chargeOf (w : Wht) (p : Payment) (i : Nat) : Charge :=
  let st := match w.ruleFor p with | some r => r.statute | none => noWhtRule
  charge (if p.toCompany then .cit else .pit) w.name p.amount id (fun _ => w.amount p)
    (event := s!"payment {i + 1} ({p.kind.name})") (bearer := .withheld) (statute := st)

/-- Charges for a company's payments abroad (booked under 1100 or 1200 by the recipient's type). -/
def Wht.charges (w : Wht) (co : Company) : List Charge :=
  co.paymentsAbroad.zipIdx.map fun (p, i) => w.chargeOf p i

/-- A cited statutory zero (kernel 2.3.0): no withholding on `kind` (for the recipients `toCompany` selects), booked as
a covered 0 with its citation, not as an unread payment. -/
def WhtRule.zero (kind : IncomeKind) (statute : String) (toCompany : Option Bool := none) : WhtRule :=
  { kind, toCompany, rateBp := 0, statute }

/-- Cited statutory zeros for several kinds. -/
def Wht.zeroOn (kinds : List IncomeKind) (statute : String) (toCompany : Option Bool := none) : List WhtRule :=
  kinds.map fun k => WhtRule.zero k statute toCompany

/-- The withholding as a family of its own (company entities only), e.g. for a model whose statute imposes none:
`({ name := "…", rules := Wht.zeroOn [.dividend, .interest, .royalty, .services] "Act s. 5" } : Wht).family`. -/
def Wht.family (w : Wht) (covers : List Oecd := [.cit]) : Family :=
  { name := w.name, covers, run := fun _ g _ => if g.entity == .company then w.charges g.company else [] }

/-- Liability after a creditable withholding: what remains (non-refundable: never below 0; refundable: may be
negative, a refund). -/
def afterCredit (liability withheld : Int) (refundable : Bool) : Int :=
  if refundable then liability - withheld else pos (liability - withheld)

/-! ## Theorems -/

theorem taxable_exempt_after (r : GainRule) (num den : Int) (d : Disposal) (h0 : 0 ≤ r.exemptAfterMonths)
    (h : r.exemptAfterMonths ≤ (d.heldMonths : Int)) : r.taxable num den d = 0 := by
  unfold GainRule.taxable GainRule.exempt
  simp [h0, h]

theorem indexedCost_ge (r : GainRule) (num den : Int) (d : Disposal) (hc : 0 ≤ d.cost) (hn : den ≤ num) :
    d.cost ≤ r.indexedCost num den d := by
  unfold GainRule.indexedCost
  split
  · rename_i h
    have hd : 0 < den := h.2
    apply Int.le_ediv_of_mul_le hd
    exact Int.mul_le_mul_of_nonneg_left hn hc
  · omega

/-- Indexation never raises the gain (index factor ≥ 1, cost ≥ 0). -/
theorem indexedGain_le (r : GainRule) (num den : Int) (d : Disposal) (hc : 0 ≤ d.cost) (hn : den ≤ num) :
    r.gain num den d ≤ d.gain := by
  have := indexedCost_ge r num den d hc hn
  unfold GainRule.gain Disposal.gain; omega

/-- An inclusion share of at most 100 % never raises a gain. -/
theorem included_le (incl g : Int) (hi : incl ≤ BP) (hg : 0 ≤ g) : divR .towardZero (incl * g) BP ≤ g := by
  have h1 : incl * g ≤ BP * g := Int.mul_le_mul_of_nonneg_right hi hg
  simp only [divR, BP] at *
  generalize incl * g = y at *
  split <;> omega

/-- A threshold (Freigrenze) is a notch: one unit more of gains makes all of them taxable. -/
theorem threshold_notch (n : Int) (hn : 1 ≤ n) :
    ({ amount := n, threshold := true } : AnnualExempt).apply (n - 1) = 0 ∧
    ({ amount := n, threshold := true } : AnnualExempt).apply n = n := by
  simp only [AnnualExempt.apply]
  constructor
  · split <;> (try rfl); simp only [↓reduceIte]; split <;> omega
  · split
    · omega
    · simp only [↓reduceIte]; split <;> omega

theorem allowance_le (a : AnnualExempt) (net : Int) (h : a.threshold = false) (ha : 0 ≤ a.amount) : a.apply net ≤ pos net := by
  unfold AnnualExempt.apply; simp only [h, pos]; split <;> (try simp) <;> omega

/-- Kernel 2.3.0: a payment no rule matches gives a placeholder (dropped and listed as grade C by `computeGlobal`). -/
theorem Wht.chargeOf_unread (w : Wht) (p : Payment) (i : Nat) (h : w.ruleFor p = none) :
    (w.chargeOf p i).unreadWht = true := by
  simp [Wht.chargeOf, Wht.amount, h, charge, appliedCredit, Charge.unreadWht, pos]
  rfl

/-- Kernel 2.3.0: a payment a rule matches is never a placeholder when the rule's statute is not `noWhtRule`, whatever
its rate (a cited 0 % rule books a covered 0). -/
theorem Wht.chargeOf_rule_kept (w : Wht) (p : Payment) (i : Nat) (r : WhtRule) (h : w.ruleFor p = some r)
    (hs : r.statute ≠ noWhtRule) : (w.chargeOf p i).unreadWht = false := by
  simp [Wht.chargeOf, h, charge, Charge.unreadWht, hs]

/-- A 0 % rule withholds the rounding of 0 (0 with every rounding rule in use). -/
theorem Wht.zero_amount (w : Wht) (p : Payment) (r : WhtRule) (h : w.ruleFor p = some r) (h0 : r.rateBp = 0) :
    w.amount p = w.round.ofTicks 0 := by
  simp [Wht.amount, h, h0]

theorem afterCredit_ge (liability withheld : Int) (r : Bool) :
    liability ≤ afterCredit liability withheld r + withheld := by
  unfold afterCredit; cases r <;> simp [pos] <;> omega

theorem flat_mono (f : FlatCapital) (hr : 0 ≤ f.rateBp) (hi : 0 ≤ f.inclusionBp) (hs : 0 < f.round.step)
    (hm : f.round.mode.isMonotoneMode) {x y : Int} (h : x ≤ y) : f.tax x ≤ f.tax y := by
  unfold FlatCapital.tax FlatCapital.base
  apply Rule.ofTicks_mono _ hs hm
  apply Int.mul_le_mul_of_nonneg_left _ hr
  apply divR_mono .down BP (by unfold BP; omega) (Or.inl rfl)
  apply Int.mul_le_mul_of_nonneg_left _ hi
  exact pos_mono (by omega)

theorem imputation_credit_nonneg (i : Imputation) (div : Int) (h : 0 ≤ i.creditBp) : 0 ≤ i.credit div := by
  have := Int.mul_nonneg h (pos_nonneg div)
  simp only [Imputation.credit, divR, BP]
  generalize i.creditBp * pos div = y at *
  omega

end TaxKernel.Global
