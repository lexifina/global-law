import MtGlobal.Pit

/-!
# MT 2025: Social family not reached (grade C)

* 2200 Employer social contributions and payroll taxes (Social Security Act Cap. 318 (Class 1, employer 10 %)): tried not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts); would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)


## 2200 Social security contribution, Class 1 (employer share) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), Malta, Social security contribution - Employers (taxId 429, situation 1.1.2025; data supplied by the member state; REST service, read 2026-11-21, held as `mt/law/tedb_ssc_employers_429_20250101.json`).
* rate 10 %; cap in monetary units 2 830.36 EUR (= 52 x 54.43)
* Class 1 table 2025: category C, basic weekly wage 221.79-544.28 EUR (born from 1.1.1962): 10 %; category D, from 544.29: 54.43 EUR a week (45.19 for persons born before 1.1.1962, wage from 451.92)
* Model: 10 % of annual wages up to 28 303 EUR (52 x 544.28), i.e. at most 2 830 EUR a year
* Hand check: wages 20 000: 2 000; wages 60 000: 2 830


## 2200 Class 1 maximum: 53,23 EUR is the 2024 rate (gap pass, grade C)
Source: Social Security Act (Amendment of Schedules) Regulations, 2025 (L.N. 10 of 2025, legislation.mt/eli/ln/2025/10/eng/pdf, fetched 2026-11-22, `mt/law/ln_2025_010.pdf`) reg. 1 (2) (a): the substituted Tenth Schedule is deemed in force from 1 January 2024; its Class One table: 10 % of a basic weekly wage above 532,29 EUR = 53,23 EUR (category D).
* Social Security Act (Amendment of Schedules) Regulations, 2025 (L.N. 10 of 2025, legislation.mt/eli/ln/2025/10/eng/pdf, fetched 2026-11-22, `mt/law/ln_2025_010.pdf`) reg. 1 (2) (a): the substituted Tenth Schedule is deemed in force from 1 January 2024; its Class One table: 10 % of a basic weekly wage above 532,29 EUR = 53,23 EUR (category D)
* so the 53,23 EUR of the malta-law consolidation is the 2024 maximum, read correctly (not an OCR error); no Tenth Schedule for 2025 is in the repository (none after L.N. 10 of 2025); the TEDB figure for 2025 (54,43 EUR a week, i.e. 10 % of 544,28) is kept, grade B
-/

namespace MtGlobal.Social
open TaxKernel TaxKernel.Global

def gxc0 : Contribution := { name := "Social security contribution, Class 1 (employer)", sched := Schedule.flat 1000, ceiling := 28303 }

def gxContribs : List (Contribution × Oecd × String) :=
  [(gxc0, .sscEmployer, "Social Security Act (Cap. 318) Class 1: employer 10 % of the basic weekly wage, at most 54.43 EUR a week (born from 1.1.1962; 2 830.36 EUR a year) (TEDB 2025)")]

/-- On the household's wages: each adult, each contribution (borne by the employer). -/
def gxHouseholdCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    gxContribs.map fun (c, o, st) =>
      charge o c.name a.wages id (fun x => c.amount x) (event := s!"adult {i + 1}") (level := .social)
        (bearer := .employer) (statute := st)

/-- On a company's payroll, spread evenly over its employees (ceilings per employee). -/
def gxCompanyCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company || g.company.payroll ≤ 0 then [] else
  let n : Int := max 1 (g.company.employees : Int)
  let avg := g.company.payroll / n
  gxContribs.map fun (c, o, st) =>
    charge o c.name g.company.payroll id (fun _ => n * c.amount avg) (event := "payroll") (level := .social)
      (statute := st)

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "2200 employer contributions (gap pass)", covers := [.sscEmployer],
     run := fun args g prev =>
       gxHouseholdCharges g ++ gxCompanyCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["MT 2200 gap pass: Social security contribution, Class 1 (employer share) (B, TEDB record 429, situation 1.1.2025 (still the version on 1.7.2025))", "MT gap pass: 2200 Class 1 maximum: 53,23 EUR is the 2024 rate"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages && a.age ≥ 63) then ["2200 MT Class 1: an employee born before 1.1.1962 has a weekly maximum of 45.19 EUR (taken at 54.43)"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["2200 (gap pass): company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard gxc0.amount 20000 == 2000
#guard gxc0.amount 60000 == 2830

end MtGlobal.Social
