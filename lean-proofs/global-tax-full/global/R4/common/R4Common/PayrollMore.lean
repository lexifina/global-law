import R4Common.Pkgs

/-! # R4Common: employer levies per head and levies on large payrolls (fourteenth pass, P4)

* `payrollHeadFamily`: a fixed amount per employee per year. Company: `employees × perYear` (a company line with a
  payroll but no employee count gets no charge: the count is not guessed; the country's P4 notes list it).
  Household: one charge per adult with wages (the adult is one employee of an unnamed employer), borne by the
  employer. Used for KE Industrial Training (Training Levy) Order (L.N. 113 of 2007) para. 4 (1) as amended by
  L.N. 10 of 2020 and L.N. 62 of 2021: "a levy of six hundred shillings per employee per year".
* `payrollMinFamily`: a flat rate on the whole annual payroll of an employer whose annual payroll is at least
  `minPayroll` (`strict := true`: more than). Company lines only: a household line gives one employee's wages, not
  the employer's payroll, so no charge is booked there (noted by the country). Used for NA Vocational Education and
  Training levy (GN 67 of 2021 para. 3: "An employer with an annual payroll of N$1 000 000 or more must pay the levy";
  para. 5: "1% of the amount of the annual payroll").
-/

namespace R4
open TaxKernel TaxKernel.Global

def payrollHeadFamily (oecd : Oecd) (name : String) (perYear : Int) (statute : String) (level : Level := .central) : Family :=
  { name := s!"{oecd.code} {name}", covers := [oecd],
    run := fun _ g _ =>
      if g.entity == .company then
        (if g.company.payroll ≤ 0 || g.company.employees == 0 then [] else
          [charge oecd name (g.company.employees : Int) id (fun n => perYear * pos n) (event := "payroll")
            (level := level) (statute := statute)])
      else
        (g.household.adults.zipIdx.filter (fun (a, _) => a.wages > 0)).map fun (_, i) =>
          charge oecd name 1 id (fun n => perYear * pos n) (event := s!"adult {i + 1}")
            (level := level) (bearer := .employer) (statute := statute) }

def payrollMinFamily (oecd : Oecd) (name : String) (rateBp minPayroll : Int) (statute : String)
    (strict : Bool := false) (level : Level := .central) : Family :=
  { name := s!"{oecd.code} {name}", covers := [oecd],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let p := g.company.payroll
      if p ≤ 0 || (if strict then decide (p ≤ minPayroll) else decide (p < minPayroll)) then [] else
      [charge oecd name p id (fun x => divR .down (rateBp * pos x) BP) (event := "payroll") (level := level)
        (statute := statute)] }

def tPH (p : Int) (e : Nat) : CanonGlobal := { id := "c", entity := .company, household := { id := "c" }, company := { payroll := p, employees := e } }
-- KE: 12 employees × KES 600
#guard ((payrollHeadFamily .payroll "t" 600 "s").run [] (tPH 5000000 12) []).map (·.due) == [7200]
#guard ((payrollHeadFamily .payroll "t" 600 "s").run [] (tPH 5000000 0) []).map (·.due) == []
#guard ((payrollHeadFamily .payroll "t" 600 "s").run []
  { id := "h", household := { id := "h", adults := [{ wages := 100000 }, { wages := 0 }, { wages := 5 }] } } []).map (·.due) == [600, 600]
-- NA: 1 % of the whole payroll from N$1 000 000 (inclusive)
#guard ((payrollMinFamily .payroll "t" 100 1000000 "s").run [] (tPH 1000000 3) []).map (·.due) == [10000]
#guard ((payrollMinFamily .payroll "t" 100 1000000 "s").run [] (tPH 999999 3) []).map (·.due) == []
#guard ((payrollMinFamily .payroll "t" 100 1000000 "s" (strict := true)).run [] (tPH 1000000 3) []).map (·.due) == []
#guard ((payrollMinFamily .payroll "t" 100 1000000 "s").run []
  { id := "h", household := { id := "h", adults := [{ wages := 5000000 }] } } []).map (·.due) == []

end R4
