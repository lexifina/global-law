import TaxKernel.Global
import R5Common

/-!
# Iraq 2025: employer social security contributions (2200)

Worker Retirement and Social Security Law No. 18 of 2023 (Official Gazette Al-Waqai' Al-Iraqiyya No. 4734, 28 August
2023; Ministry of Justice English edition, moj.gov.iq PDF archived 2025-04-30, `law/moj_law18_2023_social_security_en.pdf`),
in force 90 days after publication (final article):
* art. 14 Second (b)(1): employers' contributions "(12%) twelve per cent of the total wages and allowances the worker
  receives" (8 retirement, 1 injuries, 1 unemployment, 2 health/maternity);
* art. 14 Second (b)(2): "(25%) twenty-five per cent" for private and mixed-sector employers whose profits come from
  selling oil and other hydrocarbons produced in and exported from Iraq;
* art. 14 Second (c): the State contributes 8 %, except under (b)(2) and for foreign workers, where "the employer shall
  bear the rate of the State's contribution" in addition.
No wage ceiling is written in the Law. Inputs: `oilSector` (true: (b)(2) employer), `nationality` ("foreign": the
employer also bears the State's 8 %). Employee 5 % (art. 14 Second (a)) is not an employer charge.
-/

namespace IqGlobal
open TaxKernel TaxKernel.Global R5Common

def oilSector (g : CanonGlobal) : Bool :=
  match g.raw.getObjValAs? Bool "oilSector" with | .ok b => b | .error _ => false

def foreignWorker (g : CanonGlobal) : Bool :=
  (g.str? "nationality").getD ((g.household.str? "nationality").getD "national") == "foreign"

/-- Employer rate, bp: 12 % or 25 % (art. 14 Second (b)), plus the State's 8 % where the employer bears it ((c)). -/
def employerBp (oil foreign : Bool) : Int :=
  (if oil then 2500 else 1200) + (if oil || foreign then 800 else 0)

def social : Family :=
  { name := "2200 social security (employer)", covers := [.sscEmployer],
    run := fun _ g _ =>
      employerOn "اشتراكات صاحب العمل في الضمان الاجتماعي"
        s!"Law 18/2023 art. 14 Second (b)(1) 12 % / (b)(2) 25 %, (c) State's 8 % borne by the employer for oil-sector and foreign workers: {employerBp (oilSector g) (foreignWorker g)} bp"
        (employerBp (oilSector g) (foreignWorker g)) (-1) g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer social security: English MoJ edition of Law 18/2023; Kurdistan Region schemes and public-sector employers not distinguished"]

#guard employerBp false false == 1200
#guard employerBp false true == 2000
#guard employerBp true false == 3300

end IqGlobal
