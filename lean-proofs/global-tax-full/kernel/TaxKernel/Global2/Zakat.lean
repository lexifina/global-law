import TaxKernel.Global2.Employer
import TaxKernel.Global2.GoodsValue

/-!
# TaxKernel.Global2.Zakat (2.9.0, 2026-11-21): zakat by the payer's faith and the owners of a company (R3-GAP-1)

Zakat (MV, MY, PK, AF, BN, LY, SD, YE; SA and QA companies) is due from Muslims, and from a company on the share of it its
Muslim owners hold; the canonical input said neither, so every zakat row was grade C. The kernel adds the facts and the
part; it never presumes a faith: a model that wants a presumption declares it, with its source.

**Adult facts** (optional, on each `household.adults` record; `zakatOf g i`):

| JSON field | meaning |
|---|---|
| `"zakatLiable"` | `true` / `false`: the adult is (not) liable to zakat (wins over the others) |
| `"religion"` | `"muslim"` / `"islam"` (any case): liable; any other text: not liable |
| `"zakatExemptDeclared"` | `true`: a declaration of exemption is filed (PK Zakat and Ushr Ordinance 1980 s. 2 (a): CZ-50); exempts a Muslim when the rule allows it (`exemptByDeclaration`) |
| `"zakatableWealth"` | the adult's own zakatable figure, money (wins over the assets: `adultField`) |

**Company facts** (on the `company` record): `"muslimOwnershipBp"` (0-10 000, the Muslim-held share), `"zakatLiable"`
(`true` = 10 000, `false` = 0), `"zakatBase"` (the zakatable base the statute defines, money).

**The rule** (`ZakatRule`): `rateBp` (250 = 2.5 %) on a base above a **nisab** (`nisab`, money, with `nisabSource`: the
nisab follows the price of gold or silver, the model declares it), on the whole base (`onExcess := false`, the classical
rule) or the excess; per adult: `base := .wealth kinds` (the adult's assets of these kinds, `person` = the adult, value
less debt; PK: `[.deposits]`), `.income kinds` (wages + the adult's income items of these kinds, less `allowance`: MY zakat
on income), `.field k` (an adult record field); per company (`companies := some { … }`): the base (`.field "zakatBase"`,
`.netAssets` = `assets − debt`, `.equity`, `.profit`) × the Muslim-held share. **What an absent fact means is declared**:
`presume := none` (default) → grade C (`"6000 zakat: adult 1: religion not given … (grade C)"`); `some true/false` →
liable / not liable, the statute ending `"; presumed …: <presumeNote>"`; the company's `presumeShareBp` the same (−1:
grade C). A liable adult below the nisab books a 0 charge (computed, not missing); a non-liable adult books none.

Charges under `oecd` (`.other` = 6000 by default; MV books zakat al-mal under 4210, `.wealth`), event `"adult <i>"` or
`"year"` (company), bearer entity. `GlobalModel.withZakat m [r]`.

Theorems: `zakatFacts_null`, `ZakatStatus.ofFacts_explicit`, `ZakatStatus.ofFacts_unknown`, `zakatDue_belowNisab`,
`zakatDue_nonneg`, `zakatDue_mono`, `companyShare_explicit`, `ZakatRule.statusOf_unknown`, `withZakat_pit`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-! ## Facts -/

/-- What a record says about zakat. -/
structure ZakatFacts where
  /-- `"zakatLiable"` -/
  liable : Option Bool := none
  /-- `"religion"`, lower case (`""`: not given) -/
  religion : String := ""
  /-- `"zakatExemptDeclared"` -/
  exemptDeclared : Bool := false
  deriving Repr, Inhabited, BEq

/-- The text without white space. -/
def squash (s : String) : String := String.ofList (s.toList.filter fun c => !c.isWhitespace)

/-- A string field mapped by `f` (`""`: absent, or not a string). -/
def textField (j : Json) (k : String) (f : String → String) : String :=
  match j.getObjVal? k with
  | .ok (.str s) => f s
  | _ => ""

def jsonBool? (j : Json) (k : String) : Option Bool :=
  match j.getObjVal? k with
  | .ok (.bool b) => some b
  | _ => none

def ZakatFacts.ofJson (j : Json) : ZakatFacts :=
  { liable := jsonBool? j "zakatLiable", religion := textField j "religion" (fun s => (squash s).toLower),
    exemptDeclared := (jsonBool? j "zakatExemptDeclared").getD false }

/-- Adult `i`'s zakat facts. -/
def zakatOf (g : CanonGlobal) (i : Nat) : ZakatFacts := ZakatFacts.ofJson (adultJson g i)

theorem zakatFacts_null : ZakatFacts.ofJson Json.null = {} := by
  rfl

inductive ZakatStatus where
  | liable
  /-- not a Muslim, or `"zakatLiable": false` -/
  | notLiable
  /-- a Muslim with a declaration of exemption -/
  | exempt
  | unknown
  deriving Repr, DecidableEq, Inhabited, BEq

def isMuslim (religion : String) : Bool := religion == "muslim" || religion == "islam"

/-- The status from the facts: `"zakatLiable"` first, then `"religion"` (and a declaration of exemption). -/
def ZakatStatus.ofFacts (f : ZakatFacts) (exemptByDeclaration : Bool) : ZakatStatus :=
  match f.liable with
  | some true => .liable
  | some false => .notLiable
  | none =>
    if f.religion == "" then .unknown
    else if isMuslim f.religion then (if exemptByDeclaration && f.exemptDeclared then .exempt else .liable)
    else .notLiable

theorem ZakatStatus.ofFacts_explicit (f : ZakatFacts) (e b : Bool) (h : f.liable = some b) :
    ZakatStatus.ofFacts f e = if b then .liable else .notLiable := by
  cases b <;> simp [ofFacts, h]

/-- **Never presumed by the kernel**: no fact given, the status is unknown. -/
theorem ZakatStatus.ofFacts_unknown (e : Bool) : ZakatStatus.ofFacts {} e = .unknown := by
  simp [ofFacts]

/-! ## The due -/

/-- `rate` on the base above the nisab: nothing below it; the whole base (`onExcess = false`) or the excess. -/
def zakatDue (rateBp nisab : Int) (onExcess : Bool) (base : Int) : Int :=
  if base < nisab || base ≤ 0 then 0
  else divR .down (rateBp * (if onExcess then base - nisab else base)) BP

theorem zakatDue_belowNisab (r n : Int) (e : Bool) (b : Int) (h : b < n) : zakatDue r n e b = 0 := by
  simp [zakatDue, h]

theorem zakatDue_nonneg (r n : Int) (e : Bool) (b : Int) (hr : 0 ≤ r) : 0 ≤ zakatDue r n e b := by
  unfold zakatDue
  split
  · exact Int.le_refl 0
  · rename_i h
    simp only [Bool.or_eq_true, decide_eq_true_eq, not_or] at h
    simp only [divR, BP]
    apply Int.ediv_nonneg _ (by omega)
    apply Int.mul_nonneg hr
    split <;> omega

/-- **A larger base never owes less** (above the nisab, whole-base rule). -/
theorem zakatDue_mono (r n : Int) (b₁ b₂ : Int) (hr : 0 ≤ r) (hn : 0 ≤ n) (h₁ : n ≤ b₁) (h0 : 0 < b₁)
    (h : b₁ ≤ b₂) : zakatDue r n false b₁ ≤ zakatDue r n false b₂ := by
  have n1 : ¬ (b₁ < n) := by omega
  have n2 : ¬ (b₂ < n) := by omega
  have p1 : ¬ (b₁ ≤ 0) := by omega
  have p2 : ¬ (b₂ ≤ 0) := by omega
  simp only [zakatDue, n1, n2, p1, p2, decide_false, Bool.or_false, Bool.false_eq_true, ite_false]
  simp only [divR, BP]
  exact Int.ediv_le_ediv (by omega) (Int.mul_le_mul_of_nonneg_left h hr)

/-! ## The rule -/

inductive ZakatBase where
  /-- the adult's assets of these kinds (owner = the adult's `person` index), value less debt -/
  | wealth (kinds : List AssetKind)
  /-- the adult's wages and income items of these kinds -/
  | income (kinds : List IncomeKind)
  /-- a number on the adult's record -/
  | field (key : String)
  deriving Inhabited

inductive ZakatCompanyBase where
  /-- a number on the company record (`"zakatBase"`) -/
  | field (key : String)
  /-- `company.assets − company.debt` -/
  | netAssets
  | equity
  | profit
  deriving Inhabited

structure ZakatCompany where
  base : ZakatCompanyBase := .field "zakatBase"
  /-- the Muslim-held share when the company record gives none (−1: grade C) -/
  presumeShareBp : Int := -1
  presumeNote : String := ""
  /-- the nisab applies to companies too -/
  nisab : Bool := false
  deriving Inhabited

structure ZakatRule where
  name : String := "zakat"
  rateBp : Int := 250
  /-- money; the model declares it (`nisabSource`: the gold or silver price and its date) -/
  nisab : Int := 0
  nisabSource : String := ""
  onExcess : Bool := false
  /-- adults (`none`: households pay none under this rule) -/
  adults : Option ZakatBase := some (.wealth [.deposits, .listedShares, .unlistedShares, .bonds, .business, .other])
  /-- an adult record field that, when given, is the adult's base (`""`: none) -/
  adultField : String := "zakatableWealth"
  /-- deducted from an adult's base before the nisab (MY hadd kifayah on income) -/
  allowance : Int := 0
  /-- a Muslim with `"zakatExemptDeclared": true` is exempt -/
  exemptByDeclaration : Bool := false
  /-- the model's declared presumption for an adult without facts (`none`: grade C) -/
  presume : Option Bool := none
  presumeNote : String := ""
  companies : Option ZakatCompany := none
  oecd : Oecd := .other
  level : Level := .central
  statute : String := ""
  deriving Inhabited

/-- The company record of the line (`null`: none). -/
def companyJson (g : CanonGlobal) : Json := match g.raw.getObjVal? "company" with | .ok c => c | .error _ => Json.null

/-- The company's Muslim-held share: `"muslimOwnershipBp"` (clamped to 0-10 000), else `"zakatLiable"`, else `none`. -/
def companyMuslimShare? (g : CanonGlobal) : Option Int :=
  let j := companyJson g
  match j.getObjVal? "muslimOwnershipBp" with
  | .ok (.num _) => some (max 0 (min BP (intField j "muslimOwnershipBp")))
  | _ => match jsonBool? j "zakatLiable" with
    | some true => some BP
    | some false => some 0
    | none => none

theorem companyShare_explicit (g : CanonGlobal) (b : Bool) (hm : (companyJson g).getObjVal? "muslimOwnershipBp" = .error "")
    (hl : jsonBool? (companyJson g) "zakatLiable" = some b) : companyMuslimShare? g = some (if b then BP else 0) := by
  cases b <;> simp [companyMuslimShare?, hm, hl]

namespace ZakatRule

/-- Adult `i`'s base: the record's own figure (`adultField`), else the base the rule reads, less the allowance;
`none`: a `.field` base the record does not give. -/
def adultBase (r : ZakatRule) (g : CanonGlobal) (i : Nat) (b : ZakatBase) : Option Int :=
  let j := adultJson g i
  let own := if r.adultField == "" then -1 else nonnegField j r.adultField
  let raw : Option Int :=
    if 0 ≤ own then some own else
    match b with
    | .wealth ks => some (isum ((g.assets.filter fun a => a.person == i && ks.contains a.kind).map fun a => a.value - a.debt))
    | .income ks =>
      some ((g.household.adults.getD i {}).wages
        + isum ((g.incomes.filter fun x => x.person == i && ks.contains x.kind).map (·.amount)))
    | .field k => let v := nonnegField j k; if 0 ≤ v then some v else none
  raw.map fun v => pos (v - r.allowance)

/-- The status of adult `i` and the note when it is presumed. -/
def statusOf (r : ZakatRule) (g : CanonGlobal) (i : Nat) : ZakatStatus × String :=
  match ZakatStatus.ofFacts (zakatOf g i) r.exemptByDeclaration with
  | .unknown =>
    match r.presume with
    | some true => (.liable, s!"presumed liable (the model's declared presumption: {r.presumeNote})")
    | some false => (.notLiable, "")
    | none => (.unknown, "")
  | s => (s, "")

def statute' (r : ZakatRule) (parts : List String) : String := "; ".intercalate ((r.statute :: parts).filter (· != ""))

def nisabNote (r : ZakatRule) : String :=
  if r.nisab ≤ 0 then "" else s!"nisab {r.nisab}" ++ (if r.nisabSource == "" then "" else s!" ({r.nisabSource})")

/-- Household charges: one per liable adult (0 below the nisab). -/
def adultCharges (r : ZakatRule) (g : CanonGlobal) : List Charge :=
  match r.adults with
  | none => []
  | some b =>
    if g.entity != .household then [] else
    (List.range g.household.adults.length).filterMap fun i =>
      match r.statusOf g i with
      | (.liable, note) =>
        match r.adultBase g i b with
        | some v =>
          some (charge r.oecd r.name v (fun x => if x < r.nisab then 0 else x) (fun _ => zakatDue r.rateBp r.nisab r.onExcess v)
            (event := s!"adult {i + 1}") (level := r.level)
            (statute := r.statute' [r.nisabNote, if v < r.nisab then "below the nisab" else "", note]))
        | none => none
      | _ => none

/-- The company's charge: the base × the Muslim-held share. -/
def companyCharges (r : ZakatRule) (g : CanonGlobal) : List Charge :=
  match r.companies with
  | none => []
  | some zc =>
    if g.entity != .company then [] else
    let base : Option Int := match zc.base with
      | .field k => let v := nonnegField (companyJson g) k; if 0 ≤ v then some v else none
      | .netAssets => some (g.company.assets - g.company.debt)
      | .equity => some g.company.equity
      | .profit => some g.company.profit
    let share : Option (Int × String) := match companyMuslimShare? g with
      | some s => some (s, "")
      | none => if 0 ≤ zc.presumeShareBp then
          some (min BP zc.presumeShareBp, s!"Muslim-held share presumed {zc.presumeShareBp} bp (the model's declared presumption: {zc.presumeNote})")
        else none
    match base, share with
    | some v, some (sh, note) =>
      let part := divR .down (pos v * sh) BP
      let n := if zc.nisab then r.nisab else 0
      [charge r.oecd r.name v (fun _ => part) (fun _ => zakatDue r.rateBp n r.onExcess part) (level := r.level)
        (statute := r.statute' [s!"Muslim-held share {sh} bp", if zc.nisab then r.nisabNote else "", note])]
    | _, _ => []

def charges (r : ZakatRule) (g : CanonGlobal) : List Charge := r.adultCharges g ++ r.companyCharges g

/-- What the rule cannot compute (grade C). -/
def unknown (r : ZakatRule) (g : CanonGlobal) : List String :=
  let pre := s!"{r.oecd.code} {r.name}"
  let adults : List String := match r.adults with
    | none => []
    | some b =>
      if g.entity != .household then [] else
      (List.range g.household.adults.length).filterMap fun i =>
        match r.statusOf g i with
        | (.unknown, _) =>
          some s!"{pre}: adult {i + 1}: religion not given (\"zakatLiable\" or \"religion\"; the rule presumes nothing) (grade C)"
        | (.liable, _) =>
          match r.adultBase g i b with
          | some _ => none
          | none => some s!"{pre}: adult {i + 1}: the zakatable base not given (grade C)"
        | _ => none
  let co : List String := match r.companies with
    | none => []
    | some zc =>
      if g.entity != .company then [] else
      let noBase := match zc.base with
        | .field k => decide (nonnegField (companyJson g) k < 0)
        | _ => false
      let noShare := (companyMuslimShare? g).isNone && zc.presumeShareBp < 0
      (if noShare then [s!"{pre}: year: the Muslim-held share not given (\"muslimOwnershipBp\" or \"zakatLiable\" on the company) (grade C)"] else [])
        ++ (if noBase then [s!"{pre}: year: the zakatable base not given (company \"{match zc.base with | .field k => k | _ => ""}\") (grade C)"] else [])
  adults ++ co

def family (r : ZakatRule) : Family :=
  { name := s!"{r.oecd.code} {r.name}", covers := [r.oecd], run := fun _ g _ => r.charges g }

/-- An adult whose faith is not given (and no presumption) gets no charge. -/
theorem statusOf_unknown (r : ZakatRule) (g : CanonGlobal) (i : Nat) (h : ZakatStatus.ofFacts (zakatOf g i) r.exemptByDeclaration = .unknown)
    (hp : r.presume = none) : (r.statusOf g i).1 = .unknown := by
  simp [statusOf, h, hp]

end ZakatRule

/-- **Zakat on a model**: the families last, the grade-C lines after the model's own `unsupported`. -/
def GlobalModel.withZakat (m : GlobalModel) (rs : List ZakatRule) : GlobalModel :=
  { m with families := m.families ++ rs.map (·.family),
           unsupported := fun args g => m.unsupported args g ++ rs.flatMap (·.unknown g) }

theorem withZakat_pit (m : GlobalModel) (rs : List ZakatRule) (args : List String) (g : CanonGlobal) :
    ((m.withZakat rs).computeGlobal args g).pit = (m.computeGlobal args g).pit := rfl

end TaxKernel.Global
