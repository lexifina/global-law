import KzGlobal.Pit

/-!
# Kazakhstan 2025: employer social contributions, pension contribution, OSMS and the social tax (2200, 3000)
(B.) Social Code (2023): social contributions 5 % (base capped at 7 minimum wages: 85,000 × 7 × 12 = 7,140,000 a year);
employer pension contribution 2.5 % (2025); Law on OSMS: employer 3 % (cap 40 MW: 40,800,000). Tax Code 2017 art. 484-485: social
tax 9.5 % of wages less the employee pension contribution (10 %), less the social contributions (`socTax`).
-/

namespace KzGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Социальные отчисления (5 %)" a.wages (fun w => min (pos w) 7140000) (fun b => divR .down (500 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Social Code (2023)"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "ОПВР (employer 2.5 %)" a.wages pos (fun b => divR .down (250 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Social Code (2023) (2025 rate)"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "ОСМС (employer 3 %)" a.wages (fun w => min (pos w) 40800000) (fun b => divR .down (300 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Law on OSMS (2015)")) }

def socTax (w : Int) : Int := pos (divR .down (950 * (w - w / 10)) BP - divR .down (500 * min w 7140000) BP)
def socTaxF : Family :=
  { name := "3000 social tax", covers := [.payroll],
    run := fun _ g _ => if g.entity == .company then [] else (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
      charge .payroll "Социальный налог (9.5 %)" a.wages id socTax (event := s!"adult {i + 1}") (bearer := .employer) (statute := "Tax Code 2017 arts. 484-485") }

def families : List Family := [fam0, socTaxF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 1000000 }] } } []).map (·.due) == [50000, 25000, 30000]
#guard socTax 1000000 == 35500

end KzGlobal.Social
