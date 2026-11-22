import LaGlobal.Pit

/-!
# Lao PDR 2025: employer social security (2200)

(B.) Law on Social Security No. 54/NA (2018) arts. 74, 77: employer 6 %. The decree ceiling is not applied.
-/

namespace LaGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Social security (employer 6 %)" a.wages pos (fun b => divR .down (600 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Law on Social Security 54/NA arts. 74, 77")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 1000000 }] } } []).map (·.due) == [60000]

end LaGlobal.Social
