import FmGlobal.Pit

/-!
# Micronesia (FSM) 2025: employer social security tax (2200)

FSM Code Title 53 ch. 9 (2014 codification, `cmp20/world/B14-pacific/fm/law/T53_Ch09_2014.txt`, ch. 6 definitions
`T53_Ch06_2014.txt`):
* **§ 902 (7)**: "with respect to wages paid on and after January 1, 2013, the rate shall be seven point five (7.5) percent"
  (an excise tax on every employer); § 901 (1) (g): employees 7.5 % (in the PIT line).
* **§ 603 (15) (a)**: wages exclude the part of remuneration "in excess of $9,000 beginning on January 1, 2023 ... paid in a
  quarterly reporting period by one employer": a ceiling of $36,000 a year (four quarters of $9,000).
-/

namespace FmGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "FSM Social Security employer tax (7.5 %)" a.wages (fun w => min (pos w) 36000) (fun b => divR .down (750 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "FSMC 53 § 902 (7), § 603 (15) (a)")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if true then ["the $9,000 ceiling applies per quarter and per employer: annual wages are taken as paid evenly by one employer"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 20000 }] } } []).map (·.due) == [1500]
#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 50000 }] } } []).map (·.due) == [2700]

end FmGlobal.Social
