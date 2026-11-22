import AuGlobal.Pit

/-!
# Australia 2025 (NSW): payroll tax (3000); no social security contributions
Payroll Tax Act 2007 (NSW), current version as captured by the Internet Archive on 14 February 2025 and 13 October 2025
(legislation.nsw.gov.au `view/whole/html/inforce/current/act-2007-021`; `au/law/au_nsw_pta2007_wb20250214.html`,
`..._wb20251013.html`): s. 8 (amount per Schedules 1 and 2); Schedule 1 cl. 1: "R is ... (g) 5.45% on and from 1 July
2022" and the threshold amount "(f) for the financial year commencing on 1 July 2020 and subsequent financial years--
$1,200,000"; the same text in both captures, so 2024-25 and 2025-26 are alike: 5.45 % of taxable wages above $1.2 m a
year (deducted in full; non-group employer). Session 12 (year in force): no split. Grade A.
Superannuation guarantee (11.5 % to 30 June 2025, 12 % from 1 July 2025) is paid to private funds: non-tax; Australia
levies no social security contributions.
-/

namespace AuGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "3000 payroll taxes", covers := [.payroll],
    run := fun _ g _ => if g.entity != .company then [] else
      [charge .payroll "Payroll tax (NSW, 5.45 %)" g.company.payroll (fun b => pos (b - 1200000)) (fun b => divR .down (545 * b) BP) (level := .state) (bearer := .entity) (statute := "Payroll Tax Act 2007 (NSW) s. 8, Sch. 1 cl. 1 (R 5.45 % from 1 July 2022; threshold $1,200,000 from 2020-21)")] }

def families : List Family := [fam0]

def absent : List Absent :=
  [{ oecd := .sscEmployer, why := "Australia levies no social security contributions; the superannuation guarantee goes to private funds (non-tax); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", entity := .company, household := { id := "t" }, company := { payroll := 2200000 } } []).map (·.due) == [54500]

end AuGlobal.Social
