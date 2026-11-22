import BtGlobal.Pit

/-!
# Bhutan 2025: employer NPPF contribution (2200)

(B.) National Pension and Provident Fund Act 2018: employer 11 % (pension and provident accounts; the pension part is pooled).
-/

namespace BtGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "NPPF (employer 11 %)" a.wages pos (fun b => divR .down (1100 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "NPPF Act 2018")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000 }] } } []).map (·.due) == [11000]

end BtGlobal.Social
