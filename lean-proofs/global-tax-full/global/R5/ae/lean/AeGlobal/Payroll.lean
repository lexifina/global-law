import TaxKernel.Global
import TaxKernel.Global2
import R5Common

/-!
# United Arab Emirates 2025: MoHRE work-permit fee per foreign worker (3000, pass 3p)

Coordinator decision (pass 3l): a fee fixed by law per person employed and paid by the employer is an OECD 3000 tax.
Cabinet Resolution No. 21 of 2020 on service fees and administrative fines of the Ministry of Human Resources and
Emiratisation, schedules as amended by Cabinet Resolution No. 37 of 2022 (MoHRE publication of the annexed schedules,
English, Internet Archive capture 2022-07-25; `law/ae_mohre_cr37_2022_schedules_en.pdf` / `.txt`): a work permit is
issued, and renewed, for **two years** at AED 250 (category 1 establishment), AED 1 200 (category 2) or AED 3 450
(category 3); the same amounts apply to a transfer between establishments; AED 50 per permit application.
The establishment's category is fixed by MoHRE's classification of establishments: an input here. Kernel 2.6.0
employer facts: the adult's `employerRiskClass` (the employer's tariff class: "1", "2" or "3"), and on a company line
`company.riskClass`, carry it; absent, no charge and a grade-C line (the three amounts differ fourteen-fold: never
presumed).
A year's share of the two-year fee is booked (half the amount; the year of issue or renewal is not an input).
Company line: optional `company.expatWorkers` x the year's share; household line with `nationality` = `expatriate`:
each adult with wages, bearer the employer. The AED 50 application, mission permits and agency licences are not per
worker employed: noted only. The Emiratisation contribution for Emiratis not employed (Cabinet resolutions) is not
read: noted. **Grade B**: MoHRE's own publication of the schedules; the resolutions' Gazette text was not read and no
later amendment was found on MoHRE's archived pages (2022-2026), so the 2025 amounts rest on that publication.
-/

namespace AeGlobal
open TaxKernel TaxKernel.Global R5Common

/-- an optional integer field of the company object (-1 when absent) -/
def aeCoInt (g : CanonGlobal) (k : String) : Int :=
  match g.raw.getObjVal? "company" with
  | .ok cj => intField cj k (-1)
  | _ => -1

/-- 1.x convention: top-level or household `nationality` (`national` by default, `expatriate`, `gcc`) -/
def aeNationality (g : CanonGlobal) : String :=
  match g.raw.getObjValAs? String "nationality" with
  | .ok s => s
  | .error _ => match g.household.raw.getObjValAs? String "nationality" with
    | .ok s => s
    | .error _ => "national"

/-- CR 21/2020 schedules (CR 37/2022): two-year work permit, issue or renewal, by establishment category -/
def mohrePermit2y (cat : String) : Option Int :=
  match cat with
  | "1" => some 250
  | "2" => some 1200
  | "3" => some 3450
  | _ => none

/-- the year's share of the two-year fee -/
def mohrePermitYear (cat : String) : Option Int := (mohrePermit2y cat).map (· / 2)

def mohreStatute (cat : String) : String :=
  s!"Cabinet Resolution 21/2020 schedules as amended by Cabinet Resolution 37/2022 (MoHRE): two-year work permit, category {cat} establishment; half booked for the year"

def payroll : Family :=
  { name := "3000 MoHRE work-permit fee", covers := [.payroll],
    run := fun _ g _ =>
      if g.entity == .company then
        let e := aeCoInt g "expatWorkers"
        let cat := (companyEmployer g).riskClass
        match mohrePermitYear cat with
        | some fee => if e < 0 then [] else
            [charge .payroll "MoHRE work-permit fee (a year's share)" e pos (fun n => fee * n) (statute := mohreStatute cat)]
        | none => []
      else if aeNationality g != "expatriate" then [] else
      (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).filterMap fun (_, i) =>
        let cat := (employerOf g i).riskClass
        (mohrePermitYear cat).map fun fee =>
          charge .payroll "MoHRE work-permit fee (a year's share, employer)" 1 pos (fun n => fee * n)
            (event := s!"adult {i + 1}") (bearer := .employer) (statute := mohreStatute cat) }

def payrollUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company then
    (if aeCoInt g "expatWorkers" < 0 then
      ["3000 MoHRE work-permit fee (AED 250 / 1 200 / 3 450 per two years by establishment category): company.expatWorkers not given (grade C)"]
     else if (mohrePermit2y (companyEmployer g).riskClass).isNone then
      ["3000 MoHRE work-permit fee: company.riskClass (MoHRE establishment category 1, 2 or 3) not given (grade C)"] else [])
    ++ ["3000 Emiratisation contribution per Emirati not employed (Cabinet resolutions): not read (grade C)"]
  else if aeNationality g == "expatriate" then
    (g.household.adults.zipIdx.filter fun (a, i) => a.wages > 0 && (mohrePermit2y (employerOf g i).riskClass).isNone).map
      fun (_, i) => s!"3000 MoHRE work-permit fee, adult {i + 1}: employerRiskClass (MoHRE establishment category 1, 2 or 3) not given (grade C)"
  else []

#guard mohrePermitYear "1" == some 125 && mohrePermitYear "2" == some 600 && mohrePermitYear "3" == some 1725
#guard mohrePermitYear "" == none

end AeGlobal
