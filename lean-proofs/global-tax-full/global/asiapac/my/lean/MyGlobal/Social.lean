import MyGlobal.Pit

/-!
# Malaysia 2025: employer SOCSO, EIS and the HRD levy (2200, 3000)
(B.) Employees' Social Security Act 1969 Third Schedule: employer 1.75 % (both schemes) on wages capped at RM 6,000 a month;
Employment Insurance System Act 2017: 0.2 %, same cap; PSMB Act 2001 (Act 612): HRD levy 1 % of wages for employers with
10+ Malaysian employees. EPF (Act 452, employer 13 %/12 %) is a provident fund credited to members: non-tax (as CPF).
-/

namespace MyGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "SOCSO (employer 1.75 %)" a.wages (fun w => min (pos w) 72000) (fun b => divR .down (175 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Employees' Social Security Act 1969 Third Schedule"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "EIS (employer 0.2 %)" a.wages (fun w => min (pos w) 72000) (fun b => divR .down (20 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Employment Insurance System Act 2017 Second Schedule")) }

def hrdF : Family :=
  { name := "3000 HRD levy", covers := [.payroll],
    run := fun _ g _ => if g.entity != .company || g.company.employees < 10 then [] else
      [charge .payroll "HRD levy (1 %)" g.company.payroll id (fun b => divR .down (100 * b) BP) (statute := "PSMB Act 2001 s. 14 (1 %)")] }

def families : List Family := [fam0, hrdF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000 }] } } []).map (·.due) == [1260, 144]

end MyGlobal.Social
