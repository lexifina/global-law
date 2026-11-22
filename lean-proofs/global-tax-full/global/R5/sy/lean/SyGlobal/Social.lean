import TaxKernel.Global
import R5Common

/-!
# Syria 2025: employer social insurance contributions (2200), pass 3l

Social Insurance Law (Legislative Decree 92/1959 as amended, annotated to Legislative Decree 78/2001), unofficial
reprint on mohamah.net (`law/mohamah_57626.html`; no official consolidation reached), grade B:
* art. 21(a): work-injury insurance, "الاشتراكات الشهرية التي يؤديها صاحب العمل بواقع 3% من أجور عماله";
* art. 56(1): old-age, disability and death insurance, "الاشتراكات الشهرية التي يؤديها صاحب العمل بواقع 14% من أجور
  عماله" (art. 56(2): 7 % deducted from the worker).
Not applied: the insurable-wage ceiling and minimum (set by decree, not read), amendments after 2001 (not checked),
the art. 23 reduction for employers giving medical care.
-/

namespace SyGlobal
open TaxKernel TaxKernel.Global R5Common

def socialPre3q : Family :=
  { name := "2200 التأمينات الاجتماعية (employer)", covers := [.sscEmployer],
    run := fun _ g _ =>
      employerOn "اشتراكات التأمينات الاجتماعية (صاحب العمل): إصابات العمل 3 % + الشيخوخة والعجز والوفاة 14 %"
        "LD 92/1959 (Social Insurance Law) art. 21(a) 3 %, art. 56(1) 14 % (mohamah.net reprint, to LD 78/2001)" 1700 (-1) g }

def socialUnsupportedPre3q (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["SY employer contributions: insurable-wage ceiling (by decree) not read: whole wage used; amendments after 2001 not checked"]


/-- Pass 3q year-in-force audit: grade C. 2200 social insurance (employer) grade C (year-in-force audit, pass 3q): LD 92/1959 annotated to LD 78/2001 (unofficial reprint) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied The family above is kept (`socialPre3q`) for a later re-cite;
it is not in the model. -/
def socialUnsupported (g : CanonGlobal) : List String :=
  (if (socialPre3q.run [] g []).isEmpty then [] else ["2200 social insurance (employer) grade C (year-in-force audit, pass 3q): LD 92/1959 annotated to LD 78/2001 (unofficial reprint) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied"]) ++ socialUnsupportedPre3q g

end SyGlobal
