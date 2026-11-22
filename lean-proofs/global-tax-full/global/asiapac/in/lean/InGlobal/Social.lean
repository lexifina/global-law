import InGlobal.Pit

/-!
# India 2025: employer EPS/EPF and ESI (2200)
(B.) EPF and MP Act 1952 s. 6 and the schemes: employer 12 % of wages up to Rs 15,000 a month (180,000 a year), of which 8.33 %
goes to the pension scheme (EPS, a pooled social-security pension: 2200) and 3.67 % to the member's provident account
(non-tax, as CPF: not modelled). ESI Act 1948 s. 39 + Regulations: employer 3.25 % where wages ≤ Rs 21,000 a month.
-/

namespace InGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "EPS (employer 8.33 % of wages up to Rs 15,000 a month)" a.wages (fun w => min (pos w) 180000) (fun b => divR .down (833 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "EPF and MP Act 1952 s. 6A; EPS 1995 para. 3")) }

def esiF : Family :=
  { name := "2200 ESI (employer 3.25 %)", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0 && a.wages ≤ 252000).map fun (a, i) =>
        charge .sscEmployer "ESI (employer 3.25 %)" a.wages id (fun b => divR .down (325 * b) BP) (event := s!"adult {i + 1}") (level := .social) (bearer := .employer) (statute := "ESI Act 1948 s. 39; ESI (Central) Rules r. 51") }

def families : List Family := [fam0, esiF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 240000 }] } } []).map (·.due) == [14994]
#guard (esiF.run [] { id := "t", household := { id := "t", adults := [{ wages := 240000 }] } } []).map (·.due) == [7800]

end InGlobal.Social
