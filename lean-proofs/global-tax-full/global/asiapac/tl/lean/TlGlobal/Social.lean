import TlGlobal.Pit

/-!
# Timor-Leste 2025: employer social security (2200)

(B.) Lei 12/2016; DL 20/2017 (republished by DL 30/2021): employer 6 %.
-/

namespace TlGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Segurança social (employer 6 %)" a.wages pos (fun b => divR .down (600 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Lei 12/2016; DL 20/2017")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000 }] } } []).map (·.due) == [6000]

end TlGlobal.Social
