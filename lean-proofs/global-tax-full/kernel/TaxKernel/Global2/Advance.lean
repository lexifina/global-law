import TaxKernel.Global2.Vehicle

/-!
# TaxKernel.Global2.Advance (2.6.0, 2026-11-21): advance income tax collected on a transaction, credited against the year's income tax

Asia-Pacific session 6 (PK, read and not modelled): ITO 2001 s. 236C (the seller of immovable property, Division X of
Part IV of the First Schedule: 4.5 / 5 / 5.5 % of the gross consideration up to Rs 50 m, 100 m, above) and s. 236K (the
purchaser, Division XVIII: 3 / 3.5 / 4 % of the fair market value to 30 June 2025, 1.5 / 2 / 2.5 % from 1 July 2025,
Finance Act 2025) are **adjustable** advance income tax (s. 236K (2)): a prepayment of the year's income tax, not a
transfer tax. Booking them as a 4400 duty overstates the tax; ignoring them understates it for a person whose income tax
is smaller than the advance tax (the excess is not refunded unless claimed). Many codes have the same device (withholding
on property sales, advance tax on vehicles, cash withdrawals).

**The part** (`AdvanceTax`): on the entity's `disposals` (the seller: base = proceeds) or `purchases` (the buyer: base =
the assessed value when given, else the price) of the given asset kinds; the rate by the size of the base (`ceilings`
`(up to, bp)` for the **whole** base, `topBp` above) and, optionally, by the date of the transaction (`dateFrom`,
`dateTo`, ISO, inclusive; the record's `"date"`): the first `AdvanceRate` whose dates hold applies. A dated rate on an
undated record is **never guessed**: no charge, `unknown` lists it as grade C. The credit (`credit`, no default):
* `.adjustable`: credited against the year's income tax, the excess not refunded: due = gross − min(gross, the income
  tax still uncredited);
* `.refundable`: credited in full (the excess refunded): due 0 (the charge shows gross and credit);
* `.final`: not credited (a final tax): due = gross.

The year's income tax is the sum of the charges under 1100 booked **before** the family (the 1.x line's income tax,
surtaxes and local income tax, a stacked rule's charges), consumed in the order of the transactions; put every advance tax
of the model in one `advanceTaxFamily` after the income-tax families. Each charge books gross, the credit and due under
`oecd` (1100 by default; 4400 if the model shows the advance tax as a transaction tax), event `"disposal <i> (<kind>)"` /
`"purchase <i> (<kind>)"`, statute = the rate's provision and the credit provision.

Theorems: `advanceCharges_nil`, `advanceCharges_wf`, `advanceCharges_due_nonneg`, `advanceCharges_adjustable_total` (all
adjustable: the total due is Σ gross − min(Σ gross, income tax): what the advance tax adds to the year's income tax),
`advanceCharges_refundable` (due 0), `advanceTaxFamily_noItems` (an entity without such transactions is unchanged).
-/

namespace TaxKernel.Global
open Lean TaxKernel

inductive AdvanceOn where
  /-- the seller: the entity's disposals of these kinds, base = proceeds -/
  | disposals (kinds : List AssetKind)
  /-- the buyer: the entity's purchases of these kinds, base = the assessed value if given, else the price -/
  | purchases (kinds : List AssetKind)
  deriving Repr, Inhabited, BEq

inductive AdvanceCredit where
  | adjustable | refundable | final
  deriving Repr, DecidableEq, Inhabited, BEq

structure AdvanceRate where
  /-- `(up to, bp)`: the first ceiling the whole base does not exceed gives the rate -/
  ceilings : List (Int × Int) := []
  /-- above every ceiling -/
  topBp : Int
  /-- transactions dated on or after (ISO; `""`: open) -/
  dateFrom : String := ""
  /-- … and on or before (ISO; `""`: open) -/
  dateTo : String := ""
  statute : String
  deriving Repr, Inhabited

def AdvanceRate.bpOf (r : AdvanceRate) (base : Int) : Int :=
  match r.ceilings.find? (fun (c, _) => decide (base ≤ c)) with
  | some (_, b) => b
  | none => r.topBp

def AdvanceRate.dated (r : AdvanceRate) : Bool := r.dateFrom != "" || r.dateTo != ""

/-- The rate applies on that day (`some`), or cannot be decided (`none`: dated rate, undated record). A bound that is
not a date applies to nothing. -/
def AdvanceRate.on? (r : AdvanceRate) (day : Option Nat) : Option Bool :=
  if !r.dated then some true else
  match day with
  | none => none
  | some d =>
    match VehicleTax.windowBound r.dateFrom, VehicleTax.windowBound r.dateTo with
    | some lo, some hi =>
      some ((match lo with | none => true | some l => decide (l ≤ d)) && (match hi with | none => true | some h => decide (d ≤ h)))
    | _, _ => some false

structure AdvanceTax where
  name : String
  oecd : Oecd := .pit
  source : AdvanceOn
  rates : List AdvanceRate
  /-- how it is credited against the year's income tax (no default) -/
  credit : AdvanceCredit
  /-- the crediting provision (ITO 2001 s. 147, 168) -/
  creditStatute : String := ""
  round : Rule := {}
  deriving Repr, Inhabited

/-- One transaction the tax reads: base, the day of its `"date"` (`dayOrd`), event. -/
structure AdvanceItem where
  tax : AdvanceTax
  base : Int
  /-- the rate (`none`: dated rates and no date: grade C) -/
  rate? : Option (Option AdvanceRate)
  event : String
  deriving Inhabited

namespace AdvanceTax

/-- The first rate whose dates hold (`some none`: none applies; `none`: undecided). -/
def pick (rs : List AdvanceRate) (day : Option Nat) : Option (Option AdvanceRate) :=
  match rs with
  | [] => some none
  | r :: rs => match r.on? day with
    | some true => some (some r)
    | some false => pick rs day
    | none => none

def dayOfRecord (j : Json) : Option Nat := (isoYmd? (strField j "date")).map fun (y, m, d) => dayOrd y m d

/-- The transactions of the entity the tax reads, in order. -/
def items (t : AdvanceTax) (g : CanonGlobal) : List AdvanceItem :=
  match t.source with
  | .disposals ks =>
    (g.disposals.zipIdx.filter fun (d, _) => ks.contains d.kind).map fun (d, i) =>
      let j := (arrField g.raw "disposals").toList.getD i Json.null
      { tax := t, base := d.proceeds, rate? := pick t.rates (dayOfRecord j), event := s!"disposal {i + 1} ({d.kind.name})" }
  | .purchases ks =>
    (g.purchases.zipIdx.filter fun (p, _) => ks.contains p.kind).map fun (p, i) =>
      let j := (arrField g.raw "purchases").toList.getD i Json.null
      { tax := t, base := if p.assessed < 0 then p.price else p.assessed, rate? := pick t.rates (dayOfRecord j),
        event := s!"purchase {i + 1} ({p.kind.name})" }

end AdvanceTax

namespace AdvanceItem

def gross (it : AdvanceItem) : Int :=
  match it.rate? with
  | some (some r) => pos (it.tax.round.ofTicks (pos (r.bpOf it.base) * pos it.base))
  | _ => 0

def statute (it : AdvanceItem) : String :=
  match it.rate? with
  | some (some r) => r.statute ++ (if it.tax.creditStatute.isEmpty then "" else "; " ++ it.tax.creditStatute)
  | _ => ""

/-- Priced: a rate applies. -/
def priced (it : AdvanceItem) : Bool := match it.rate? with | some (some _) => true | _ => false

/-- The credit given the income tax still uncredited `cap`. -/
def creditOf (it : AdvanceItem) (cap : Int) : Int :=
  match it.tax.credit with
  | .adjustable => min it.gross (pos cap)
  | .refundable => it.gross
  | .final => 0

/-- The income tax it uses up. -/
def usedOf (it : AdvanceItem) (cap : Int) : Int :=
  if it.tax.credit == .final then 0 else min it.gross (pos cap)

theorem gross_nonneg (it : AdvanceItem) : 0 ≤ it.gross := by
  unfold gross; split
  · exact pos_nonneg _
  · exact Int.le_refl 0

end AdvanceItem

/-- The charges of the priced items in order, `cap` the year's income tax not yet credited. -/
def advanceCharges (cap : Int) : List AdvanceItem → List Charge
  | [] => []
  | it :: its =>
    if it.priced then
      charge it.tax.oecd it.tax.name it.base (fun _ => it.base) (fun _ => it.gross) (credit := it.creditOf cap)
        (refundable := true) (event := it.event) (statute := it.statute)
      :: advanceCharges (cap - it.usedOf cap) its
    else advanceCharges cap its

/-- The year's income tax the advance taxes are credited against: every 1100 charge booked before. -/
def advanceCap (acc : List Charge) : Int := isum ((acc.filter (·.oecd == .pit)).map (·.due))

/-- The advance taxes of a model, as one family (after the income-tax families). -/
def advanceTaxFamily (name : String) (ts : List AdvanceTax) : Family :=
  { name := s!"1100 {name}", covers := (ts.map (·.oecd)).eraseDups,
    run := fun _ g acc => advanceCharges (advanceCap acc) (ts.flatMap (·.items g)) }

/-- For `unsupported`: transactions whose rate depends on a date not given (grade C). -/
def advanceTaxUnknown (ts : List AdvanceTax) (g : CanonGlobal) : List String :=
  (ts.flatMap (·.items g)).filterMap fun it =>
    if it.rate?.isNone then
      some s!"{it.tax.oecd.code} {it.tax.name}: {it.event}: the rate depends on the date of the transaction, not given (grade C)"
    else none

theorem advanceCharges_nil (cap : Int) : advanceCharges cap [] = [] := rfl

theorem advanceCharges_wf : ∀ (cap : Int) (its : List AdvanceItem), ∀ c ∈ advanceCharges cap its, c.WF
  | _, [] => by simp [advanceCharges]
  | cap, it :: its => by
    intro c hc
    unfold advanceCharges at hc
    split at hc
    · rcases List.mem_cons.mp hc with h | h
      · subst h; exact charge_wf ..
      · exact advanceCharges_wf _ its c h
    · exact advanceCharges_wf _ its c hc

/-- Every charge is between 0 and its gross. -/
theorem advanceCharges_due_nonneg : ∀ (cap : Int) (its : List AdvanceItem), ∀ c ∈ advanceCharges cap its, 0 ≤ c.due
  | _, [] => by simp [advanceCharges]
  | cap, it :: its => by
    intro c hc
    unfold advanceCharges at hc
    split at hc
    · rcases List.mem_cons.mp hc with h | h
      · subst h
        have hg := it.gross_nonneg
        simp only [charge, appliedCredit, ↓reduceIte, AdvanceItem.creditOf]
        split <;> omega
      · exact advanceCharges_due_nonneg _ its c h
    · exact advanceCharges_due_nonneg _ its c hc

/-- **What adjustable advance taxes add to the year**: with every item adjustable and priced, the charges' total is
Σ gross − min(Σ gross, income tax): the advance tax beyond the year's income tax (0 when the income tax covers it). -/
theorem advanceCharges_adjustable_total : ∀ (cap : Int) (its : List AdvanceItem),
    (∀ it ∈ its, it.tax.credit = .adjustable ∧ it.priced = true) →
    isum ((advanceCharges cap its).map (·.due)) = isum (its.map (·.gross)) - min (isum (its.map (·.gross))) (pos cap)
  | cap, [] => by intro _; have := pos_nonneg cap; simp [advanceCharges, isum]; omega
  | cap, it :: its => by
    intro h
    obtain ⟨ha, hp⟩ := h it (by simp)
    have ih := advanceCharges_adjustable_total (cap - it.usedOf cap) its (fun x hx => h x (by simp [hx]))
    have hS : 0 ≤ isum (its.map (·.gross)) :=
      isum_nonneg _ (fun x hx => by obtain ⟨y, _, rfl⟩ := List.mem_map.mp hx; exact y.gross_nonneg)
    have hg := it.gross_nonneg
    have hu : it.usedOf cap = min it.gross (pos cap) := by unfold AdvanceItem.usedOf; rw [ha]; rfl
    have hc : it.creditOf cap = min it.gross (pos cap) := by unfold AdvanceItem.creditOf; rw [ha]
    simp only [advanceCharges, hp, ↓reduceIte, List.map_cons, isum]
    rw [ih, hu]
    simp only [charge, appliedCredit, ↓reduceIte, hc]
    simp only [pos] at *
    omega

/-- A refundable advance tax adds nothing: every charge is 0. -/
theorem advanceCharges_refundable : ∀ (cap : Int) (its : List AdvanceItem),
    (∀ it ∈ its, it.tax.credit = .refundable) → ∀ c ∈ advanceCharges cap its, c.due = 0
  | _, [] => by simp [advanceCharges]
  | cap, it :: its => by
    intro h c hc
    unfold advanceCharges at hc
    split at hc
    · rcases List.mem_cons.mp hc with e | e
      · subst e
        simp [charge, appliedCredit, AdvanceItem.creditOf, h it (by simp)]
      · exact advanceCharges_refundable _ its (fun x hx => h x (by simp [hx])) c e
    · exact advanceCharges_refundable _ its (fun x hx => h x (by simp [hx])) c hc

/-- An entity without such transactions gets no advance-tax charge and no grade-C line. -/
theorem advanceTaxFamily_noItems (n : String) (ts : List AdvanceTax) (args : List String) (g : CanonGlobal)
    (acc : List Charge) (h : ∀ t ∈ ts, t.items g = []) :
    (advanceTaxFamily n ts).run args g acc = [] ∧ advanceTaxUnknown ts g = [] := by
  have : ts.flatMap (·.items g) = [] := by simp only [List.flatMap_eq_nil_iff]; exact h
  simp [advanceTaxFamily, advanceTaxUnknown, this, advanceCharges]

end TaxKernel.Global
