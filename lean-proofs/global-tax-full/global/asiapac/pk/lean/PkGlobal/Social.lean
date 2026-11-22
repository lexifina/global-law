import PkGlobal.Pit

/-!
# Pakistan 2025: employer EOBI contribution (2200)
(B.) Employees' Old-Age Benefits Act 1976 s. 9: employer 5 % of the minimum wage (Rs 37,000 a month from 2025-07): Rs 1,850 a
month, Rs 22,200 a year per employee. Punjab Employees' Social Security (6 %) not modelled (C).
-/

namespace PkGlobal.Social
open TaxKernel TaxKernel.Global

def eobiF : Family :=
  { name := "2200 EOBI (employer)", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
        charge .sscEmployer "EOBI (5 % of the minimum wage)" a.wages id (fun _ => 22200) (event := s!"adult {i + 1}") (level := .social) (bearer := .employer) (statute := "EOBI Act 1976 s. 9 (minimum wage Rs 37,000)") }

def families : List Family := [eobiF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (eobiF.run [] { id := "t", household := { id := "t", adults := [{ wages := 1000000 }] } } []).map (·.due) == [22200]

end PkGlobal.Social
