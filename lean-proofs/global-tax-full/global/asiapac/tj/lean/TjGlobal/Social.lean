import TjGlobal.Pit

/-!
# Tajikistan 2025: social tax of insurers (employer share, 2200)

Tax Code of the Republic of Tajikistan (2021, in force 1 Jan 2022), edition of 14 May 2025, English translation copied by the
1.x TJ builder (`cmp20/world/B05-former-ussr/tj/law/tc_en_20250514.txt`; the Tajik original governs):
* **art. 328 (1)**: legal entities and individual entrepreneurs-employers paying wages to resident individuals pay social
  tax as insurers; **art. 330 (1)**: base = wages, remuneration and other benefits paid for the period;
* **art. 332 (1)**: insurers 25 % (budgetary institutions), **20 %** (other organisations); (2) insured persons 1 % / 2 %
  (withheld: the employee share is in the vendored PIT line).
Wages are taken as paid by an organisation other than a budgetary institution; no ceiling in the Code.
-/

namespace TjGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Social tax, insurer share (20 %)" a.wages pos (fun b => divR .down (2000 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Tax Code 2021 arts. 328, 330 (1), 332 (1)")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if true then ["budgetary institutions (25 %) and individual entrepreneurs' minimum social tax (art. 332 (3)-(4)) not distinguished"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000 }] } } []).map (·.due) == [20000]

end TjGlobal.Social
