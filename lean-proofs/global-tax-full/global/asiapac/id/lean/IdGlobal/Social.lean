import IdGlobal.Pit

/-!
# Indonesia 2025: employer BPJS contributions (2200)
(B, official BPJS tables.) PP 46/2015 JHT 3.7 %; PP 45/2015 JP 2 % (wage cap Rp 10,547,400 a month in 2025: 126,568,800 a
year); PP 44/2015 JKK 0.24 % (lowest risk group) and JKM 0.3 %; Perpres 82/2018 jo. 64/2020 health 4 % (cap Rp 12 m a month).
-/

namespace IdGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "BPJS JHT (3.7 %)" a.wages pos (fun b => divR .down (370 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "PP 46/2015 Pasal 16"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "BPJS JP (2 %)" a.wages (fun w => min (pos w) 126568800) (fun b => divR .down (200 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "PP 45/2015 Pasal 28"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "BPJS JKK (0.24 %) + JKM (0.3 %)" a.wages pos (fun b => divR .down (54 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "PP 44/2015 Pasal 16, 18"))
      ++ ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "BPJS Kesehatan (4 %)" a.wages (fun w => min (pos w) 144000000) (fun b => divR .down (400 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Perpres 82/2018 Pasal 30 jo. Perpres 64/2020")) }

def families : List Family := [fam0]

def absent : List Absent :=
  [{ oecd := .payroll, why := "No payroll tax in Indonesia (registry: not levied); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000000 }] } } []).map (·.due) == [3700000, 2000000, 540000, 4000000]

end IdGlobal.Social
