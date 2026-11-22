import TaxKernel.Global
import R5Common

/-!
# Jordan 2025: work-permit fees for non-Jordanian workers (3000)

Regulation No. 142 of 2019 on work-permit fees for non-Jordanians (نظام رسوم تصاريح العمل لغير الأردنيين لسنة 2019,
issued under Labour Law 8/1996 art. 12; in force on publication, applications from 19/09/2019), text as reprinted by
jordanianlaw.com (`?p=1509`, `law/jo_lawcom_wpfees.{html,txt}`). **Unofficial reprint**, flagged; the amounts agree
with EY's mobility alert of October 2019 (reliable secondary, facts only). The Ministry of Labour's 2025 guide (cited
as "Regulation 142/2019 and its amendments") answered HTTP 451 to the research client: not read, amendments after
2019 not checked.
* art. 2: the employer pays, for issuing or renewing a work permit **for a year or part of a year**, **JOD 400 for
  each worker** in all sectors, except (أ) garment factories in development zones 175, (ب) a second and further
  domestic worker 900, (ج) massage parlours and night clubs 1 000, (د) specialised workers above the quota 2 400,
  (هـ)-(و) free permits of day workers in agriculture 1 400 and construction/loading 1 900;
* art. 3(أ): an additional **JOD 100 per worker** on each issue or renewal (to the Vocational and Technical Skills
  Development Commission).
Model (employer, company line with the optional `company.expatWorkers`): 400 per foreign worker for the year (pass 3r: the amended amounts, below) (the
general rate; the permit is annual). Without `expatWorkers`: grade-C line. **Grade A** (pass 3r: the Ministry's consolidated text, below).
**2025 (pass 3r re-cite, corrected).** The Ministry of Labour's comprehensive guide to work permits for non-Jordanian
workers ("الدليل الشامل لأسس اصدار تصاريح عمل للعمال غير الاردنيين", editions of 28/1/2025 and 22/5/2025, PDFs on
mol.gov.jo, Wayback 30/01/2025 and 26/05/2025; `law/jo_mol_permit_guide_2025*.pdf`, `.txt`) reproduces "نظام رسوم
تصاريح العمل لغير الأردنيين رقم (142) لسنة 2019 وتعديلاته": art. 2 "رسم إصدار تصريح عمل أو تجديده لسنة أو لجزء من السنة
مقداره (350) ثلاثمائة وخمسون ديناراً عن كل عامل في كافة القطاعات الاقتصادية" except (أ) garment factories in development
zones 225, (ب) free permits of day workers 800, (ج) specialised workers above the quota 2,150 a year (1,250 six months,
645 three months); art. 3(أ) "مبلغ إضافي مقداره (50) خمسون ديناراً عند كل إصدار تصريح عمل أو عند تجديده". So in 2025
the general charge is **JOD 350 + 50 = 400** per worker a year (the reprint's 400 + 100 was the 2019 original). Both 2025
editions carry the same text.
-/

namespace JoGlobal
open TaxKernel TaxKernel.Global R5Common

/-- an optional field of the company object (-1 when absent) -/
def joCoInt (g : CanonGlobal) (k : String) : Int :=
  match g.raw.getObjVal? "company" with
  | .ok cj => intField cj k (-1)
  | _ => -1

/-- art. 2 as amended (general rate 350) + art. 3(أ) as amended (50): per foreign worker and year. -/
def permitFees (n : Int) : Int := 400 * pos n

def payroll : Family :=
  { name := "3000 رسوم تصاريح العمل لغير الأردنيين", covers := [.payroll],
    run := fun _ g _ =>
      let e := joCoInt g "expatWorkers"
      if g.entity != .company || e < 0 then [] else
      [charge .payroll "رسوم تصاريح العمل لغير الأردنيين (صاحب العمل)" e pos permitFees
        (statute := "Regulation 142/2019 and its amendments art. 2 (JOD 350 per worker a year, general rate) + art. 3(أ) (JOD 50 per issue or renewal) (MoL comprehensive guide, 28/1/2025 and 22/5/2025 editions)")] }

def payrollUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company then
    (if joCoInt g "expatWorkers" < 0 then
      ["3000 work-permit fees (JOD 350 + 50 per non-Jordanian worker a year): company.expatWorkers not given (grade C)"] else
      ["3000 work-permit fees: general rate booked; sector rates of Regulation 142/2019 art. 2(أ)-(ج) (garments 225, day workers 800, specialised workers above the quota 2,150) not applied"])
  else []

#guard permitFees 8 == 3200



end JoGlobal
