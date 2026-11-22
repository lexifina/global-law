import DkGlobal.Pit

/-!
# DK 2025: employer social contributions (2200) and payroll taxes (3000)

Source: the dated statute quotes carried by the 1.x model's parameters (`lean/DKTax/Params.lean`, rounds 15: BEK nr 1621 af 12/12/2023 read from retsinformation.dk, `cmp20/nordic/dk/refs/web/atp_bek_2023_1621.xml`).
* BEK nr 1621 af 12/12/2023 § 2, stk. 1: "Det almindelige årsbidrag udgør 3.564 kr. (A-satsen)"; Bilag 1, månedslønnede "Mindst 117 (fuldtid) 99 198 297"; § 13: "træder i kraft den 1. januar 2024"
* ATP-loven § 15, stk. 6: "Arbejdsgiveren betaler 2/3 af bidraget og medlemmet 1/3" (1.x `atpEmployer := 2376` for 2025)
-/

namespace DkGlobal.Social
open TaxKernel TaxKernel.Global

/-- ATP, full-time (A-sats): BEK nr 1621 af 12/12/2023 § 2, stk. 1 "Det almindelige årsbidrag udgør 3.564 kr.
(A-satsen)" (in force 1.1.2024, unchanged for 2025); ATP-loven § 15, stk. 6 "Arbejdsgiveren betaler 2/3 af bidraget":
2.376 kr. a year, a fixed amount per full-time employee, not a share of the pay. -/
def atpEmployer (wages : Int) : Int := if 0 < wages then 2376 else 0

def contribs : List (String × (Int → Int) × Oecd × String) :=
  [("ATP-bidrag (arbejdsgiverandel)", atpEmployer, .sscEmployer, "ATP-loven § 15, stk. 6 (arbejdsgiveren betaler 2/3); BEK nr 1621 af 12/12/2023 § 2, stk. 1 (A-satsen 3.564 kr. årligt): 2.376 kr.")]

/-- On the household's wages: each adult, each contribution (borne by the employer). -/
def householdCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    contribs.map fun (nm, f, o, st) =>
      charge o nm a.wages id (fun x => f x) (event := s!"adult {i + 1}") (level := .social)
        (bearer := .employer) (statute := st)

/-- On a company's payroll, spread evenly over its employees. -/
def companyCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company || g.company.payroll ≤ 0 then [] else
  let n : Int := max 1 (g.company.employees : Int)
  let avg := g.company.payroll / n
  contribs.map fun (nm, f, o, st) =>
    charge o nm g.company.payroll id (fun _ => n * f avg) (event := "payroll") (level := .social)
      (statute := st)

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "2200/3000 employer contributions", covers := [.sscEmployer],
     run := fun args g prev =>
       householdCharges g ++ companyCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["DK 2200/3000: BEK nr 1621 af 12/12/2023 (A-sats for 2024, still in force in 2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["every wage earner taken as full-time monthly paid (A-sats); hours are not in the input. AUB, AES, Barsel.dk, the finansieringsbidrag and the lønsumsafgift (exempt sectors) not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees"] else [])

#guard atpEmployer 0 == 0
#guard atpEmployer 50000 == 2376
#guard atpEmployer 500000 == 2376

end DkGlobal.Social
