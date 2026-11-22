import MhGlobal.Pit

/-!
# Marshall Islands 2025: employer social security contributions (2200)

Social Security Act of 1990 (49 MIRC Ch. 1, `cmp20/world/B14-pacific/mh/law/1990-0075_6.txt`):
* **§ 130 (d)**: every employer contributes out of his own funds "from March 6, 2017, and thereafter 8%" of the worker's
  covered earnings (P.L. 2016-26, 2017-29, 2017-30); § 129 (1) (d): workers 8 % (in the PIT line).
* **§ 103 (k)** "Covered Earnings": the worker's gross earnings in a quarter; the clause added in 2017 ("and thereafter for
  new retirees ten thousand dollars (US$10,000)") reads as a quarterly limit of $10,000 for new retirees: not applied.
-/

namespace MhGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "MISSA employer contribution (8 %)" a.wages pos (fun b => divR .down (800 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Social Security Act 1990 (49 MIRC Ch. 1) § 130 (d), § 103 (k)")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if true then ["the US$10,000 covered-earnings clause of § 103 (k) (2017) is not applied: its wording does not settle a general quarterly ceiling"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 20000 }] } } []).map (·.due) == [1600]

end MhGlobal.Social
