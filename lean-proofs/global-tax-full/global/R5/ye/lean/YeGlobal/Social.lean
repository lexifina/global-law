import TaxKernel.Global
import R5Common

/-!
# Yemen 2025: employer social insurance contributions (2200)

Republican Decision by Law No. 26 of 1991 on Social Insurance (Official Gazette 2/7 of 1991; text in the University of
Minnesota Human Rights Library's Yemeni laws collection, `law/umn_Yemeni_Laws48.pdf`, `law/yl48.nfkc.txt`):
* art. 27(1)(a) employment injuries: employers "بواقع (%٤) من اجور المؤمن عليهم العاملين لديه";
* art. 49(1) old age, disability and death: "حصة صاحب العمل في الاشتراكات وتعادل (%٩) من اجور المؤمن عليهم";
* art. 14-15: contributions on the January wage before any deduction; no ceiling in the Law.
Employer total 13 %. The text is the 1991 enactment; later amendments were not found or checked (grade B).
-/

namespace YeGlobal
open TaxKernel TaxKernel.Global R5Common

def socialPre3q : Family :=
  { name := "2200 social insurance (employer)", covers := [.sscEmployer],
    run := fun _ g _ =>
      employerOn "اشتراكات التأمينات الاجتماعية (صاحب العمل)"
        "RDL 26/1991 art. 49(1) 9 % (old age, disability, death), art. 27(1)(a) 4 % (employment injuries)" 1300 (-1) g }

def socialUnsupportedPre3q (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer social insurance: 1991 text, later amendments not checked; contributions are on the January wage (art. 14), taken as the year's wages"]

#guard divR .down (1300 * 100000) BP == 13000


/-- Pass 3q year-in-force audit: grade C. 2200 social insurance (employer) grade C (year-in-force audit, pass 3q): Republican Decision by Law 26/1991 as enacted (1991) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied The family above is kept (`socialPre3q`) for a later re-cite;
it is not in the model. -/
def socialUnsupported (g : CanonGlobal) : List String :=
  (if (socialPre3q.run [] g []).isEmpty then [] else ["2200 social insurance (employer) grade C (year-in-force audit, pass 3q): Republican Decision by Law 26/1991 as enacted (1991) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied"]) ++ socialUnsupportedPre3q g

end YeGlobal
