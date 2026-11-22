import NpGlobal.Pit

/-!
# Nepal FY 2082/83: employer social security (2200)

(B.) Contribution Based Social Security Act 2074: employer 20 % of basic salary (employee 11 %); basic salary taken as the wage.
-/

namespace NpGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Social security fund (employer 20 %)" a.wages pos (fun b => divR .down (2000 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Contribution Based Social Security Act 2074")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000 }] } } []).map (·.due) == [20000]

end NpGlobal.Social
