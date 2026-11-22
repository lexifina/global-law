import TaxKernel.Global
import R5Common

/-!
# Libya 2025: employer social security contribution (2200)

Tax Authority encyclopaedia "موسوعة التشريعات الضريبية الحديثة" (2016, `law/m2016.pdf` -> the 1.x copy; scanned):
* Law 1/1991 art. 3 and Fund decision 182/1991 art. 1 (PDF pp. 203-206): the contribution is shared 25 % insured,
  70 % employer, 5 % treasury for national employers; 25 % / 75 % for non-national employers;
* table "جدول توزيع عبء الاشتراكات الضمانية" (book p. 208, PDF p. 207, read as an image): total 15 % of the actual
  salary; "70% من الاشتراك وهو ما نسبته 10.50% من المرتب" for an employee of a national employer, 11.25 % for a
  non-national employer; in force from June 1991.
No ceiling in these texts. The 2016 compilation is the latest dated text reached (grade B).
-/

namespace LyGlobal
open TaxKernel TaxKernel.Global R5Common

def socialPre3q : Family :=
  { name := "2200 social security (employer)", covers := [.sscEmployer],
    run := fun _ g _ =>
      employerOn "الاشتراك الضماني (حصة جهة العمل)"
        "Law 1/1991 art. 3(b); Fund decision 182/1991 art. 1(b): 70 % of the 15 % contribution = 10.50 % of salary" 1050 (-1) g }

def socialUnsupportedPre3q (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer social security at the national-employer share 10.50 % (non-national employers 11.25 %); texts as compiled in 2016"]

#guard divR .down (1050 * 100000) BP == 10500


/-- Pass 3q year-in-force audit: grade C. 2200 social security (employer) grade C (year-in-force audit, pass 3q): Law 13/1980 and Fund decision 182/1991 from the encyclopaedia of 2016 is the version read; its 2025 version or amendment history was not reached, so the rule is not applied The family above is kept (`socialPre3q`) for a later re-cite;
it is not in the model. -/
def socialUnsupported (g : CanonGlobal) : List String :=
  (if (socialPre3q.run [] g []).isEmpty then [] else ["2200 social security (employer) grade C (year-in-force audit, pass 3q): Law 13/1980 and Fund decision 182/1991 from the encyclopaedia of 2016 is the version read; its 2025 version or amendment history was not reached, so the rule is not applied"]) ++ socialUnsupportedPre3q g

end LyGlobal
