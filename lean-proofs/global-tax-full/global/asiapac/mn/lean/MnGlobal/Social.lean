import MnGlobal.Pit

/-!
# Mongolia 2025: employer social insurance (2200)

(B.) Нийгмийн даатгалын ерөнхий хууль (2023) arts. 18-19: employer 12.5 % (lowest occupational-risk class; 13.5-14.5 % in riskier classes). The contribution ceiling is not applied.
-/

namespace MnGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Нийгмийн даатгал (employer 12.5 %)" a.wages pos (fun b => divR .down (1250 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Social Insurance General Law (2023) art. 18-19")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 1000000 }] } } []).map (·.due) == [125000]

end MnGlobal.Social
