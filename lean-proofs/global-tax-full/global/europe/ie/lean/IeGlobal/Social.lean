import IeGlobal.Pit

/-!
# IE 2025: employer social contributions (2200) and payroll taxes (3000)

Source: Social Welfare Consolidation Act 2005, revised act (Law Reform Commission, updated to 21 January 2026, `cmp20/anglo/ie/refs/swca_rev.pdf`), Social Welfare (Miscellaneous Provisions) Act 2024 (`swmp2024.txt`) and Social Welfare Act 2024 (`swa2024.txt`), irishstatutebook.ie, kept by the 1.x model.
* SWCA s. 13 (2) (d) (revised): "a contribution shall be payable by the employed contributor's employer— (i) at the rate of [..] per cent of the amount of the reckonable earnings in that week to which that payment relates where those reckonable earnings do not exceed €527 ... and (ii) at the rate of [..] per cent ... where those reckonable earnings exceed €527"
* SW(MP)A 2024 s. 3 (1): provisions amended "on and from 1 October 2024" by column (4); (2): "on and from 1 October 2025" by column (5); Table amendments 2-3 (s. 13 (2) (d) (i), (ii)): "7.8 per cent" -> "7.9 per cent" -> "8 per cent"; "10.05 per cent" -> "10.15 per cent" -> "10.25 per cent"
* Social Welfare Act 2024: "by the substitution, in subparagraph (i), of '€527' for '€496', and (b) ... in subparagraph (ii), of '€527' for '€496'"
-/

namespace IeGlobal.Social
open TaxKernel TaxKernel.Global

/-- Employer PRSI, SWCA 2005 s. 13 (2) (d): a contribution "at the rate of [x] per cent of the amount of the reckonable
earnings in that week ... where those reckonable earnings do not exceed €527" and at the higher rate "where those
reckonable earnings exceed €527": the whole week's pay at one rate (a cliff, not a band). Rates for 2025 from the
Social Welfare (Miscellaneous Provisions) Act 2024 s. 3 and Table: 7.9 % / 10.15 % on and from 1 October 2024 (col. (4)),
8 % / 10.25 % on and from 1 October 2025 (col. (5)). Threshold €527 from 1 January 2025 (Social Welfare Act 2024 s. 2 (1), in operation 1.1.2025 by s. 2 (2):
"€527" for "€496"). Year convention of the 1.x model (IeTax.Params `payWeeksAt41 = 39`): 52 equal weekly payments, the
first 39 at the January-September rate. Annual pay `w` (euros): weekly pay w / 52 exceeds €527 iff w > 52 × 527. -/
def prsiThresholdYear : Int := 52 * 527
def prsiEmployer (w : Int) : Int :=
  if w ≤ 0 then 0 else
  let low := decide (w ≤ prsiThresholdYear)
  let w1 := w * 39 / 52
  let w2 := w - w1
  (w1 * (if low then 790 else 1015) + w2 * (if low then 800 else 1025)) / 10000

def contribs : List (String × (Int → Int) × Oecd × String) :=
  [("Employer PRSI (Class A)", prsiEmployer, .sscEmployer, "Social Welfare Consolidation Act 2005 s. 13 (2) (d) (i)-(ii), as amended by SW(MP)A 2024 s. 3 and Table cols. (4)-(5): 7.9 % / 10.15 % to 30.9.2025, 8 % / 10.25 % from 1.10.2025, the whole week's pay at one rate; weekly threshold €527 (Social Welfare Act 2024)")]

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

def notes : List String := ["IE 2200/3000: 2025: SW(MP)A 2024 cols. (4)-(5); Social Welfare Act 2024 threshold"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["National Training Fund levy (1 %, collected with employer PRSI; NTF Act 2000 s. 2 not read) and the 2025 weekly pay pattern (evenly paid, 39 weeks at the January-September rate) taken by convention"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees"] else [])

#guard prsiEmployer 20000 == 1585
#guard prsiEmployer 27404 == 2171
#guard prsiEmployer 27405 == 2788
#guard prsiEmployer 60000 == 6105

end IeGlobal.Social
