import TaxKernel.Global2.CorpRule

/-!
# TaxKernel.Global2.Sector (2.5.0, 2026-11-21): the company's sector and CIT rates by sector (R2-P9-1)

Many corporate income taxes set the rate by the company's activity: GY Corporation Tax Act Cap. 81:03 s. 10 (40 % with a
2 % turnover minimum for a "commercial company", 45 % for a telephone company, 25 % for any other), AG s. 32 (4), banks,
insurers, petroleum and mining companies in many codes.

**The input** (optional, canonical): `company.sector` on the company record, a string or an array of strings (a company
in several sectors). The agreed names (`Sector.canonical`): `general`, `commercialTrading` (trading in goods it did not
manufacture, commission agency), `manufacturing`, `telecom`, `bank`, `insurer`, `petroleum`, `mining`, `agriculture`,
`tourism`, `shipping`, `utilities`. Another string is read as given (for a statute's own category; `Sector.isCanonical`
lets a dataset check its names). `Company` is unchanged: `companySectors g` reads the line (`none`: not given).

**The rule** (`SectorCorp`): a general 2.1 `CorpRule` with its provision, and `bySector` rules (`SectorRule`: sectors,
a `CorpRule`, its provision), the first whose sectors meet the company's applies; a company whose sector is given and in
none of them is under the general rule (the statute's "any other company"). **What an absent sector means is declared by
the model** (`ifAbsent`, no default): `.general` (the general rule, and the charge's statute ends with `absentSectorNote`;
`SectorCorp.notes` adds a line), or `.gradeC` (no CIT charge; `SectorCorp.unknown` lists it as grade C). A rule without
`bySector` never reads the sector and books exactly the `CorpRule`'s charge (`ofRule_citCharges`).

Theorems: `SectorCorp.ofRule_citCharges`, `pick_given`, `pick_absent_general`, `pick_absent_gradeC`, `pick_noSilent`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-- The agreed sector names (`company.sector`). -/
def Sector.canonical : List String :=
  ["general", "commercialTrading", "manufacturing", "telecom", "bank", "insurer", "petroleum", "mining", "agriculture",
   "tourism", "shipping", "utilities"]

def Sector.isCanonical (s : String) : Bool := Sector.canonical.contains s

/-- The company's sectors from `company.sector` (a string, or an array of strings); `none`: not given. -/
def companySectors (g : CanonGlobal) : Option (List String) :=
  match g.raw.getObjVal? "company" with
  | .ok cj =>
    match cj.getObjVal? "sector" with
    | .ok (.str s) => if s.isEmpty then none else some [s]
    | .ok (.arr a) =>
      let l := a.toList.filterMap fun x => match x with | .str s => some s | _ => none
      if l.isEmpty then none else some l
    | _ => none
  | .error _ => none

/-- What an absent `company.sector` means (declared by the model; no default). -/
inductive SectorAbsent where
  /-- the general rule (the charge's statute says so: `absentSectorNote`) -/
  | general
  /-- no CIT charge: grade C -/
  | gradeC
  deriving Repr, DecidableEq, Inhabited, BEq

/-- The text a charge booked under the general rule for want of a sector carries at the end of its statute. -/
def absentSectorNote : String := " (company.sector not given: the general rule, as the model declares)"

/-- A rate for companies of some sectors. -/
structure SectorRule where
  sectors : List String
  rule : CorpRule
  statute : String
  deriving Repr, Inhabited

/-- 2.7.0 (R4-18-2): sectors taxed under another Act, not this tax (NA petroleum: Petroleum (Taxation) Act). -/
structure SectorOutside where
  sectors : List String
  /-- the other Act -/
  statute : String
  deriving Repr, Inhabited

/-- CIT by sector: the first `bySector` rule that meets the company's sectors, else the general rule. -/
structure SectorCorp where
  general : CorpRule
  /-- the general rule's provision -/
  statute : String
  bySector : List SectorRule := []
  ifAbsent : SectorAbsent
  /-- 2.7.0 (R4-18-2): sectors outside this tax (no charge; `unknown` names the other Act, grade C) -/
  outside : List SectorOutside := []
  deriving Repr, Inhabited

namespace SectorCorp

/-- The rule and provision for the entity; `none`: the sector decides, is not given, and the model said grade C. -/
def pick (s : SectorCorp) (g : CanonGlobal) : Option (CorpRule × String) :=
  if s.bySector.isEmpty then some (s.general, s.statute) else
  match companySectors g with
  | some secs =>
    match s.bySector.find? (fun r => r.sectors.any secs.contains) with
    | some r => some (r.rule, r.statute)
    | none => some (s.general, s.statute)
  | none =>
    match s.ifAbsent with
    | .general => some (s.general, s.statute ++ absentSectorNote)
    | .gradeC => none

/-- 2.7.0: the `outside` entry the company's given sectors meet, if any (absent sector: none). -/
def outsideOf (s : SectorCorp) (g : CanonGlobal) : Option SectorOutside :=
  if s.outside.isEmpty then none else
  match companySectors g with
  | some secs => s.outside.find? (fun o => o.sectors.any secs.contains)
  | none => none

def citCharges (s : SectorCorp) (g : CanonGlobal) (credit : Int := 0) : List Charge :=
  if (s.outsideOf g).isSome then [] else
  match s.pick g with
  | some (r, st) => [r.citCharge g st credit]
  | none => []

/-- For `unsupported`: the CIT not computed for want of a sector (company entities). -/
def unknown (s : SectorCorp) (name : String) (g : CanonGlobal) : List String :=
  if g.entity == .company && (s.outsideOf g).isSome then
    [s!"1200 {name}: company.sector is taxed under {((s.outsideOf g).map (·.statute)).getD ""}, not this tax (grade C)"]
  else if g.entity == .company && (s.pick g).isNone then
    [s!"1200 {name}: company.sector not given; the rate depends on it (grade C)"]
  else []

/-- For `notes`: the general rule taken for want of a sector (company entities, `ifAbsent := .general`). -/
def notes (s : SectorCorp) (name : String) (g : CanonGlobal) : List String :=
  if g.entity == .company && !s.bySector.isEmpty && (companySectors g).isNone && s.ifAbsent == .general then
    [s!"1200 {name}: company.sector not given: the general rule applied (declared by the model)"]
  else []

/-- 1200 family: the CIT by sector, the statutory withholding on payments abroad, and any extra company charges (as
`CorpRule.family`). -/
def family (s : SectorCorp) (name : String) (w : Wht) (extra : Company → List Charge := fun _ => []) : Family :=
  { name := s!"1200 {name}", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else s.citCharges g ++ w.charges g.company ++ extra g.company }

/-- A rule without sector rates never reads the sector: exactly the `CorpRule`'s charge. -/
theorem ofRule_citCharges (r : CorpRule) (st : String) (a : SectorAbsent) (g : CanonGlobal) (cr : Int) :
    ({ general := r, statute := st, ifAbsent := a } : SectorCorp).citCharges g cr = [r.citCharge g st cr] := by
  simp [citCharges, pick, outsideOf]

/-- 2.7.0: without `outside` entries the charges are those of 2.6.0 (the pick). -/
theorem citCharges_noOutside (s : SectorCorp) (g : CanonGlobal) (cr : Int) (h : s.outside = []) :
    s.citCharges g cr = (match s.pick g with | some (r, st) => [r.citCharge g st cr] | none => []) := by
  simp [citCharges, outsideOf, h]

/-- 2.7.0: a company of a sector outside this tax is not charged under it. -/
theorem citCharges_outside (s : SectorCorp) (g : CanonGlobal) (cr : Int) (h : (s.outsideOf g).isSome) :
    s.citCharges g cr = [] := by
  simp [citCharges, h]

/-- A given sector: the first rule that lists it, else the general rule (never grade C). -/
theorem pick_given (s : SectorCorp) (g : CanonGlobal) (secs : List String) (h : companySectors g = some secs) :
    (s.pick g).isSome := by
  unfold pick; split
  · rfl
  · rw [h]; simp only; split <;> rfl

theorem pick_absent_general (s : SectorCorp) (g : CanonGlobal) (hb : s.bySector ≠ []) (h : companySectors g = none)
    (ha : s.ifAbsent = .general) : s.pick g = some (s.general, s.statute ++ absentSectorNote) := by
  simp [pick, hb, h, ha]

theorem pick_absent_gradeC (s : SectorCorp) (g : CanonGlobal) (hb : s.bySector ≠ []) (h : companySectors g = none)
    (ha : s.ifAbsent = .gradeC) : s.pick g = none := by
  simp [pick, hb, h, ha]

/-- **Never silent**: when sector rates exist and the sector is not given, the CIT is either booked with the declared
note at the end of its statute, or not booked at all. -/
theorem pick_noSilent (s : SectorCorp) (g : CanonGlobal) (hb : s.bySector ≠ []) (h : companySectors g = none) :
    s.pick g = none ∨ ∃ r st, s.pick g = some (r, st ++ absentSectorNote) := by
  cases ha : s.ifAbsent
  · exact Or.inr ⟨s.general, s.statute, pick_absent_general s g hb h ha⟩
  · exact Or.inl (pick_absent_gradeC s g hb h ha)

end SectorCorp

end TaxKernel.Global
