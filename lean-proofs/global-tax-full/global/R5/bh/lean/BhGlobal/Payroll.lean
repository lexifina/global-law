import TaxKernel.Global
import R5Common

/-!
# Bahrain 2025: LMRA monthly fee per expatriate worker (3000)

Labour Market Regulation Law No. 19 of 2006, art. 4 and 42 (fees fixed by Cabinet decision, collected by the LMRA).
Prime Minister's Decision No. 26 of 2008 on the fees charged to employers for issuing and renewing work permits and the
residence permits of family members (in force 01/07/2008; lloc.gov.bh `Legislation/HTM/RCAB2608`, `law/bh_RCAB2608.*`):
* art. 1: per work permit or renewal **BHD 200** (permit, no-objection and entry visa, residence permit, return visa,
  medical examination and identity card), and a **monthly fee of BHD 10 for each foreign worker**;
Decision No. 67 of 2013 (in force 01/09/2013; `RCAB6713`, `law/bh_RCAB6713.*`) added to art. 1: "a reduced fee of
**BHD 5 a month for the first five workers** of the employer".
Decision No. 79 of 2025 (`RCAB7925`, `law/bh_RCAB7925.*`) replaces art. 1 from 01/01/2026: it does not govern 2025.
Model (employer, a company line with the optional `company.expatWorkers`): 12 × (5 × min(n, 5) + 10 × (n − 5)⁺).
The BHD 200 per permit issue or renewal is a charge per permit whose term is not an input: noted, not booked.
Without `expatWorkers` the heading is a grade-C line. **Grade A** (decision texts read).
-/

namespace BhGlobal
open TaxKernel TaxKernel.Global R5Common

/-- an optional field of the company object (-1 when absent) -/
def bhCoInt (g : CanonGlobal) (k : String) : Int :=
  match g.raw.getObjVal? "company" with
  | .ok cj => intField cj k (-1)
  | _ => -1

/-- Decision 26/2008 art. 1 as amended by 67/2013: monthly fee for `n` foreign workers. -/
def lmraMonthly (n : Int) : Int := 5 * min (pos n) 5 + 10 * pos (n - 5)

def lmraStatute : String :=
  "LMR Law 19/2006 art. 4, 42; PM Decision 26/2008 art. 1 (BHD 10 a month per foreign worker) as amended by Decision 67/2013 (BHD 5 for the first five workers)"

def payroll : Family :=
  { name := "3000 LMRA monthly fee", covers := [.payroll],
    run := fun _ g _ =>
      let e := bhCoInt g "expatWorkers"
      if g.entity != .company || e < 0 then [] else
      [charge .payroll "الرسم الشهري عن كل عامل أجنبي (هيئة تنظيم سوق العمل)" e pos (fun n => 12 * lmraMonthly n)
        (statute := lmraStatute)] }

def payrollUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company then
    (if bhCoInt g "expatWorkers" < 0 then
      ["3000 LMRA monthly fee (BHD 5 for each of the first five foreign workers, BHD 10 for each further one): company.expatWorkers not given (grade C)"] else [])
    ++ ["3000 LMRA work-permit fee BHD 200 per issue or renewal (Decision 26/2008 art. 1): a charge per permit, permit term not an input; noted, not booked"]
  else []

#guard lmraMonthly 3 == 15
#guard lmraMonthly 12 == 95
#guard 12 * lmraMonthly 12 == 1140

end BhGlobal
