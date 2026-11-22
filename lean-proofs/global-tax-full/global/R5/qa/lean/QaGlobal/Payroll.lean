import TaxKernel.Global
import TaxKernel.Global2
import R5Common

/-!
# Qatar 2025: work-permit fee per foreign worker (3000, pass 3p)

Coordinator decision (pass 3l): a fee fixed by law per person employed and paid by the employer is an OECD 3000 tax.
Texts read on the Ministry of Justice legislation API (`api.moj.gov.qa/api/v1/Legislation/<id>`, article dumps in `law/`):
* Cabinet Decision No. 36 of 2006 on the fees for work permits, recruitment and attestations (`law/qa_cd36_2006_articles.txt`),
  art. 1(1): QAR 100 for each year of a work permit granted or renewed for a worker sponsored by a company, association,
  private establishment or individual (QAR 50 for a replacement). The API dates its repeal 20/08/2025.
  Decision 38/2007 (`law/qa_cd38_2007_articles.txt`) changed only art. 3 (attestations, QAR 20).
* Minister of Labour Decision No. 32 of 2025 (Official Gazette 11/09/2025; in force 26/09/2025 per the API;
  `law/qa_mol32_2025_articles.txt`), art. 1: QAR 100 for each year of a work permit of a worker of a company,
  association, private establishment or individual; art. 4: no fee where the request concerns a Qatari, the child of a
  Qatari mother or a GCC national.
The yearly amount per foreign worker is QAR 100 under either text, so 2025 needs no split.
Company line: optional `company.expatWorkers` (workers other than Qataris and GCC nationals): QAR 100 x n; without it a
grade-C line. Household line with `nationality` = `expatriate` (1.x convention): each adult with wages costs the employer
QAR 100 (bearer employer). Kernel 2.6.0 employer facts: an `employerSector` on the adult (a business sector) confirms a
private employer; without it a private employer is presumed and the charge says so (a public-sector employer is outside
both decisions and is not an input). `national` and `gcc` households: no fee (art. 4).
Recruitment-agency licences (art. 2) and attestations (art. 3) are not per worker employed: not booked.
**Grade A** (decision texts read).
-/

namespace QaGlobal
open TaxKernel TaxKernel.Global R5Common

/-- an optional integer field of the company object (-1 when absent) -/
def qaCoInt (g : CanonGlobal) (k : String) : Int :=
  match g.raw.getObjVal? "company" with
  | .ok cj => intField cj k (-1)
  | _ => -1

/-- 1.x convention: top-level or household `nationality` (`national` by default, `expatriate`, `gcc`) -/
def qaNationality (g : CanonGlobal) : String :=
  match g.raw.getObjValAs? String "nationality" with
  | .ok s => s
  | .error _ => match g.household.raw.getObjValAs? String "nationality" with
    | .ok s => s
    | .error _ => "national"

/-- QAR a year per work permit of a foreign worker (CD 36/2006 art. 1(1); MoL 32/2025 art. 1) -/
def permitFeeYear : Int := 100

def permitStatute : String :=
  "Cabinet Decision 36/2006 art. 1(1) (to 20/08/2025) and Minister of Labour Decision 32/2025 art. 1, 4 (from 26/09/2025): QAR 100 for each year of a foreign worker's work permit"

def privatePresumedNote : String := " (employerSector not given: a private employer presumed)"

def payroll : Family :=
  { name := "3000 work-permit fee", covers := [.payroll],
    run := fun _ g _ =>
      if g.entity == .company then
        let e := qaCoInt g "expatWorkers"
        if e < 0 then [] else
        [charge .payroll "رسوم رخص العمل (QAR 100 a year per foreign worker)" e pos (fun n => permitFeeYear * n)
          (statute := permitStatute)]
      else if qaNationality g != "expatriate" then [] else
      (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
        let presumed := (employerOf g i).sectors.isNone
        charge .payroll "رسوم رخصة العمل (work-permit fee, employer)" 1 pos (fun n => permitFeeYear * n)
          (event := s!"adult {i + 1}") (bearer := .employer)
          (statute := permitStatute ++ (if presumed then privatePresumedNote else "")) }

def payrollUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company then
    (if qaCoInt g "expatWorkers" < 0 then
      ["3000 work-permit fee (QAR 100 a year per foreign worker): company.expatWorkers not given (grade C)"] else [])
  else []

#guard permitFeeYear * 12 == 1200

end QaGlobal
