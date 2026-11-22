import TaxKernel.Global
import R5Common

/-!
# Morocco 2025: employer CNSS and AMO contributions (2200), taxe de formation professionnelle (3000)

CNSS employer page "Paiement de vos cotisations" as captured on 2025-03-25 (`law/ma_cnss_paiement_cotisations_20250325.html`),
"Barèmes et taux de cotisation … déterminés par la loi" (Dahir 1-72-184 on social security, Law 65-00 on AMO; the
rate decrees were not read), employer column ("Charge patronale"):
* prestations familiales 6,40 % of actual salaries;
* prestations sociales à court terme 1,05 % (of which IPE 0,38 %) and à long terme 7,93 %, each salary capped at
  MAD 6,000 a month;
* Assurance Maladie Obligatoire 4,11 % of actual salaries;
* taxe de formation professionnelle 1,6 % of actual salaries (OECD 3000).
-/

namespace MaGlobal
open TaxKernel TaxKernel.Global R5Common

/-- A payroll tax (OECD 3000) of `rateBp` on each adult's wages, borne by the employer. -/
def payrollOn (name statute : String) (rateBp : Int) (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
    charge .payroll name a.wages (fun w => pos w) (fun b => divR .down (rateBp * b) BP)
      (event := s!"adult {i + 1}") (level := .social) (bearer := .employer) (statute := statute)

def maCnssCap : Int := 6000 * 12

def social : Family :=
  { name := "2200/3000 CNSS, AMO, TFP (employer)", covers := [.sscEmployer, .payroll],
    run := fun _ g _ =>
      employerOn "Cotisations CNSS prestations familiales et AMO (patronales)"
        "CNSS barème 2025: prestations familiales 6,40 % + AMO 4,11 % of actual salaries" 1051 (-1) g
      ++ employerOn "Cotisations CNSS prestations sociales (patronales)"
        "CNSS barème 2025: court terme 1,05 % + long terme 7,93 %, salary capped at MAD 6,000 a month" 898 maCnssCap g
      ++ payrollOn "Taxe de formation professionnelle" "CNSS barème 2025: 1,6 % of actual salaries" 160 g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer: rates from the CNSS barème (rate decrees not read); fishing crews' scheme not distinguished"]

#guard maCnssCap == 72000
#guard divR .down (898 * maCnssCap) BP == 6465

end MaGlobal
