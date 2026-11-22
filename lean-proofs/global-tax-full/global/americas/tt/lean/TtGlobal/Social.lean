import TtGlobal.Pit

/-!
# Trinidad and Tobago 2025: employer National Insurance (2200)

Source: National Insurance Act Chap. 32:01 (laws.gov.tt consolidation of 2025-01-08, the 1.x builder's copy
`world/B13-caribbean/tt/law/nis_32-01_118843.pdf`), Second Schedule Table A9 "Earnings Class and Contributions from
5th September 2016 (Based on a contribution rate of 13.2%)": columns "EMPLOYEE'S WEEKLY", "EMPLOYER'S WEEKLY", "TOTAL
WEEKLY"; in every class the employer's contribution is twice the employee's (I: 11.90 / 23.80 / 35.70 ... XVI:
138.10 / 276.20 / 414.30). The employer's charge is 2 x the 1.x model's employee NIS (`TtTax.person`, same weeks,
classes and insurable ages). Grade A.
-/

namespace TtGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon TtGlobal

/-- Employer NIS for one adult: twice the employee's Table A9 contribution (cents to dollars, down). -/
def employerNis (a : Adult) : Int := divR .down (2 * (TtTax.person a).nis) 100
def sscF : Family :=
  { name := "2200 NIS employer (Table A9)", covers := [.sscEmployer],
    run := fun _ g _ =>
      if g.entity == .company then
        [charge .sscEmployer "NIS (employer)" g.company.payroll id (fun _ => payrollAmount (fun w => employerNis { age := 40, wages := w }) g.company)
          (event := "payroll") (level := .social) (bearer := .entity) (statute := "NIA Chap. 32:01 Sched. 2 Table A9: employer = 2 x employee")]
      else
        (g.household.adults.zipIdx.filter fun (a, _) => employerNis a > 0).map fun (a, i) =>
          flatCharge .sscEmployer "NIS (employer)" (employerNis a) (event := s!"adult {i + 1}") (level := .social)
            (bearer := .employer) (statute := "NIA Chap. 32:01 Sched. 2 Table A9: employer = 2 x employee (13.2 %)") }

def families : List Family := [sscF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "company: Table A9 applied to the average wage per employee (age 40 assumed)"

#guard employerNis { age := 40, wages := 14040 } == 1237
#guard employerNis { age := 40, wages := 1000000 } == 14362
#guard employerNis { age := 70, wages := 50000 } == 0

end TtGlobal.Social
