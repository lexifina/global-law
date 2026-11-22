import TaxKernel.Global
import R5Common

/-!
# Azerbaijan 2025: employer social contributions (2200)

Texts as in force in 2025 (e-qanun.az, saved by the 1.x builder: `law/ssi250_14_20250813.txt`, `law/unemp_9.txt`,
`law/med_15-10.txt`):
* Law 250-IQ on social insurance, art. 14.4 (for 7 years from 1 January 2019, insured persons working for employers
  outside the oil-gas sector and outside the state sector): monthly income up to 200 manat, employer "22 faiz"; above,
  "44 manat + 200 manatdan çox olan hissənin 15 faizi". Art. 14.3.1 (oil-gas or state employers: input
  `oilGasOrState`: true): 22 % of the payroll.
* Law 765-VQ on unemployment insurance, art. 9.0.1: employer 0,5 % of the payroll.
* Law 725-IQ on medical insurance, art. 15-10.1.2: employer 2 % of the wage up to 8000 manat a month, 0,5 % above.
Annual wages are read as twelve equal months.
-/

namespace AzGlobal
open TaxKernel TaxKernel.Global R5Common

def oilGasOrState (g : CanonGlobal) : Bool :=
  match g.raw.getObjValAs? Bool "oilGasOrState" with | .ok b => b | .error _ => false

/-- Annual employer social insurance on annual wages `w` (art. 14.4, or 14.3.1 when `flat`). -/
def ssiEmployer (flat : Bool) (w : Int) : Int :=
  let w := pos w
  if flat || w ≤ 2400 then divR .down (2200 * w) BP else 528 + divR .down (1500 * (w - 2400)) BP

def medEmployer (w : Int) : Int := (Schedule.ofList [(0, 200), (96000, 50)]).tax {} (pos w)

def social : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).flatMap fun (a, i) =>
        [charge .sscEmployer "Məcburi dövlət sosial sığorta haqqı (sığortaedən)" a.wages pos (ssiEmployer (oilGasOrState g))
           (event := s!"adult {i + 1}") (level := .social) (bearer := .employer)
           (statute := if oilGasOrState g then "Law 250-IQ art. 14.3.1 (22 %)" else "Law 250-IQ art. 14.4 (22 % to 200 manat a month, then 44 + 15 %)"),
         charge .sscEmployer "İşsizlikdən sığorta haqqı (sığortaedən)" a.wages pos (fun b => divR .down (50 * b) BP)
           (event := s!"adult {i + 1}") (level := .social) (bearer := .employer) (statute := "Law 765-VQ art. 9.0.1 (0,5 %)"),
         charge .sscEmployer "İcbari tibbi sığorta haqqı (sığortalı)" a.wages pos medEmployer
           (event := s!"adult {i + 1}") (level := .social) (bearer := .employer)
           (statute := "Law 725-IQ art. 15-10.1.2 (2 % to 8000 manat a month, 0,5 % above)")] }

#guard ssiEmployer false 2400 == 528
#guard ssiEmployer false 12000 == 1968
#guard ssiEmployer true 12000 == 2640
#guard medEmployer 120000 == 2040

end AzGlobal
