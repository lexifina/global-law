import TaxKernel.Global
import R5Common

/-!
# Kuwait 2025: employer social insurance contributions (2200)

PIFSS consolidated book 1 (laws, edition 2021, `law/pifss_book1_2021.pdf`; pages read as images, the text layer
garbles digits):
* Social Insurance Law 61/1976 art. 11(ب) (as amended by DL 127/1992): employers pay "(10%) من مرتبات المؤمن عليهم";
  art. 1(م) note: maximum salary KD 1,500 a month (Ministerial Decision 7/2010, from 2011-04-01); p. 23, 18.
* Supplementary insurance DL 128/1992 art. 4(ب) (restated in the explanatory memorandum, p. 207): employers "(10%)"
  of the salary above the basic maximum; art. 1(3): supplementary maximum KD 1,250 a month (Decision 1/2005), p. 292.
  So 10 % on the salary up to KD 2,750 a month.
* Unemployment insurance Law 101/2013 art. 3 first (2) (p. 312): employers "(0.5%)" of the basic and supplementary
  salaries; private and oil sectors.
* Work injuries (Law 61/1976 part IV, 2 %): not in force (DL 126/1977 defers parts IV-V to a decree; p. 43 note).
Insured persons are Kuwaiti (the 1.x model is a Kuwaiti private-sector employee); `nationality` other than
`national` gives no charge. The book is the 2021 edition: later decisions not seen (grade B).
-/

namespace KwGlobal
open TaxKernel TaxKernel.Global R5Common

def nationalityKw (g : CanonGlobal) : String := (g.str? "nationality").getD ((g.household.str? "nationality").getD "national")

/-- KD 2,750 a month (basic 1,500 + supplementary 1,250), a year. -/
def kwCap : Int := (1500 + 1250) * 12

def socialPre3q : Family :=
  { name := "2200 PIFSS employer contributions", covers := [.sscEmployer],
    run := fun _ g _ =>
      if nationalityKw g != "national" then [] else
      employerOn "اشتراكات التأمينات الاجتماعية (صاحب العمل)"
        "Law 61/1976 art. 11(b) 10 % (KD 1,500); DL 128/1992 art. 4(b) 10 % (next KD 1,250); Law 101/2013 art. 3 0.5 %" 1050 kwCap g }

def socialUnsupportedPre3q (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer: PIFSS book 2021 edition (later ceiling decisions not seen); government employers (no unemployment share) and the minimum salary not applied; non-Kuwaitis are outside PIFSS"]

#guard kwCap == 33000
#guard divR .down (1050 * 33000) BP == 3465


/-- Pass 3q year-in-force audit: grade C. 2200 PIFSS employer contributions grade C (year-in-force audit, pass 3q): the PIFSS consolidated laws book 1, 2021 edition, is the version read; its 2025 version or amendment history was not reached, so the rule is not applied The family above is kept (`socialPre3q`) for a later re-cite;
it is not in the model. -/
def socialUnsupported (g : CanonGlobal) : List String :=
  (if (socialPre3q.run [] g []).isEmpty then [] else ["2200 PIFSS employer contributions grade C (year-in-force audit, pass 3q): the PIFSS consolidated laws book 1, 2021 edition, is the version read; its 2025 version or amendment history was not reached, so the rule is not applied"]) ++ socialUnsupportedPre3q g

end KwGlobal
