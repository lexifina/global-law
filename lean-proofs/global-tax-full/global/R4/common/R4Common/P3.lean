import R4Common.Basic

/-! # R4Common P3-P5 helpers: employer levies, recurrent property tax, final withholding on household income -/

namespace R4
open TaxKernel TaxKernel.Global

/-- An employer levy at a flat rate on wages: on each adult's wages for a household (borne by the employer), on the
payroll for a company (borne by the company). `oecd` is `.sscEmployer` (2200) or `.payroll` (3000). -/
def payrollFamily (oecd : Oecd) (name : String) (rateBp : Int) (statute : String) (level : Level := .central) : Family :=
  { name := s!"{oecd.code} {name}", covers := [oecd],
    run := fun _ g _ =>
      if g.entity == .company then
        (if g.company.payroll ≤ 0 then [] else
          [charge oecd name g.company.payroll id (fun x => divR .down (rateBp * pos x) BP) (event := "payroll")
            (level := level) (statute := statute)])
      else
        (g.household.adults.zipIdx.filter (fun (a, _) => a.wages > 0)).map fun (a, i) =>
          charge oecd name a.wages id (fun x => divR .down (rateBp * pos x) BP) (event := s!"adult {i + 1}")
            (level := level) (bearer := .employer) (statute := statute) }

/-- A recurrent property tax at flat rates: built property on its annual (rental / cadastral) value, land on its
statutory value. Built property without an annual value is skipped (the caller lists it). -/
def propertyFamily (name : String) (builtBp landBp : Int) (statute : String) (level : Level := .local) : Family :=
  { name := s!"4100 {name}", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      g.assets.zipIdx.filterMap fun (a, i) =>
        if a.kind == .land then
          some (charge .propertyRecurrent name a.statutoryValue id (fun x => divR .down (landBp * pos x) BP)
            (event := s!"asset {i + 1} (land)") (level := level) (statute := statute))
        else if (a.kind == .home || a.kind == .realEstate) && decide (a.annualValue ≥ 0) then
          some (charge .propertyRecurrent name a.annualValue id (fun x => divR .down (builtBp * pos x) BP)
            (event := s!"asset {i + 1} (built)") (level := level) (statute := statute))
        else none }

def builtWithoutValue (g : CanonGlobal) : Bool :=
  g.assets.any fun a => (a.kind == .home || a.kind == .realEstate) && decide (a.annualValue < 0)

/-- A final flat withholding on the household's extra domestic income items of one kind (1100). -/
def finalWhtFamily (kind : IncomeKind) (name : String) (rateBp : Int) (statute : String) : Family :=
  { name := s!"1100 {name}", covers := [],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.incomes.zipIdx.filter (fun (x, _) => x.kind == kind && !x.foreign)).map fun (x, i) =>
        charge .pit name x.amount id (fun y => divR .down (rateBp * pos y) BP) (event := s!"income {i + 1} ({kind.name})")
          (statute := statute) }

def testAssets : List Asset := [{ kind := .home, value := 1000000, annualValue := 60000 }, { kind := .land, value := 200000 }]

#guard ((propertyFamily "t" 500 500 "s").run [] { id := "x", household := { id := "x" }, assets := testAssets } []).map (·.due) == [3000, 10000]

end R4
