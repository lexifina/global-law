import KgGlobal.Pit

/-!
# Kyrgyzstan 2025: employer insurance contributions (2200)

(B.) Law on Tariffs of Insurance Contributions: employer 17.25 %; the base ceiling is not applied.
-/

namespace KgGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Страховые взносы (employer 17.25 %)" a.wages pos (fun b => divR .down (1725 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Law on Tariffs of Insurance Contributions")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000 }] } } []).map (·.due) == [17250]

end KgGlobal.Social
