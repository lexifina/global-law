import TaxKernel.Global2.Assets
import TaxKernel.Global2.Vehicle

/-!
# TaxKernel.Global2.Stack (2.5.0, 2026-11-21; 2.6.0, 2.7.0, 2.8.0): income stacked on the 1.x income tax (R4-13-1)

Many statutes tax an individual's capital gains (and some dividends or interest) by **adding an included share of them
to taxable income**, so that they bear the personal income tax at the marginal rate, on top of the other income: ZA
Income Tax Act s. 26A and Eighth Schedule (40 % of the net gain after the R40 000 annual exclusion), CZ ZDP § 10 (other
income at 15 % / 23 %), SK, LU (speculative gains), CA (50 % inclusion) and many more. The 2.0 model computes the 1.x
PIT once, on the routed household (`GlobalModel.pit`, `route`), and a family could not call it on a changed household.
This module makes the call:

    charge(rule k) = PIT(1.x household + included amounts of rules 1 … k)
                   − PIT(1.x household + included amounts of rules 1 … k−1)

where PIT is the 1.x line's income tax (`jsonIncomeTax`: income tax + surtaxes + local income tax, the 1100 lines of
`legacyCharges`). The 1.x line itself is never changed (`pit` is computed on `route g` as before, `withStack_pit`): the
stacked tax is booked as charges of its own under 1100 (the local income tax part as a `.local` charge of its own).

**The included amount** (`StackRule`) is the year's net of
* the gains on the entity's `disposals` of the kinds `gainKinds` (`AssetKind.every`: all), each through a 2.0 `GainRule`
  (exemption after a holding period, main home with or without a cap, minimum stake, indexation by the disposal's
  `indexBp`, inclusion by holding period), and
* the `incomes` items of the kinds `incomeKinds` (domestic, foreign or both: `foreign`),

per natural person (`pool := .person`, the default: each person's own exclusion, ZA para 5) or for the household
(`.household`: one exclusion), less the annual `exclusion` (a 2.0 `AnnualExempt`: allowance or threshold), times
`inclusionBp` (rounded down; `exclusionAfterInclusion` for statutes that include first). Losses offset gains and income
of the same rule and year; a net loss gives 0 (no carry-forward). Write one rule per regime; the rules are stacked in
the order given.

**Where it enters the 1.x household** (`into : StackField`, **no default**): a household field (`interest`,
`dividends`, `capitalGains`, `rentalIncome`) or the item's person's own field (`wages`, `selfEmployment`, `pension`:
each person's amount goes to that adult; such a rule always works per person). Choose a field the 1.x model taxes **in
full at the scale** (ZA: `selfEmployment`, which `ZaTax.personTI` adds in full); a 1.x model that already applies the
statute's inclusion and exclusion to `capitalGains` takes the gross gain there (`inclusionBp := 10000`, no exclusion).
The amount is added both to the `Canon` field and to the household's input line `raw` (an exact JSON-number addition,
`jsonNumAdd_int`), so a model wrapped by `ofCountry` (it reads the structure) and one wrapped by `ofLine` (it re-reads
the line: the exe-level models) price the same household.

**Never guessed** (`stackUnknown`, `"1100 <name>: … (grade C)"` in `unsupported`; no charge for the rule): an item of
a person who is not an adult of the household (per-person rules); a 1.x line with an `"error"`; a household whose input
line cannot carry the amount (`stackRawAgrees` fails) while the 1.x line does not move; and every later rule of the
entity (it would be stacked on a slice that was not priced). Company entities: no stacking.

**Use** (`import TaxKernel.Global2`):

    def zaCgt : StackRule := { name := "Capital gains tax (taxable capital gain in taxable income)", statute := "…",
      gainKinds := AssetKind.every, gainRule := { mainHomeExempt := true, mainHomeCap := 2000000 },
      exclusion := { amount := 40000 }, inclusionBp := 4000, into := .selfEmployment }
    def model : GlobalModel := ({ (GlobalModel.ofCountry ZaTax.country) with families := … }).withStack [zaCgt]

`withStack` adds the family (last) and appends the grade-C lines to `unsupported`; call it on the final model (it
captures `pit` and `route`).

**2.6.0 (R1 Europe pass 10): a share of the charge, or the global (average) rate.** Two last fields of `StackRule`,
both defaulting to 2.5.0 (`StackSlice.due_default`):
* `shareBp` (10000): the charge is that share of what `mode` gives (LU's alternative reading
  "(PIT(income + gain) − PIT(income)) × ½" is `shareBp := 5000` with `.marginal`);
* `mode` (`.marginal`): `.averageRate "taxableIncome"` charges the included amount at the **global rate of the 1.x line
  with the amount**, PIT(after) / taxable income(after), the taxable income read from that line (top level or
  `"detail"`) under the key given. LU L.I.R. art. 131 (1) c (gains of art. 99ter and 100 at half the global rate of the
  adjusted taxable income, art. 132 (2)): `{ …, into := .rentalIncome, mode := .averageRate "taxableIncome",
  shareBp := 5000 }`. The 1.x line (the ordinary income at the tariff, art. 131 (1) a) is unchanged. A 1.x line with
  the amount that gives no positive taxable income under the key, or a negative income tax, prices nothing: no charge,
  grade C (`StackSlice.rated`; never a rate guessed). The central and local parts are each rounded down.

**2.7.0 (R4-18-3): an elective flat rate.** `electFlatBp` (−1: none): the charge is the lower of the stacked charge and
`electFlatBp` × the included amount (GH Act 896 First Schedule para 1 (3) as substituted by Act 1094: a gain on an
investment asset is chargeable income, or at the individual's election 25 %: `electFlatBp := 2500`); the statute then
ends with "; elective flat rate 2500 bp taken (lower than the stacked tax)" and no local part is booked. The election is
the taxpayer's, presumed taken when it is lower; a later rule still stacks on the line with the amount
(`StackSlice.due_noElect`, `dueTotal_le_core`; `due_default` now also names `electFlatBp < 0`).

**2.7.0 (FT reviewer 7; IMPROVE_FT R5-6): a date window, and one global rate for the whole stack.** Three last fields
of `StackRule`, defaults = 2.6.0 (`StackRule.wItems_noWindow`, `undated_noWindow`, `shareStackRate_none`):
* `dateFrom` / `dateTo` (ISO, inclusive, `""` open): the rule takes only the disposals and income items whose record's
  `"date"` (`"YYYY-MM-DD"`) lies in the window (`AdvanceRate` semantics; a bound that is not a date takes nothing). **An
  item of the rule's kinds without a date, when the rule has a window, is never guessed**: the rule is not priced (no
  charge, `"1100 <name>: disposal 2 (realEstate) has no date (the rule takes items dated …) (grade C)"`), nor are the
  later rules (they would stack on an unpriced slice). LU art. 99ter, 2025: a quarter of the global rate for sales to
  30 September 2025 (Loi du 22 mai 2024 art. 14 as extended by the laws of 4 April and 27 June 2025), half from
  1 October (art. 131 (1) c): two rules with `dateTo := "2025-09-30"` / `dateFrom := "2025-10-01"` and `shareBp`
  2500 / 5000. The art. 99bis derogation that turns on the sale date is two rules with different `gainRule`s and the
  same kind of windows.
* `rateFromStack` (`false`): for `.averageRate`, take the global rate from the 1.x line with the amounts of **every** rule
  of the stack (the adjusted taxable income including every stacked amount), not only of this rule and the earlier
  ones; LU's two windows then share one rate. It needs every rule of the stack priced (else grade C). `.marginal` rules
  ignore it.

**2.8.0 (R1 Europe pass 17): an undated item the rule taxes at 0 does not block a window.** `undatedIfTaxable` (`false`,
the 2.7.0 behaviour): an item of the rule's kinds without a date is undecided (grade C) only when its amount under the rule
(`gainRule.taxable` of a disposal, the amount of an income item) is not 0; an undated sale of a main home that `gainRule`
exempts whatever the date (LU art. 99bis / 99ter, `mainHomeExempt`) then leaves the rule priced. A loss is still
undecided. `StackRule.undated_v27` (the option off: the 2.7.0 list), `undated_taxable` (with it every undecided item has a
non-zero amount).

Theorems: `jsonNumAdd_int`, `StackField.addTo_zero`, `addAll_zero`, `addAll_length`, `AnnualExempt.apply_nonneg`,
`StackRule.included_nonneg`, `amounts_nonneg`, `items_ofCanon`, `StackSlice.charges_sum` (a priced rule's charges add
up to its due; PIT with − PIT without for a 2.5.0 rule: `due_default`), `dueTotal_nonneg`, `dues_zero`,
`stackSlices_shape`, `stackCharges_nonneg` (≥ 0 when the 1.x income tax does not fall
as the field rises: `StackMono`), `stackCharges_zero` (included amount 0: every charge 0), `stackCharges_noItems`,
`withStack_pit` (the 1.x line unchanged), `withStack_rawCharges`, `withStack_noItems` and `withStack_ofCanon` (an
entity without stacked items gets the very same output).
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-! ## Adding to the household: the structure and its input line together -/

/-- `n + d` exactly (a JSON number is `mantissa / 10^exponent`). -/
def jsonNumAdd (n : JsonNumber) (d : Int) : JsonNumber :=
  ⟨n.mantissa + d * (10 : Int) ^ n.exponent, n.exponent⟩

/-- The kernel reads `n + d` as `n` read, plus `d` (so an `ofLine` model sees exactly the amount added). -/
theorem jsonNumAdd_int (n : JsonNumber) (d : Int) : numToInt (jsonNumAdd n d) = numToInt n + d := by
  unfold numToInt jsonNumAdd
  simp only
  generalize hP : (10 : Int) ^ n.exponent = P
  have hp : 0 < P := by rw [← hP]; exact Int.pow_pos (by decide)
  have e : 2 * (n.mantissa + d * P) + P = (2 * n.mantissa + P) + d * (2 * P) := by
    rw [Int.mul_add, Int.mul_left_comm d 2 P]; omega
  rw [e, Int.add_mul_ediv_right _ _ (by omega)]

/-- Add `d` to the number at key `k` of a JSON object (absent or not a number: it becomes `d`, as `intField` read it
as 0); `d = 0` or not an object: unchanged. -/
def jsonAddField (j : Json) (k : String) (d : Int) : Json :=
  if d = 0 then j else
  match j with
  | .obj _ => j.setObjVal! k (match j.getObjVal? k with
      | .ok (.num n) => .num (jsonNumAdd n d)
      | _ => Lean.toJson d)
  | _ => j

/-- Add `d` to field `k` of adult `i` in the line's `"adults"` array. -/
def jsonAddAdult (j : Json) (i : Nat) (k : String) (d : Int) : Json :=
  if d = 0 then j else
  match j with
  | .obj _ => match j.getObjVal? "adults" with
    | .ok (.arr a) => if i < a.size then j.setObjVal! "adults" (.arr (a.modify i (jsonAddField · k d))) else j
    | _ => j
  | _ => j

theorem jsonAddField_zero (j : Json) (k : String) : jsonAddField j k 0 = j := by simp [jsonAddField]
theorem jsonAddAdult_zero (j : Json) (i : Nat) (k : String) : jsonAddAdult j i k 0 = j := by simp [jsonAddAdult]

/-- `f` applied to element `i` (no such element: unchanged). -/
def stackModifyNth {α : Type} (f : α → α) : List α → Nat → List α
  | [], _ => []
  | x :: xs, 0 => f x :: xs
  | x :: xs, n + 1 => x :: stackModifyNth f xs n

theorem stackModifyNth_id {α : Type} (f : α → α) (hf : ∀ a, f a = a) : ∀ (l : List α) (i : Nat), stackModifyNth f l i = l
  | [], _ => rfl
  | x :: xs, 0 => by simp [stackModifyNth, hf]
  | x :: xs, n + 1 => by simp [stackModifyNth, stackModifyNth_id f hf xs n]

theorem stackModifyNth_length {α : Type} (f : α → α) : ∀ (l : List α) (i : Nat), (stackModifyNth f l i).length = l.length
  | [], _ => rfl
  | x :: xs, 0 => by simp [stackModifyNth]
  | x :: xs, n + 1 => by simp [stackModifyNth, stackModifyNth_length f xs n]

/-- The 1.x household field an included amount enters. -/
inductive StackField where
  | interest | dividends | capitalGains | rentalIncome
  /-- the item's person's own field (each person's amount goes to that adult) -/
  | wages | selfEmployment | pension
  deriving Repr, DecidableEq, Inhabited, BEq

namespace StackField

def name : StackField → String
  | .interest => "interest" | .dividends => "dividends" | .capitalGains => "capitalGains"
  | .rentalIncome => "rentalIncome" | .wages => "wages" | .selfEmployment => "selfEmployment" | .pension => "pension"

/-- A field of one adult (else of the household). -/
def perAdult : StackField → Bool
  | .wages | .selfEmployment | .pension => true
  | _ => false

/-- Add `d` to the field (of adult `i` for an adult field), in the structure and in the input line. -/
def addTo (f : StackField) (c : Canon) (i : Nat) (d : Int) : Canon :=
  match f with
  | .interest => { c with interest := c.interest + d, raw := jsonAddField c.raw "interest" d }
  | .dividends => { c with dividends := c.dividends + d, raw := jsonAddField c.raw "dividends" d }
  | .capitalGains => { c with capitalGains := c.capitalGains + d, raw := jsonAddField c.raw "capitalGains" d }
  | .rentalIncome => { c with rentalIncome := c.rentalIncome + d, raw := jsonAddField c.raw "rentalIncome" d }
  | .wages => { c with adults := stackModifyNth (fun a => { a with wages := a.wages + d }) c.adults i,
                       raw := jsonAddAdult c.raw i "wages" d }
  | .selfEmployment => { c with adults := stackModifyNth (fun a => { a with selfEmployment := a.selfEmployment + d }) c.adults i,
                                raw := jsonAddAdult c.raw i "selfEmployment" d }
  | .pension => { c with adults := stackModifyNth (fun a => { a with pension := a.pension + d }) c.adults i,
                         raw := jsonAddAdult c.raw i "pension" d }

/-- Add every `(person, amount)` in turn. -/
def addAll (f : StackField) (c : Canon) (xs : List (Nat × Int)) : Canon :=
  xs.foldl (fun c x => f.addTo c x.1 x.2) c

theorem addTo_zero (f : StackField) (c : Canon) (i : Nat) : f.addTo c i 0 = c := by
  cases c
  cases f <;> simp [addTo, jsonAddField_zero, jsonAddAdult_zero] <;>
    exact stackModifyNth_id _ (fun a => by cases a; simp) _ _

theorem addTo_length (f : StackField) (c : Canon) (i : Nat) (d : Int) : (f.addTo c i d).adults.length = c.adults.length := by
  cases f <;> simp [addTo, stackModifyNth_length]

theorem addAll_zero (f : StackField) : ∀ (c : Canon) (xs : List (Nat × Int)), (∀ x ∈ xs, x.2 = 0) → f.addAll c xs = c
  | _, [], _ => rfl
  | c, x :: xs, h => by
    simp only [addAll, List.foldl_cons]
    rw [h x (by simp), addTo_zero]
    exact addAll_zero f c xs (fun y hy => h y (by simp [hy]))

theorem addAll_length (f : StackField) : ∀ (c : Canon) (xs : List (Nat × Int)), (f.addAll c xs).adults.length = c.adults.length
  | _, [] => rfl
  | c, x :: xs => by
    simp only [addAll, List.foldl_cons]
    rw [← addTo_length f c x.1 x.2]
    exact addAll_length f _ xs

end StackField

/-- The household's input line carries the same household as the structure (what an `ofLine` model re-reads). -/
def stackRawAgrees (c : Canon) : Bool :=
  match parseCanon c.raw with
  | .ok p => p.interest == c.interest && p.dividends == c.dividends && p.capitalGains == c.capitalGains
      && p.rentalIncome == c.rentalIncome && p.adults.length == c.adults.length
      && (p.adults.zip c.adults).all fun (x, y) =>
          x.wages == y.wages && x.selfEmployment == y.selfEmployment && x.pension == y.pension
  | .error _ => false

/-! ## The rule -/

/-- Whose items share one exclusion: each natural person's (`person`) or the household's (`household`). -/
inductive StackPool where
  | person | household
  deriving Repr, DecidableEq, Inhabited, BEq

/-- Every asset kind (a rule on every disposal). -/
def AssetKind.every : List AssetKind :=
  [.home, .realEstate, .land, .listedShares, .unlistedShares, .bonds, .deposits, .business, .pensionFund, .vehicle, .other]

theorem AssetKind.mem_every (k : AssetKind) : k ∈ AssetKind.every := by cases k <;> simp [AssetKind.every]

theorem AnnualExempt.apply_nonneg (a : AnnualExempt) (net : Int) : 0 ≤ a.apply net := by
  unfold AnnualExempt.apply pos
  split
  · omega
  · split
    · split <;> omega
    · exact Int.le_max_left _ _

/-- 2.6.0: how a stacked rule's charge is taken from the 1.x lines without (`before`) and with (`after`) its amount.
* `marginal` (2.5.0): PIT(after) − PIT(before), the amount at the marginal rate;
* `averageRate taxableKey`: the included amount × the **global (average) rate of the 1.x line with the amount**,
  PIT(after) / taxable income(after), the taxable income being the number the 1.x line gives under `taxableKey` (at the
  top level of the line or in its `"detail"`, e.g. `"taxableIncome"`). LU L.I.R. art. 131 (1) c: "un taux égal à la
  moitié du taux global correspondant au revenu imposable ajusté" (with `shareBp := 5000`). The 1.x line itself (the
  ordinary income at the tariff, art. 131 (1) a) is unchanged. -/
inductive StackMode where
  | marginal
  | averageRate (taxableKey : String)
  deriving Repr, DecidableEq, Inhabited, BEq

/-- An amount taxed by adding an included share of it to the income the 1.x PIT taxes. -/
structure StackRule where
  /-- the charge's tax name -/
  name : String
  /-- the provisions (inclusion, exclusion, exemptions; the rates are the 1.x model's) -/
  statute : String
  /-- disposals of these kinds feed the amount (`AssetKind.every`: all) -/
  gainKinds : List AssetKind := []
  /-- each disposal's gain: exemptions, main home, stake, indexation (by the disposal's `indexBp`), inclusion by holding -/
  gainRule : GainRule := {}
  /-- income items (`incomes`) of these kinds feed the amount -/
  incomeKinds : List IncomeKind := []
  /-- income items: `some true` foreign only, `some false` domestic only, `none` both -/
  foreign : Option Bool := none
  /-- the annual exclusion on the net (allowance, or threshold with `threshold := true`) -/
  exclusion : AnnualExempt := {}
  pool : StackPool := .person
  /-- included share of the net after the exclusion, bp (ZA 40 % = 4000) -/
  inclusionBp : Int := 10000
  /-- the inclusion first, then the exclusion -/
  exclusionAfterInclusion : Bool := false
  /-- where the included amount enters the 1.x household (**no default**) -/
  into : StackField
  /-- the charge's event (`""`: the items, "disposal 1 (listedShares), income 2 (interest)") -/
  event : String := ""
  /-- 2.6.0: how the charge is taken from the 1.x lines (`.marginal`: PIT with − PIT without, as 2.5.0) -/
  mode : StackMode := .marginal
  /-- 2.6.0: share of that charge, bp (LU art. 131 (1) c: half, 5000; 10000: all of it, as 2.5.0) -/
  shareBp : Int := 10000
  /-- 2.7.0: only items whose record's `"date"` is on or after this day (ISO; `""`: open) -/
  dateFrom : String := ""
  /-- 2.7.0: only items whose record's `"date"` is on or before this day (ISO; `""`: open) -/
  dateTo : String := ""
  /-- 2.7.0: `.averageRate` at the global rate of the 1.x line with every rule's amount (the whole stack) -/
  rateFromStack : Bool := false
  /-- 2.7.0 (R4-18-3): an elective flat rate, bp (−1: none): the charge is the lower of the stacked charge and this rate
  × the included amount (GH Act 896 First Schedule para 1 (3): 25 %, 2500) -/
  electFlatBp : Int := -1
  /-- 2.8.0 (R1 Europe pass 17): an undated item counts as undecided only when its amount under the rule is not 0 -/
  undatedIfTaxable : Bool := false
  deriving Repr, Inhabited

namespace StackRule

def gainOf (r : StackRule) (d : Disposal) : Int := r.gainRule.taxable d.indexBp BP d

def takesIncome (r : StackRule) (x : Income) : Bool :=
  r.incomeKinds.contains x.kind && (match r.foreign with | none => true | some b => b == x.foreign)

/-- The items the rule reads: (person, amount, label). -/
def items (r : StackRule) (g : CanonGlobal) : List (Nat × Int × String) :=
  ((g.disposals.zipIdx.filter fun (d, _) => r.gainKinds.contains d.kind).map fun (d, i) =>
      (d.person, r.gainOf d, s!"disposal {i + 1} ({d.kind.name})"))
  ++ ((g.incomes.zipIdx.filter fun (x, _) => r.takesIncome x).map fun (x, i) =>
      (x.person, x.amount, s!"income {i + 1} ({x.kind.name})"))

/-- 2.7.0: the rule has a date window. -/
def hasWindow (r : StackRule) : Bool := r.dateFrom != "" || r.dateTo != ""

/-- 2.7.0: the day (`dayOrd`) of a record's `"date"`; `none` when it gives no calendar date. -/
def recordDay (j : Json) : Option Nat := (isoYmd? (strField j "date")).map fun (y, m, d) => dayOrd y m d

/-- 2.7.0: the items with the day of their record's `"date"`, in the order of `items`. -/
def itemDays (r : StackRule) (g : CanonGlobal) : List ((Nat × Int × String) × Option Nat) :=
  ((g.disposals.zipIdx.filter fun (d, _) => r.gainKinds.contains d.kind).map fun (d, i) =>
      ((d.person, r.gainOf d, s!"disposal {i + 1} ({d.kind.name})"),
        recordDay ((arrField g.raw "disposals").toList.getD i Json.null)))
  ++ ((g.incomes.zipIdx.filter fun (x, _) => r.takesIncome x).map fun (x, i) =>
      ((x.person, x.amount, s!"income {i + 1} ({x.kind.name})"),
        recordDay ((arrField g.raw "incomes").toList.getD i Json.null)))

theorem itemDays_fst (r : StackRule) (g : CanonGlobal) : (r.itemDays g).map Prod.fst = r.items g := by
  simp [itemDays, items, List.map_map, Function.comp_def]

/-- 2.7.0: an item of that day is in the window (`some`), or it cannot be told (`none`: a window and no date). A bound
that is not a date takes nothing. -/
def inWindow? (r : StackRule) (day : Option Nat) : Option Bool :=
  if !r.hasWindow then some true else
  match day with
  | none => none
  | some d =>
    match VehicleTax.windowBound r.dateFrom, VehicleTax.windowBound r.dateTo with
    | some lo, some hi =>
      some ((match lo with | none => true | some l => decide (l ≤ d)) && (match hi with | none => true | some h => decide (d ≤ h)))
    | _, _ => some false

/-- 2.7.0: **the items the rule takes**: all of them without a window, else those dated inside it. -/
def wItems (r : StackRule) (g : CanonGlobal) : List (Nat × Int × String) :=
  if !r.hasWindow then r.items g else ((r.itemDays g).filter fun x => r.inWindow? x.2 == some true).map (·.1)

/-- 2.7.0: items of the rule's kinds whose date the window needs and the record does not give (grade C). -/
def undated (r : StackRule) (g : CanonGlobal) : List (Nat × Int × String) :=
  if !r.hasWindow then [] else
    ((r.itemDays g).filter fun x => (r.inWindow? x.2).isNone && (!r.undatedIfTaxable || x.1.2.1 != 0)).map (·.1)

/-- 2.8.0: without `undatedIfTaxable` the undecided items are those of 2.7.0. -/
theorem undated_v27 (r : StackRule) (g : CanonGlobal) (h : r.undatedIfTaxable = false) :
    r.undated g = if !r.hasWindow then [] else ((r.itemDays g).filter fun x => (r.inWindow? x.2).isNone).map (·.1) := by
  simp [undated, h]

/-- 2.8.0: with `undatedIfTaxable` an undecided item has a non-zero amount under the rule. -/
theorem undated_taxable (r : StackRule) (g : CanonGlobal) (h : r.undatedIfTaxable = true) :
    ∀ it ∈ r.undated g, it.2.1 ≠ 0 := by
  intro it hit
  unfold undated at hit
  split at hit
  · simp at hit
  · simp only [List.mem_map, List.mem_filter, h, Bool.not_true, Bool.false_or, Bool.and_eq_true, bne_iff_ne,
      ne_eq] at hit
    obtain ⟨x, ⟨_, _, hx⟩, rfl⟩ := hit
    exact hx

theorem wItems_noWindow (r : StackRule) (g : CanonGlobal) (h : r.hasWindow = false) : r.wItems g = r.items g := by
  simp [wItems, h]

theorem undated_noWindow (r : StackRule) (g : CanonGlobal) (h : r.hasWindow = false) : r.undated g = [] := by
  simp [undated, h]

/-- The window as text. -/
def windowText (r : StackRule) : String :=
  if r.dateFrom != "" && r.dateTo != "" then s!"dated {r.dateFrom} to {r.dateTo}"
  else if r.dateFrom != "" then s!"dated from {r.dateFrom}" else s!"dated to {r.dateTo}"

/-- The rule works per person (its pool, or an adult field). -/
def perPerson (r : StackRule) : Bool := r.pool == .person || r.into.perAdult

/-- Items of a person who is not one of the `n` adults (per-person rules only). -/
def unplaced (r : StackRule) (n : Nat) (g : CanonGlobal) : List (Nat × Int × String) :=
  if r.perPerson then (r.wItems g).filter (fun it => n ≤ it.1) else []

/-- The included amount of a net: exclusion, then inclusion (or the other way round). -/
def included (r : StackRule) (net : Int) : Int :=
  if r.exclusionAfterInclusion then r.exclusion.apply (divR .down (r.inclusionBp * net) BP)
  else divR .down (r.inclusionBp * r.exclusion.apply net) BP

/-- The included amount per adult (`(p, x)` for each of the `n` adults) or of the household (`[(0, x)]`). -/
def amounts (r : StackRule) (n : Nat) (g : CanonGlobal) : List (Nat × Int) :=
  let its := r.wItems g
  if r.perPerson then (List.range n).map fun p => (p, r.included (isum ((its.filter (·.1 == p)).map (·.2.1))))
  else [(0, r.included (isum (its.map (·.2.1))))]

/-- The statutory base shown on the charge: the net of the items before exclusion and inclusion. -/
def base (r : StackRule) (g : CanonGlobal) : Int := isum ((r.wItems g).map (·.2.1))

def eventOf (r : StackRule) (g : CanonGlobal) : String :=
  if r.event.isEmpty then ", ".intercalate ((r.wItems g).map (·.2.2)) else r.event

theorem included_nonneg (r : StackRule) (h : 0 ≤ r.inclusionBp) (net : Int) : 0 ≤ r.included net := by
  unfold included
  split
  · exact AnnualExempt.apply_nonneg _ _
  · simp only [divR]
    exact Int.ediv_nonneg (Int.mul_nonneg h (AnnualExempt.apply_nonneg _ _)) (by decide)

theorem amounts_nonneg (r : StackRule) (h : 0 ≤ r.inclusionBp) (n : Nat) (g : CanonGlobal) :
    ∀ x ∈ r.amounts n g, 0 ≤ x.2 := by
  intro x hx
  unfold amounts at hx
  split at hx
  · obtain ⟨p, _, rfl⟩ := List.mem_map.mp hx
    exact included_nonneg r h _
  · simp only [List.mem_singleton] at hx
    subst hx
    exact included_nonneg r h _

/-- A 1.x household has nothing to stack. -/
theorem items_ofCanon (r : StackRule) (c : Canon) : r.items (CanonGlobal.ofCanon c) = [] := by
  simp [items, CanonGlobal.ofCanon]

end StackRule

/-! ## Slices: one rule priced on top of the earlier ones -/

/-- The local income tax of a 1.x line (the `.local` 1100 line of `legacyCharges`). -/
def jsonLocalIncomeTax (j : Json) : Int := jInt j "localIncomeTax"

/-- The 1.x line is an error line. -/
def stackErrorLine (j : Json) : Bool := match j.getObjVal? "error" with | .ok _ => true | .error _ => false

/-- One rule priced on top of the earlier ones: the 1.x lines without (`before`) and with (`after`) its amount. -/
structure StackSlice where
  rule : StackRule
  base : Int
  included : Int
  before : Json
  after : Json
  event : String
  /-- priced; otherwise `why` says why not (grade C) -/
  ok : Bool
  why : String := ""
  /-- 2.7.0: the 1.x line the global rate is read from (`none`: `after`; `rateFromStack`: the whole stack's line) -/
  rateLine : Option Json := none
  deriving Inhabited

namespace StackSlice

/-- PIT with − PIT without. -/
def total (s : StackSlice) : Int := jsonIncomeTax s.after - jsonIncomeTax s.before

def localPart (s : StackSlice) : Int := jsonLocalIncomeTax s.after - jsonLocalIncomeTax s.before

/-- `share` bp of `x`, rounded down (10000: `x` itself; a negative share reads as 0). -/
def stackShare (share x : Int) : Int := if share = BP then x else divR .down (x * pos share) BP

/-- `x × share × tax / taxable`, rounded down (all parts taken at least 0; 0 when `taxable ≤ 0`). -/
def stackAtRate (x share tax taxable : Int) : Int :=
  if taxable ≤ 0 then 0 else divR .down (pos x * pos share * pos tax) (taxable * BP)

/-- A number of a 1.x line: at the top level, else in its `"detail"`. -/
def stackLineInt? (j : Json) (k : String) : Option Int :=
  match j.getObjVal? k with
  | .ok (.num n) => some (numToInt n)
  | _ => match j.getObjVal? "detail" with
    | .ok d => match d.getObjVal? k with
      | .ok (.num n) => some (numToInt n)
      | _ => none
    | .error _ => none

/-- 2.7.0: the 1.x line the global rate is read from. -/
def rateOn (s : StackSlice) : Json := s.rateLine.getD s.after

/-- 2.6.0: the global rate can be taken (always for `.marginal`; for `.averageRate k`: the 1.x line with the amount
gives `k`, positive (or 0 with no income tax: a rate of 0), and a non-negative income tax; or nothing is included). -/
def rated (s : StackSlice) : Bool :=
  match s.rule.mode with
  | .marginal => true
  | .averageRate k =>
    s.included == 0 || (match stackLineInt? s.rateOn k with
      | some t => (decide (0 < t) || jsonIncomeTax s.rateOn == 0)
          && decide (0 ≤ jsonIncomeTax s.rateOn - jsonLocalIncomeTax s.rateOn)
          && decide (0 ≤ jsonLocalIncomeTax s.rateOn)
      | none => false)

/-- 2.6.0: the local income tax part of the charge. -/
def coreLocal (s : StackSlice) : Int :=
  match s.rule.mode with
  | .marginal => stackShare s.rule.shareBp s.localPart
  | .averageRate k => stackAtRate s.included s.rule.shareBp (jsonLocalIncomeTax s.rateOn) ((stackLineInt? s.rateOn k).getD 0)

/-- 2.6.0: the whole charge (`.marginal`: `shareBp` of PIT with − PIT without; `.averageRate`: the included amount at
`shareBp` of the 1.x line's global rate, central and local parts each rounded down). -/
def coreTotal (s : StackSlice) : Int :=
  match s.rule.mode with
  | .marginal => stackShare s.rule.shareBp s.total
  | .averageRate k =>
    stackAtRate s.included s.rule.shareBp (jsonIncomeTax s.rateOn - jsonLocalIncomeTax s.rateOn)
      ((stackLineInt? s.rateOn k).getD 0) + s.coreLocal

/-- 2.7.0 (R4-18-3): the included amount at the elective flat rate (rounded down). -/
def flatDue (s : StackSlice) : Int := divR .down (pos s.included * pos s.rule.electFlatBp) BP

/-- 2.7.0: the flat rate is elected (the rule offers one and it is lower than the stacked charge). -/
def elects (s : StackSlice) : Bool := decide (0 ≤ s.rule.electFlatBp) && decide (s.flatDue < s.coreTotal)

/-- The local income tax part of the charge (0 when the flat rate is elected). -/
def dueLocal (s : StackSlice) : Int := if s.elects then 0 else s.coreLocal

/-- The whole charge: the stacked charge (`coreTotal`), or the flat-rate amount when that is lower and elective. -/
def dueTotal (s : StackSlice) : Int := if s.elects then s.flatDue else s.coreTotal

/-- The statute, naming the election when it is taken. -/
def statuteOf (s : StackSlice) : String :=
  if s.elects then s.rule.statute ++ s!"; elective flat rate {s.rule.electFlatBp} bp taken (lower than the stacked tax)"
  else s.rule.statute

/-- A priced slice: the central part (income tax and surtaxes), and the local income tax part when it is not 0. -/
def charges (s : StackSlice) : List Charge :=
  if s.ok && s.rated then
    charge .pit s.rule.name s.base (fun _ => s.included) (fun _ => s.dueTotal - s.dueLocal) (event := s.event)
      (statute := s.statuteOf)
    :: (if s.dueLocal = 0 then [] else
        [charge .pit (s.rule.name ++ " (local income tax)") s.base (fun _ => s.included) (fun _ => s.dueLocal)
          (event := s.event) (level := .local) (statute := s.rule.statute)])
  else []

def unknown (s : StackSlice) : List String :=
  if !s.ok then [s!"1100 {s.rule.name}: {s.why} (grade C)"]
  else if !s.rated then
    [s!"1100 {s.rule.name}: no global rate: the 1.x line with {s.included} added gives no usable {match s.rule.mode with | .averageRate k => k | .marginal => ""} (absent, or not positive while income tax is due) or a negative income tax (grade C)"]
  else []

theorem stackShare_default (x : Int) : stackShare BP x = x := by simp [stackShare]

theorem stackShare_nonneg (share x : Int) (h : 0 ≤ x) : 0 ≤ stackShare share x := by
  unfold stackShare; split
  · exact h
  · simp only [divR]; exact Int.ediv_nonneg (Int.mul_nonneg h (pos_nonneg _)) (by decide)

theorem stackShare_zero (share : Int) : stackShare share 0 = 0 := by
  unfold stackShare; split <;> simp [divR]

theorem stackAtRate_nonneg (x share tax taxable : Int) : 0 ≤ stackAtRate x share tax taxable := by
  unfold stackAtRate; split
  · exact Int.le_refl 0
  · simp only [divR]
    exact Int.ediv_nonneg (Int.mul_nonneg (Int.mul_nonneg (pos_nonneg _) (pos_nonneg _)) (pos_nonneg _))
      (Int.mul_nonneg (by omega) (by decide))

theorem stackAtRate_zero (share tax taxable : Int) : stackAtRate 0 share tax taxable = 0 := by
  unfold stackAtRate; split
  · rfl
  · simp [divR, pos]

/-- **The 2.5.0 charge**: a marginal rule with the whole share books PIT with − PIT without, central and local. -/
theorem due_default (s : StackSlice) (hm : s.rule.mode = .marginal) (hs : s.rule.shareBp = BP)
    (he : s.rule.electFlatBp < 0) :
    s.dueTotal = s.total ∧ s.dueLocal = s.localPart ∧ s.rated = true := by
  have hel : s.elects = false := by simp [elects]; omega
  simp [dueTotal, dueLocal, hel, coreTotal, coreLocal, rated, hm, hs, stackShare_default]

/-- 2.7.0: without an elective rate the charge is the 2.6.0 charge. -/
theorem due_noElect (s : StackSlice) (he : s.rule.electFlatBp < 0) : s.dueTotal = s.coreTotal ∧ s.dueLocal = s.coreLocal := by
  have hel : s.elects = false := by simp [elects]; omega
  simp [dueTotal, dueLocal, hel]

/-- 2.7.0: an elective flat rate never raises the charge. -/
theorem dueTotal_le_core (s : StackSlice) : s.dueTotal ≤ s.coreTotal := by
  unfold dueTotal
  split
  · rename_i h; simp only [elects, Bool.and_eq_true, decide_eq_true_eq] at h; omega
  · exact Int.le_refl _

/-- A marginal rule (whatever its share) books no less than 0 when PIT with ≥ PIT without. -/
theorem dueTotal_nonneg (s : StackSlice) (h : 0 ≤ s.total) : 0 ≤ s.dueTotal := by
  unfold dueTotal
  split
  · simp only [flatDue, divR]
    exact Int.ediv_nonneg (Int.mul_nonneg (pos_nonneg _) (pos_nonneg _)) (by decide)
  · unfold coreTotal
    split
    · exact stackShare_nonneg _ _ h
    · unfold coreLocal; rename_i k hk; simp only [hk]
      exact Int.add_nonneg (stackAtRate_nonneg _ _ _ _) (stackAtRate_nonneg _ _ _ _)

/-- Nothing included and the 1.x line unchanged: nothing due. -/
theorem dues_zero (s : StackSlice) (hi : s.included = 0) (ha : s.after = s.before) :
    s.dueTotal = 0 ∧ s.dueLocal = 0 := by
  have ht : s.total = 0 := by simp [total, ha]
  have hl : s.localPart = 0 := by simp [localPart, ha]
  have hf : s.flatDue = 0 := by simp [flatDue, hi, pos, divR]
  have hc : s.coreTotal = 0 ∧ s.coreLocal = 0 := by
    unfold coreTotal coreLocal
    split <;> simp [ht, hl, hi, stackShare_zero, stackAtRate_zero]
  unfold dueTotal dueLocal
  split <;> simp [hf, hc.1, hc.2]

/-- **A priced rule's charges add up to its due** (`dueTotal`; for a 2.5.0 rule PIT(with) − PIT(without),
`due_default`). -/
theorem charges_sum (s : StackSlice) (h : s.ok = true) (hr : s.rated = true) :
    isum (s.charges.map (·.due)) = s.dueTotal := by
  unfold charges
  simp only [h, hr, Bool.and_self, ↓reduceIte]
  have h0 : pos 0 = 0 := rfl
  have h1 := pos_nonneg (s.dueTotal - s.dueLocal)
  have h2 := pos_nonneg s.dueLocal
  split <;> simp [charge, appliedCredit, isum, h0] <;> omega

theorem charges_notOk (s : StackSlice) (h : s.ok = false) : s.charges = [] := by simp [charges, h]

theorem charges_notRated (s : StackSlice) (h : s.rated = false) : s.charges = [] := by simp [charges, h]

end StackSlice

/-- The slices of `rules` on household `c` whose 1.x line is `j` (`ok`: the earlier slices were priced). A rule without
items is skipped (no 1.x call); a rule whose amounts are all 0 is a priced 0 (no 1.x call). -/
def stackSlices (pit : Canon → Json) (g : CanonGlobal) : List StackRule → Canon → Json → Bool → List StackSlice
  | [], _, _, _ => []
  | r :: rs, c, j, ok =>
    if (r.wItems g).isEmpty && (r.undated g).isEmpty then stackSlices pit g rs c j ok else
    let xs := r.amounts c.adults.length g
    let inc := isum (xs.map (·.2))
    let bad (why : String) : StackSlice :=
      { rule := r, base := r.base g, included := inc, before := j, after := j, event := r.eventOf g, ok := false, why }
    if !ok then bad "stacked on an earlier rule that was not priced" :: stackSlices pit g rs c j false
    else match r.undated g with
    | it :: _ => bad s!"{it.2.2} has no date (the rule takes items {r.windowText})" :: stackSlices pit g rs c j false
    | [] =>
    match r.unplaced c.adults.length g with
    | it :: _ =>
      bad s!"{it.2.2} is of person {it.1}, who is not an adult of the household (not stacked)"
        :: stackSlices pit g rs c j false
    | [] =>
      if xs.all (·.2 == 0) then
        { rule := r, base := r.base g, included := 0, before := j, after := j, event := r.eventOf g, ok := true }
          :: stackSlices pit g rs c j true
      else
        let c' := r.into.addAll c xs
        let j' := pit c'
        if stackErrorLine j' then
          bad s!"the 1.x model answers with an error on the household with {inc} added to {r.into.name}"
            :: stackSlices pit g rs c j false
        else if !stackRawAgrees c' && j' == j then
          bad s!"included amount {inc} did not reach the 1.x model (the household's input line cannot carry it)"
            :: stackSlices pit g rs c j false
        else
          { rule := r, base := r.base g, included := inc, before := j, after := j', event := r.eventOf g, ok := true }
            :: stackSlices pit g rs c' j' true

/-- **The shape of every slice**: it belongs to a rule of the list, and its 1.x lines are those of a household `c₀`
(the household with the earlier rules' amounts) and either the same line (not priced, or nothing included) or the line
of `c₀` plus the rule's amounts, `included` being their sum (2.6.0 added what `included` is). -/
theorem stackSlices_shape (pit : Canon → Json) (g : CanonGlobal) (rules : List StackRule) :
    ∀ (c : Canon) (ok : Bool) (s : StackSlice), s ∈ stackSlices pit g rules c (pit c) ok →
      s.rule ∈ rules ∧ ∃ c₀ : Canon, c₀.adults.length = c.adults.length ∧ s.before = pit c₀ ∧
        ((s.after = s.before ∧ (s.ok = false ∨ s.included = 0))
          ∨ (s.after = pit (s.rule.into.addAll c₀ (s.rule.amounts c₀.adults.length g))
              ∧ s.included = isum ((s.rule.amounts c₀.adults.length g).map (·.2)))) := by
  induction rules with
  | nil => intro c ok s hs; simp [stackSlices] at hs
  | cons r rs ih =>
    intro c ok s hs
    have tail : ∀ (c' : Canon) ok', c'.adults.length = c.adults.length → s ∈ stackSlices pit g rs c' (pit c') ok' →
        s.rule ∈ r :: rs ∧ ∃ c₀ : Canon, c₀.adults.length = c.adults.length ∧ s.before = pit c₀ ∧
          ((s.after = s.before ∧ (s.ok = false ∨ s.included = 0))
            ∨ (s.after = pit (s.rule.into.addAll c₀ (s.rule.amounts c₀.adults.length g))
                ∧ s.included = isum ((s.rule.amounts c₀.adults.length g).map (·.2)))) := by
      intro c' ok' hl h
      obtain ⟨hm, c₀, h1, h2⟩ := ih c' ok' s h
      exact ⟨List.mem_cons_of_mem _ hm, c₀, h1.trans hl, h2⟩
    simp only [stackSlices] at hs
    split at hs
    · exact tail c ok rfl hs
    · split at hs
      · rcases List.mem_cons.mp hs with h | h
        · subst h; exact ⟨List.mem_cons_self .., c, rfl, rfl, Or.inl ⟨rfl, Or.inl rfl⟩⟩
        · exact tail c false rfl h
      · split at hs
        · rcases List.mem_cons.mp hs with h | h
          · subst h; exact ⟨List.mem_cons_self .., c, rfl, rfl, Or.inl ⟨rfl, Or.inl rfl⟩⟩
          · exact tail c false rfl h
        · split at hs
          · rcases List.mem_cons.mp hs with h | h
            · subst h; exact ⟨List.mem_cons_self .., c, rfl, rfl, Or.inl ⟨rfl, Or.inl rfl⟩⟩
            · exact tail c false rfl h
          · split at hs
            · rcases List.mem_cons.mp hs with h | h
              · subst h; exact ⟨List.mem_cons_self .., c, rfl, rfl, Or.inl ⟨rfl, Or.inr rfl⟩⟩
              · exact tail c true rfl h
            · split at hs
              · rcases List.mem_cons.mp hs with h | h
                · subst h; exact ⟨List.mem_cons_self .., c, rfl, rfl, Or.inl ⟨rfl, Or.inl rfl⟩⟩
                · exact tail c false rfl h
              · split at hs
                · rcases List.mem_cons.mp hs with h | h
                  · subst h; exact ⟨List.mem_cons_self .., c, rfl, rfl, Or.inl ⟨rfl, Or.inl rfl⟩⟩
                  · exact tail c false rfl h
                · rcases List.mem_cons.mp hs with h | h
                  · subst h; exact ⟨List.mem_cons_self .., c, rfl, rfl, Or.inr ⟨rfl, rfl⟩⟩
                  · exact tail _ true (StackField.addAll_length _ _ _) h

/-- 2.7.0: the slices with `rateFromStack` read their global rate from the whole stack's 1.x line (the last priced
slice's `after`, which carries every rule's amount); if a slice of the stack is not priced, they are not either. -/
def shareStackRate (ss : List StackSlice) : List StackSlice :=
  if !(ss.any fun s => s.rule.rateFromStack) then ss else
  let allOk := ss.all (·.ok)
  let top := (ss.filter (·.ok)).getLast?.map (·.after)
  ss.map fun s =>
    if s.rule.rateFromStack && s.ok then
      (if allOk then { s with rateLine := top }
       else { s with ok := false, why := "the global rate of the whole stack needs every rule of the stack priced" })
    else s

/-- Without `rateFromStack` the slices are unchanged. -/
theorem shareStackRate_none (ss : List StackSlice) (h : ∀ s ∈ ss, s.rule.rateFromStack = false) :
    shareStackRate ss = ss := by
  have : (ss.any fun s => s.rule.rateFromStack) = false := by
    simp only [List.any_eq_false]; intro s hs; simp [h s hs]
  simp [shareStackRate, this]

/-- A shared-rate slice is a slice of the stack with only its rate line (or its `ok`) changed. -/
theorem shareStackRate_mem (ss : List StackSlice) (s : StackSlice) (hs : s ∈ shareStackRate ss) :
    ∃ s0 ∈ ss, s.rule = s0.rule ∧ s.before = s0.before ∧ s.after = s0.after ∧ s.included = s0.included
      ∧ (s.ok = true → s0.ok = true) := by
  unfold shareStackRate at hs
  split at hs
  · exact ⟨s, hs, rfl, rfl, rfl, rfl, id⟩
  · obtain ⟨s0, h0, rfl⟩ := List.mem_map.mp hs
    refine ⟨s0, h0, ?_⟩
    split
    · split <;> simp_all
    · exact ⟨rfl, rfl, rfl, rfl, id⟩

/-! ## The family -/

/-- The stacked charges of an entity (none for a company entity, or when no rule has an item: no extra 1.x call). -/
def stackCharges (pit : List String → Canon → Json) (route : CanonGlobal → Canon) (rules : List StackRule)
    (args : List String) (g : CanonGlobal) : List Charge :=
  if g.entity == .company || rules.all (fun r => (r.items g).isEmpty) then [] else
  (shareStackRate (stackSlices (pit args) g rules (route g) (pit args (route g)) true)).flatMap (·.charges)

/-- The rules not priced, as grade-C lines for `unsupported`. -/
def stackUnknown (pit : List String → Canon → Json) (route : CanonGlobal → Canon) (rules : List StackRule)
    (args : List String) (g : CanonGlobal) : List String :=
  if g.entity == .company || rules.all (fun r => (r.items g).isEmpty) then [] else
  (shareStackRate (stackSlices (pit args) g rules (route g) (pit args (route g)) true)).flatMap (·.unknown)

/-- The stacking as a family (1100 is already covered by the PIT line). -/
def stackRuleFamily (pit : List String → Canon → Json) (route : CanonGlobal → Canon) (rules : List StackRule)
    (name : String := "1100 income stacked on the 1.x income tax") : Family :=
  { name, covers := [], run := fun args g _ => stackCharges pit route rules args g }

/-- **Stacking on a model**: the family last, and the grade-C lines after the model's own `unsupported`. -/
def GlobalModel.withStack (m : GlobalModel) (rules : List StackRule)
    (name : String := "1100 income stacked on the 1.x income tax") : GlobalModel :=
  { m with families := m.families ++ [stackRuleFamily m.pit m.route rules name],
           unsupported := fun args g => m.unsupported args g ++ stackUnknown m.pit m.route rules args g }

/-- The assumption of `stackCharges_nonneg`: the 1.x income tax does not fall when field `f` rises. -/
def StackMono (pit : Canon → Json) (f : StackField) : Prop :=
  ∀ (c : Canon) (i : Nat) (d : Int), 0 ≤ d → jsonIncomeTax (pit c) ≤ jsonIncomeTax (pit (f.addTo c i d))

theorem StackMono.addAll {pit : Canon → Json} {f : StackField} (hm : StackMono pit f) :
    ∀ (c : Canon) (xs : List (Nat × Int)), (∀ x ∈ xs, 0 ≤ x.2) →
      jsonIncomeTax (pit c) ≤ jsonIncomeTax (pit (f.addAll c xs))
  | _, [], _ => Int.le_refl _
  | c, x :: xs, h => by
    simp only [StackField.addAll, List.foldl_cons]
    exact Int.le_trans (hm c x.1 x.2 (h x (by simp)))
      (StackMono.addAll hm _ xs (fun y hy => h y (by simp [hy])))

theorem isum_flatMap_due {α : Type} (l : List α) (f : α → List Charge) :
    isum ((l.flatMap f).map (·.due)) = isum (l.map fun a => isum ((f a).map (·.due))) := by
  induction l with
  | nil => rfl
  | cons a l ih => simp [List.flatMap_cons, isum_append, isum, ih]

theorem stack_isum_zero (l : List (Nat × Int)) (h : ∀ x ∈ l, x.2 = 0) : isum (l.map (·.2)) = 0 := by
  induction l with
  | nil => rfl
  | cons a l ih =>
    simp only [List.map_cons, isum]
    rw [h a (by simp), ih (fun x hx => h x (by simp [hx]))]
    rfl

/-- **The stacked charge is never negative when the 1.x income tax does not fall as the stacked field rises**
(`StackMono`, an assumption on the country's 1.x model; and inclusion rates ≥ 0). -/
theorem stackCharges_nonneg (pit : List String → Canon → Json) (route : CanonGlobal → Canon) (rules : List StackRule)
    (args : List String) (g : CanonGlobal) (hm : ∀ r ∈ rules, StackMono (pit args) r.into)
    (hi : ∀ r ∈ rules, 0 ≤ r.inclusionBp) : 0 ≤ isum ((stackCharges pit route rules args g).map (·.due)) := by
  unfold stackCharges
  split
  · simp [isum]
  · rw [isum_flatMap_due]
    apply isum_nonneg
    intro y hy
    obtain ⟨s, hs, rfl⟩ := List.mem_map.mp hy
    by_cases hok : s.ok = true
    · by_cases hrt : s.rated = true
      · rw [StackSlice.charges_sum s hok hrt]
        apply StackSlice.dueTotal_nonneg
        obtain ⟨s0, hs0, -, hbef, haft, -, -⟩ := shareStackRate_mem _ s hs
        obtain ⟨hr, c₀, -, hb, ha⟩ := stackSlices_shape (pit args) g rules (route g) true s0 hs0
        unfold StackSlice.total
        rw [hbef, haft]
        rcases ha with ⟨ha, -⟩ | ⟨ha, -⟩
        · rw [ha]; omega
        · rw [ha, hb]
          have := (hm s0.rule hr).addAll c₀ (s0.rule.amounts c₀.adults.length g)
            (StackRule.amounts_nonneg s0.rule (hi s0.rule hr) c₀.adults.length g)
          omega
      · simp at hrt
        simp [StackSlice.charges_notRated s hrt, isum]
    · simp at hok
      simp [StackSlice.charges_notOk s hok, isum]

/-- **An included amount of 0 gives a stacked charge of 0** (every charge booked is 0). -/
theorem stackCharges_zero (pit : List String → Canon → Json) (route : CanonGlobal → Canon) (rules : List StackRule)
    (args : List String) (g : CanonGlobal)
    (h : ∀ r ∈ rules, ∀ x ∈ r.amounts (route g).adults.length g, x.2 = 0) :
    ∀ ch ∈ stackCharges pit route rules args g, ch.due = 0 := by
  intro ch hch
  unfold stackCharges at hch
  split at hch
  · simp at hch
  · obtain ⟨s, hs, hc⟩ := List.mem_flatMap.mp hch
    obtain ⟨s0, hs0, -, hbef, haft, hinc, hok0⟩ := shareStackRate_mem _ s hs
    obtain ⟨hr, c₀, hl, hb, ha⟩ := stackSlices_shape (pit args) g rules (route g) true s0 hs0
    have hz : ∀ x ∈ s0.rule.amounts c₀.adults.length g, x.2 = 0 := by rw [hl]; exact h s0.rule hr
    have hok : s.ok = true := by
      cases hk : s.ok
      · simp [StackSlice.charges_notOk s hk] at hc
      · rfl
    have hok' : s0.ok = true := hok0 hok
    have hboth : s0.after = s0.before ∧ s0.included = 0 := by
      rcases ha with ⟨ha, hi⟩ | ⟨ha, hi⟩
      · refine ⟨ha, ?_⟩
        rcases hi with hi | hi
        · simp [hok'] at hi
        · exact hi
      · refine ⟨by rw [ha, hb, StackField.addAll_zero _ _ _ hz], ?_⟩
        rw [hi]
        exact stack_isum_zero _ hz
    obtain ⟨hdt, hdl⟩ := StackSlice.dues_zero s (by rw [hinc]; exact hboth.2) (by rw [haft, hbef]; exact hboth.1)
    unfold StackSlice.charges at hc
    rw [hdt, hdl] at hc
    split at hc
    · simp at hc
      subst hc
      have h0 : pos 0 = 0 := rfl
      simp [charge, appliedCredit, h0]
    · simp at hc

/-- An entity with no item for any rule gets no stacked charge and no grade-C line. -/
theorem stackCharges_noItems (pit : List String → Canon → Json) (route : CanonGlobal → Canon) (rules : List StackRule)
    (args : List String) (g : CanonGlobal) (h : ∀ r ∈ rules, r.items g = []) :
    stackCharges pit route rules args g = [] ∧ stackUnknown pit route rules args g = [] := by
  have hall : rules.all (fun r => (r.items g).isEmpty) = true := by
    simp only [List.all_eq_true]; intro r hr; simp [h r hr]
  simp [stackCharges, stackUnknown, hall]

/-! ## The model: the 1.x line is unchanged -/

/-- **Stacking never changes the 1.x line** (`rfl`). -/
theorem withStack_pit (m : GlobalModel) (rules : List StackRule) (n : String) (args : List String) (g : CanonGlobal) :
    ((m.withStack rules n).computeGlobal args g).pit = (m.computeGlobal args g).pit := rfl

/-- The model's charges are those before, then the stacked ones. -/
theorem withStack_rawCharges (m : GlobalModel) (rules : List StackRule) (n : String) (args : List String)
    (g : CanonGlobal) :
    (m.withStack rules n).rawCharges args g = m.rawCharges args g ++ stackCharges m.pit m.route rules args g := by
  simp [GlobalModel.rawCharges, GlobalModel.withStack, runFamilies_append, GlobalModel.pitChargesFor, stackRuleFamily]

/-- **An entity without stacked items gets exactly the output of the model without stacking.** -/
theorem withStack_noItems (m : GlobalModel) (rules : List StackRule) (n : String) (args : List String)
    (g : CanonGlobal) (h : ∀ r ∈ rules, r.items g = []) :
    (m.withStack rules n).computeGlobal args g = m.computeGlobal args g := by
  obtain ⟨h1, h2⟩ := stackCharges_noItems m.pit m.route rules args g h
  simp [GlobalModel.computeGlobal, GlobalModel.withStack, runFamilies_append, GlobalModel.pitChargesFor,
    stackRuleFamily, h1, h2]

/-- Every 1.x household (in particular every line of the 1.x grid read in global mode) is unchanged. -/
theorem withStack_ofCanon (m : GlobalModel) (rules : List StackRule) (n : String) (args : List String) (c : Canon) :
    (m.withStack rules n).computeGlobal args (CanonGlobal.ofCanon c) = m.computeGlobal args (CanonGlobal.ofCanon c) :=
  withStack_noItems m rules n args _ (fun r _ => StackRule.items_ofCanon r c)

end TaxKernel.Global
