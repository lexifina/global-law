import CaGlobal.Pit

/-!
# Canada 2025 (Ontario): employer CPP and EI (2200), Ontario Employer Health Tax (3000)

Sources (Justice Laws, current consolidations; Ontario e-Laws): Canada Pension Plan (C-8), Employment Insurance Act
(E-5.6), Employer Health Tax Act R.S.O. 1990 c. E.11 (consolidation from 2025-11-27 with dated provisions).
* **CPP s. 9 (1)**: the employer's base contribution is "the contribution rate for employers for the year" times the
  same earnings as the employee's (s. 8), the employer and employee rates being equal; s. 9 (1.1), (1.2) the first and
  second additional contributions likewise. The 1.x model computes each employee's CPP (`cppBaseCents`,
  `cppEnhancedCents`): the employer pays the same amounts.
* **EI Act s. 68**: "an employer shall pay a premium equal to 1.4 times the employees' premiums" (1.x `eiCents`).
* **EHT Act s. 2 (2) (c)**: "a rate of 1.95 per cent" where Ontario remuneration exceeds $400,000; the exemption of an
  eligible employer is "$1,000,000 for a year in the nine-year period consisting of 2020 to 2028" (eligible: payroll
  up to $5,000,000). Below $1,000,000 nothing is due, so for a company the tax is 1.95 % × (payroll − exemption).
  For a household's wages the employer's payroll is unknown: not charged (listed).
-/

namespace CaGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon CaGlobal

/-- Employer CPP and EI per adult, from the 1.x model's own per-person lines (cents → dollars, down). -/
def employerOf (p : Lean.Json) : Int × Int :=
  (divR .down (intField p "cppBaseCents" + intField p "cppEnhancedCents") 100, divR .down (14 * intField p "eiCents") 1000)

def personsOf (j : Lean.Json) : List Lean.Json :=
  match j.getObjVal? "detail" with
  | .ok d => (arrField d "persons").toList
  | _ => []

def sscF : Family :=
  { name := "2200 employer CPP and EI", covers := [.sscEmployer],
    run := fun args g _ =>
      if g.entity == .company then [] else
      let ps := personsOf (base.pit args g.household)
      (ps.zipIdx.filter fun (p, _) => (employerOf p).1 + (employerOf p).2 > 0).flatMap fun (p, i) =>
        [flatCharge .sscEmployer "CPP employer contribution" (employerOf p).1 (event := s!"adult {i + 1}") (level := .social)
           (bearer := .employer) (statute := "Canada Pension Plan s. 9 (1), (1.1), (1.2): equal to the employee's (1.x model)"),
         flatCharge .sscEmployer "EI employer premium" (employerOf p).2 (event := s!"adult {i + 1}") (level := .social)
           (bearer := .employer) (statute := "Employment Insurance Act s. 68: 1.4 × the employee's premium (1.x model)")] }

/-- EHT on a company's Ontario payroll: 1.95 % above the $1,000,000 exemption of an eligible employer (payroll up to
$5,000,000); a larger employer has no exemption. -/
def eht (payroll : Int) : Int :=
  divR .down (195 * pos (payroll - (if payroll ≤ 5000000 then 1000000 else 0))) BP

def ehtF : Family :=
  { name := "3000 Ontario Employer Health Tax", covers := [.payroll],
    run := fun _ g _ => if g.entity != .company then [] else
      [charge .payroll "Employer Health Tax (Ontario)" g.company.payroll id eht (event := "payroll") (level := .state)
        (statute := "EHT Act s. 2 (2) (c) 1.95 %; exemption $1,000,000 (2020-2028)")] }

def families : List Family := [sscF, ehtF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company && g.company.payroll > 0) "company: employer CPP/EI on its payroll need per-employee earnings: not computed (household lines carry them)"
  ++ when (g.entity != .company && g.household.adults.any (·.wages > 0)) "Ontario EHT on a household's wages: the employer's total payroll is not known: not charged; WSIB premiums not modelled"

#guard eht 900000 == 0
#guard eht 3000000 == 39000
#guard eht 6000000 == 117000
#guard employerOf (Lean.Json.mkObj [("cppBaseCents", Lean.toJson (335610 : Int)), ("cppEnhancedCents", Lean.toJson (102600 : Int)), ("eiCents", Lean.toJson (107748 : Int))]) == (4382, 1508)

end CaGlobal.Social
