import UzGlobal.Pit

/-!
# Uzbekistan 2025: social tax (3000/2200)

(B.) Tax Code (ZRU-599) art. 405: social tax 12 % of the wage bill (budget organisations 25 %), booked as an employer social contribution (2200).
-/

namespace UzGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Социальный налог (12 %)" a.wages pos (fun b => divR .down (1200 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Tax Code art. 405")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000 }] } } []).map (·.due) == [12000]

end UzGlobal.Social
