import TaxKernel.Global
import R5Common

/-!
# Qatar 2025: employer social insurance contribution (2200)

Social Insurance Law No. 1 of 2022 (Al Meezan, 1.x `law/law-2022-1_social_insurance.txt`), art. 11: the
contribution on the contribution salary "بما لا يزيد على (100,000) مائة ألف ريال", 21 %, of which
"(14%) أربعة عشر في المائة، تُسددها جهة العمل". Insured persons are Qatari (art. 2-3); the household's `nationality`
(1.x convention: `national` default) selects them. Ceiling 100 000 a month = 1 200 000 a year.
-/

namespace QaGlobal
open TaxKernel TaxKernel.Global R5Common

def nationalityQa (g : CanonGlobal) : String := (g.str? "nationality").getD ((g.household.str? "nationality").getD "national")

def social : Family :=
  { name := "2200 GRSIA employer contribution", covers := [.sscEmployer],
    run := fun _ g _ =>
      if nationalityQa g != "national" then [] else
      employerOn "social insurance contribution (employer)" "Social Insurance Law 1/2022 art. 11 (14 %, QAR 100,000 a month)" 1400 1200000 g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  (if nationalityQa g == "gcc" then ["GCC national: home state's scheme (not modelled)"] else [])

end QaGlobal
