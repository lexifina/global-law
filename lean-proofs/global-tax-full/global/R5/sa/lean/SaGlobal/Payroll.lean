import TaxKernel.Global
import R5Common

/-!
# Saudi Arabia 2025: expatriate levy (المقابل المالي على العمالة الوافدة), OECD 3000 (pass 3l)

Coordinator decision (pass 3l): OECD heading 3000 covers taxes paid by employers as a fixed amount per person
employed, so the levy the employer pays for each expatriate worker is booked here (bearer: the entity, i.e. the
employer). Grade B: the Council of Ministers decision was not read; facts from official and reliable secondary sources:
* amounts: Ministry of Finance, Fiscal Balance Program (December 2016), as reported by Arab News (23/12/2016,
  node 1028596): from January 2020 SAR 800 a month for each expatriate worker where the expatriates of the
  establishment outnumber its Saudi workers, SAR 700 where they are equal to or fewer (2018: 400/300, 2019: 600/500);
  the tier test as stated by EY tax news 2018-0152 (Ministry of Labor and Social Development resolution effective
  1/1/2018). No later change of the 2020 amounts was found for 2025.
* small establishments: MHRSD news 20/02/2024 (hrsd.gov.sa/media-center/news/200220241, read): the Council of
  Ministers extended for three years the exemption of establishments with nine workers or fewer including the owner:
  two expatriates exempt where the owner works full time in it and is registered with GOSI, four where moreover at
  least one other worker is a Saudi working full time and registered (maximum four).
* licensed industrial facilities: the State bore the levy from October 2019, extended to 31/12/2025 (Council of
  Ministers; press reports of 2024-2025, not read in an official text): booked as a cited zero (flag
  `"licensedIndustrial"`).
Inputs (optional, company line): `company.expatWorkers`, `company.saudiWorkers` (Saudi workers other than the owner),
flags `"ownerFullTimeGosi"`, `"licensedIndustrial"`; a full year (12 months) is charged. Without `expatWorkers`
the heading is listed as grade C, never guessed. Household lines: the levy falls on the employer and its rate
depends on the employer's workforce: listed, not computed.
-/

namespace SaGlobal
open TaxKernel TaxKernel.Global R5Common

/-- an optional field of the company object (-1 when absent) -/
def coInt (g : CanonGlobal) (k : String) : Int :=
  match g.raw.getObjVal? "company" with
  | .ok cj => intField cj k (-1)
  | _ => -1

/-- monthly levy per expatriate: SAR 800 where expatriates outnumber Saudi workers, else SAR 700 -/
def expatLevyMonthly (expat saudi : Int) : Int := if expat > saudi then 800 else 700

/-- expatriates exempt in a small establishment (nine workers or fewer, owner included) -/
def expatSmallExempt (expat saudi : Int) (ownerFT : Bool) : Int :=
  if ownerFT && expat + saudi + 1 ≤ 9 then min expat (if saudi ≥ 1 then 4 else 2) else 0

def expatLevyStatute : String :=
  "Expatriate levy (المقابل المالي): MoF Fiscal Balance Program 2016 (SAR 800/700 a month from 2020, by the expatriate/Saudi ratio); MHRSD 20/02/2024 (small-establishment exemption extended 3 years); grade B"

def expatLevy (g : CanonGlobal) : List Charge :=
  let e := coInt g "expatWorkers"
  let s := max 0 (coInt g "saudiWorkers")
  if g.entity != .company || e < 0 then [] else
  if g.company.flags.contains "licensedIndustrial" then
    [flatCharge .payroll "المقابل المالي على العمالة الوافدة (منشأة صناعية مرخصة)" 0
      (statute := "Council of Ministers: the State bears the levy of licensed industrial facilities to 31/12/2025 (press reports; cited zero)")]
  else
    [charge .payroll "المقابل المالي على العمالة الوافدة" e
      (fun n => pos (n - expatSmallExempt e s (g.company.flags.contains "ownerFullTimeGosi")))
      (fun n => n * expatLevyMonthly e s * 12) (statute := expatLevyStatute)]

def payrollPre3q : Family :=
  { name := "3000 expatriate levy", covers := [.payroll], run := fun _ g _ => expatLevy g }

def payrollUnsupportedPre3q (g : CanonGlobal) : List String :=
  if g.entity == .company then
    (if coInt g "expatWorkers" < 0 then
      ["3000 expatriate levy (SAR 700/800 a month per expatriate worker): company.expatWorkers not given (grade C)"] else [])
  else if (g.str? "nationality").getD ((g.household.str? "nationality").getD "national") == "expatriate"
      && g.household.adults.any (·.wages > 0) then
    ["3000 expatriate levy on the employer (SAR 700/800 a month) not computed on a household line: the employer's workforce is not an input"]
  else []

#guard expatLevyMonthly 10 4 == 800
#guard expatLevyMonthly 4 4 == 700
#guard expatSmallExempt 6 1 true == 4
#guard expatSmallExempt 6 0 true == 2
#guard expatSmallExempt 6 3 true == 0
#guard expatSmallExempt 6 1 false == 0


/-- Pass 3q year-in-force audit: grade C. 3000 expatriate levy grade C (year-in-force audit, pass 3q): the Fiscal Balance Program amounts of 2016 (press) with a 2024 MHRSD statement on exemptions is the version read; its 2025 version or amendment history was not reached, so the rule is not applied The family above is kept (`payrollPre3q`) for a later re-cite;
it is not in the model. -/
def payrollUnsupported (g : CanonGlobal) : List String :=
  (if (payrollPre3q.run [] g []).isEmpty then [] else ["3000 expatriate levy grade C (year-in-force audit, pass 3q): the Fiscal Balance Program amounts of 2016 (press) with a 2024 MHRSD statement on exemptions is the version read; its 2025 version or amendment history was not reached, so the rule is not applied"]) ++ payrollUnsupportedPre3q g

end SaGlobal
