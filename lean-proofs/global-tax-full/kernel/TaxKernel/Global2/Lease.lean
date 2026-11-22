import TaxKernel.Global2.Zakat

/-!
# TaxKernel.Global2.Lease (2.9.0, 2026-11-21): the tenant's nationality and residence on a lease

Some levies on rent depend on who the tenant is: Bahrain's municipal fee is 10 % of the rent of property let to
non-Bahrainis (Legislative Decree 13/1979 and its orders; PwC 2025: "paid by the owner"); others exempt or surcharge
non-resident or company tenants. The canonical input has an asset's `annualValue` and a household's `rent` basket line, but
not the tenant.

**The input** (all optional):

| where | JSON | meaning |
|---|---|---|
| an asset record (the entity lets it) | `"lessee": {"nationality": "BH", "national": true, "resident": true, "kind": "individual" \| "company"}` | the tenant (any field may be left out) |
| an asset record | `"tenantNationality"`, `"tenantNational"`, `"tenantResident"` | the same, flat (when there is no `"lessee"` record) |
| an asset record | `"rent"` | the annual rent received, money (else `"annualValue"`) |
| a `rent` basket line (the household is the tenant) | the same `"lessee"` / flat fields | the tenant, else the household's first adult |
| `household.adults[i]` | `"nationality"`, `"national"`, `"resident"` | the adult's nationality (ISO) and residence |

`lesseeOfAsset g i`, `tenantOfLine g j`, `adultNationality g i` read them. "National" is `"national"` when given, else the
nationality compared with the levy's `country`.

**The levy** (`RentLevy`): `rateBp` of the rent, on the landlord's let assets (`side := .landlord`, assets of `kinds` that
carry a lessee, a `"rent"` or `"let": true`) or on the household's rent lines (`side := .tenant`), when every lessee
test holds (`LesseeTest`: `.national`, `.nonNational`, `.resident`, `.nonResident`, `.nationalities l`, `.company`,
`.individual`). **What an absent fact means is declared, with no default** (`ifUnknown : StateUnknown`, as `EmployerLevy`):
`.general` (not applied; `notes` says so), `.presume` (applied; the statute says so), `.gradeC` (no charge; grade C). A let
asset with no rent and no annual value: grade C. One charge per item: base = relieved = the rent, due = rate × rent,
event `"asset <i>"` / `"line <i> (rent)"`, heading `oecd` (4100, local, by default), `bearer`.
`GlobalModel.withRentLevies m [l]`.

Theorems: `lesseeFacts_null`, `LesseeFacts.national?_explicit`, `LesseeTest.eval_none`, `RentLevy.decideFor_allGiven`,
`RentLevy.decideFor_unknown_gradeC`, `RentLevy.charges_ofCanon`, `withRentLevies_pit`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-! ## Facts -/

structure LesseeFacts where
  /-- ISO code, upper case (`""`: not given) -/
  nationality : String := ""
  /-- `"national"`: a national of the levy's country -/
  national : Option Bool := none
  resident : Option Bool := none
  /-- `"kind"`: `"company"` (`some true`) or `"individual"` (`some false`) -/
  company : Option Bool := none
  deriving Repr, Inhabited, BEq

def LesseeFacts.ofJson (j : Json) (nat national resident : String) : LesseeFacts :=
  { nationality := textField j nat (fun s => (squash s).toUpper), national := jsonBool? j national, resident := jsonBool? j resident,
    company := match textField j "kind" id with | "company" => some true | "individual" => some false | _ => none }

theorem lesseeFacts_null : LesseeFacts.ofJson Json.null "nationality" "national" "resident" = {} := by
  rfl

/-- The tenant given on a record: its `"lessee"` object, else the flat `"tenant…"` fields; `none`: neither. -/
def lesseeOnRecord? (j : Json) : Option LesseeFacts :=
  match j.getObjVal? "lessee" with
  | .ok l@(.obj _) => some (LesseeFacts.ofJson l "nationality" "national" "resident")
  | _ =>
    let f := { LesseeFacts.ofJson j "tenantNationality" "tenantNational" "tenantResident" with company := none }
    if f.nationality == "" && f.national.isNone && f.resident.isNone then none else some f

/-- The tenant of asset `i` (`{}`: nothing given). -/
def lesseeOfAsset (g : CanonGlobal) (i : Nat) : LesseeFacts := (lesseeOnRecord? (assetJson g i)).getD {}

/-- Adult `i`'s own nationality and residence (`"nationality"`, `"national"`, `"resident"` on the adult record). -/
def adultNationality (g : CanonGlobal) (i : Nat) : LesseeFacts :=
  { LesseeFacts.ofJson (adultJson g i) "nationality" "national" "resident" with company := some false }

/-- The tenant of a rent line: given on the line, else the household's first adult. -/
def tenantOfLine (g : CanonGlobal) (j : Json) : LesseeFacts := (lesseeOnRecord? j).getD (adultNationality g 0)

namespace LesseeFacts

/-- A national of `country`: `"national"` when given, else the nationality compared; `none`: not given. -/
def national? (f : LesseeFacts) (country : String) : Option Bool :=
  match f.national with
  | some b => some b
  | none => if f.nationality == "" then none else some (f.nationality == country.toUpper)

theorem national?_explicit (f : LesseeFacts) (c : String) (b : Bool) (h : f.national = some b) : f.national? c = some b := by
  simp [national?, h]

end LesseeFacts

inductive LesseeTest where
  | national
  | nonNational
  | resident
  | nonResident
  /-- the nationality is one of these (ISO) -/
  | nationalities (l : List String)
  | company
  | individual
  deriving Repr, Inhabited, BEq

namespace LesseeTest

/-- `some` the test's value when its fact is given. -/
def eval : LesseeTest → LesseeFacts → String → Option Bool
  | .national, f, c => f.national? c
  | .nonNational, f, c => (f.national? c).map (!·)
  | .resident, f, _ => f.resident
  | .nonResident, f, _ => f.resident.map (!·)
  | .nationalities l, f, _ => if f.nationality == "" then none else some (l.any (·.toUpper == f.nationality))
  | .company, f, _ => f.company
  | .individual, f, _ => f.company.map (!·)

def fact : LesseeTest → String
  | .national | .nonNational | .nationalities _ => "the tenant's nationality"
  | .resident | .nonResident => "the tenant's residence"
  | .company | .individual => "whether the tenant is a company"

theorem eval_none (t : LesseeTest) (c : String) : t.eval {} c = none := by
  cases t <;> simp [eval, LesseeFacts.national?]

end LesseeTest

/-! ## The levy -/

inductive RentSide where
  /-- the entity lets assets -/
  | landlord
  /-- the household pays rent (its `rent` basket lines) -/
  | tenant
  deriving Repr, DecidableEq, Inhabited, BEq

structure RentLevy where
  name : String
  /-- the model's ISO code: a tenant of that nationality is a national -/
  country : String
  rateBp : Int
  side : RentSide := .landlord
  /-- the let assets the levy reads (landlord side) -/
  kinds : List AssetKind := [.home, .realEstate]
  /-- every test must hold -/
  tests : List LesseeTest := []
  /-- what an absent fact means (required) -/
  ifUnknown : StateUnknown
  bearer : Bearer := .entity
  oecd : Oecd := .propertyRecurrent
  level : Level := .local
  statute : String := ""
  deriving Inhabited

/-- One item a rent levy reads. -/
structure RentItem where
  event : String
  /-- the rent (−1: not given) -/
  rent : Int
  lessee : LesseeFacts
  deriving Inhabited

/-- How the tests came out. -/
inductive RentDecision where
  | applies (note : String)
  | notApplies
  | general (why : String)
  | unknown (why : String)
  deriving Repr, Inhabited, BEq

namespace RentLevy

/-- The items: the let assets of the kinds (landlord), or the rent lines (tenant). -/
def items (l : RentLevy) (g : CanonGlobal) : List RentItem :=
  match l.side with
  | .landlord =>
    (g.assets.zipIdx.filter fun (a, i) =>
      let j := assetJson g i
      l.kinds.contains a.kind && ((lesseeOnRecord? j).isSome || 0 ≤ nonnegField j "rent"
        || (jsonBool? j "let").getD false)).map fun (a, i) =>
      let j := assetJson g i
      let r := nonnegField j "rent"
      { event := s!"asset {i + 1}", rent := if 0 ≤ r then r else if 0 ≤ a.annualValue then a.annualValue else -1,
        lessee := lesseeOfAsset g i }
  | .tenant =>
    if g.entity != .household then [] else
    let js := (arrField g.raw "consumption").toList
    (g.consumption.zipIdx.filter fun (s, _) => s.good == .rent).map fun (s, i) =>
      { event := s!"line {i + 1} (rent)", rent := pos s.amount, lessee := tenantOfLine g (js.getD i Json.null) }

/-- The tests on a tenant: all given and true → applies; one given and false → not; else per `ifUnknown`. -/
def decideFor (l : RentLevy) (f : LesseeFacts) : RentDecision :=
  let vals := l.tests.map fun t => (t, t.eval f l.country)
  if vals.any (·.2 == some false) then .notApplies
  else match vals.find? (·.2.isNone) with
    | none => .applies ""
    | some (t, _) =>
      match l.ifUnknown with
      | .presume => .applies s!"{t.fact} not given: applied as the statute presumes"
      | .general => .general s!"{t.fact} not given: not applied (the rule's general case)"
      | .gradeC => .unknown s!"{t.fact} not given"

theorem decideFor_allGiven (l : RentLevy) (f : LesseeFacts) (h : ∀ t ∈ l.tests, t.eval f l.country = some true) :
    l.decideFor f = .applies "" := by
  have h1 : (l.tests.map fun t => (t, t.eval f l.country)).any (·.2 == some false) = false := by
    simp only [List.any_map, List.any_eq_false, Function.comp_def]
    intro t ht; simp [h t ht]
  have h2 : (l.tests.map fun t => (t, t.eval f l.country)).find? (·.2.isNone) = none := by
    simp only [List.find?_eq_none, List.mem_map]
    rintro _ ⟨t, ht, rfl⟩; simp [h t ht]
  simp [decideFor, h1, h2]

/-- **No fact, no charge** under `.gradeC`: a levy with a test on the tenant is undecided for a tenant nothing is known of. -/
theorem decideFor_unknown_gradeC (l : RentLevy) (t : LesseeTest) (rest : List LesseeTest) (ht : l.tests = t :: rest)
    (hu : l.ifUnknown = .gradeC) : ∃ w, l.decideFor {} = .unknown w := by
  have h1 : (l.tests.map fun t => (t, t.eval {} l.country)).any (·.2 == some false) = false := by
    simp only [List.any_map, List.any_eq_false, Function.comp_def]
    intro t _; simp [LesseeTest.eval_none]
  have h2 : (l.tests.map fun t => (t, t.eval {} l.country)).find? (·.2.isNone) = some (t, none) := by
    simp [ht, LesseeTest.eval_none]
  exact ⟨s!"{t.fact} not given", by simp [decideFor, h1, h2, hu]⟩

def statute' (l : RentLevy) (note : String) : String := "; ".intercalate ([l.statute, note].filter (· != ""))

def charges (l : RentLevy) (g : CanonGlobal) : List Charge :=
  (l.items g).filterMap fun (item : RentItem) =>
    if item.rent < 0 then none else
    match l.decideFor item.lessee with
    | .applies note =>
      some (charge l.oecd l.name item.rent id (fun r => divR .down (r * l.rateBp) BP) (event := item.event) (level := l.level)
        (bearer := l.bearer) (statute := l.statute' note))
    | _ => none

/-- Grade-C lines (an undecided tenant under `.gradeC`, a let asset with no rent). -/
def unknown (l : RentLevy) (g : CanonGlobal) : List String :=
  (l.items g).filterMap fun (item : RentItem) =>
    let pre := s!"{l.oecd.code} {l.name}: {item.event}"
    match l.decideFor item.lessee with
    | .unknown why => some s!"{pre}: {why} (grade C)"
    | .applies _ => if item.rent < 0 then some s!"{pre}: rent not given (\"rent\" or \"annualValue\") (grade C)" else none
    | _ => none

/-- Informational lines (an undecided tenant under `.general`). -/
def notes (l : RentLevy) (g : CanonGlobal) : List String :=
  (l.items g).filterMap fun (item : RentItem) =>
    match l.decideFor item.lessee with
    | .general why => some s!"{l.oecd.code} {l.name}: {item.event}: {why}"
    | _ => none

def family (l : RentLevy) : Family :=
  { name := s!"{l.oecd.code} {l.name}", covers := [l.oecd], run := fun _ g _ => l.charges g }

theorem charges_ofCanon (l : RentLevy) (c : Canon) : l.charges (CanonGlobal.ofCanon c) = [] := by
  cases h : l.side <;> simp [charges, items, h, CanonGlobal.ofCanon]

end RentLevy

/-- **Rent levies on a model**: the families last; grade-C and informational lines after the model's `unsupported`. -/
def GlobalModel.withRentLevies (m : GlobalModel) (ls : List RentLevy) : GlobalModel :=
  { m with families := m.families ++ ls.map (·.family),
           unsupported := fun args g => m.unsupported args g ++ ls.flatMap (fun l => l.unknown g ++ l.notes g) }

theorem withRentLevies_pit (m : GlobalModel) (ls : List RentLevy) (args : List String) (g : CanonGlobal) :
    ((m.withRentLevies ls).computeGlobal args g).pit = (m.computeGlobal args g).pit := rfl

end TaxKernel.Global
