import TaxKernel.Global
import R5Common

/-!
# Egypt 2025: employer social insurance contributions (2200)

Social Insurance and Pensions Law No. 148 of 2019, NOSI's copy (1.x `law/w5/eg_law148_2019.pdf`), for employees of
private employers (art. 2 first, items 3-5):
* art. 19(1)(a): old age, disability and death, employer "(12٪) من أجر المؤمن عليهم" (the 1 % step every seven years
  first applies after 2025);
* art. 36(2): end-of-service reward scheme, employer (1٪);
* art. 46(1)-(2): work injuries, employer (1٪) (treatment, paid over to the health insurance body) and (0.5٪) (cash
  benefits; up to 1 % by the Regulations' risk classes: the minimum is applied);
* art. 70(1)(a)(2): sickness, employer (3.25٪) for items 3-5;
* art. 86(1): unemployment, employer (1٪).
Total 18,75 % of the contribution wage, bounded by the Regulations' monthly limits, for 2025 EGP 2,300-14,500 (NOSI
notice of 30/11/2025 raising them from 1 January 2026; the 1.x model's source): the ceiling 174,000 a year is applied;
the floor (wages below 2,300 a month counted at 2,300) is not.
-/

namespace EgGlobal
open TaxKernel TaxKernel.Global R5Common

def egCap : Int := 14500 * 12

def social : Family :=
  { name := "2200 social insurance (employer)", covers := [.sscEmployer],
    run := fun _ g _ =>
      employerOn "اشتراكات التأمين الاجتماعي (صاحب العمل)"
        "Law 148/2019 art. 19(1)(a) 12 %, 36(2) 1 %, 46 1 % + 0.5 %, 70(1)(a)(2) 3.25 %, 86(1) 1 % (EGP 14,500 a month)" 1875 egCap g }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer social insurance: contribution-wage floor not applied; injury cash rate at the 0.5 % minimum; government employers (items 1-2) not distinguished"]

#guard egCap == 174000

end EgGlobal
