import ThGlobal.Pit

/-!
# Thailand 2025: employer social security (2200)
Social Security Act B.E. 2533 s. 46-47 and the Ministerial Regulation (B): employer 5 % on wages between 1,650 and 15,000 baht
a month (cap 180,000 a year). Workmen's Compensation Fund (0.2-1 % by risk class): not modelled.
Gap-closing session: 3000 is a cited absence. The Workmen's Compensation Act B.E. 2537 (read in lexifina/thailand-law
`workmen-compensation`, official source searchlaw.ocs.go.th; texts in force to 2018-12-09, amended by Act No. 2 B.E. 2561)
s. 44 makes employers pay contributions (เงินสมทบ) to the Workmen's Compensation Fund, and s. 45 lets the Ministry of Labour
set the rate "not above 5 % of the wages paid each year" by the accident statistics of each type of business. A
compulsory payment to general government that confers an entitlement to employment-injury benefits is a social security
contribution (OECD Interpretative Guide §40-41: 2200), not a payroll tax (3000). The rate notice was not read: the WCF
stays unmodelled under 2200. No payroll tax (3000) is levied.
-/

namespace ThGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "Social security (employer 5 %)" a.wages (fun w => min (pos w) 180000) (fun b => divR .down (500 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Social Security Act B.E. 2533 s. 46-47; MR B.E. 2545")) }

def families : List Family := [fam0]

def absent : List Absent :=
  [{ oecd := .payroll, why := "No payroll tax (3000) in Thailand. The Workmen's Compensation Fund contribution (Workmen's Compensation Act B.E. 2537 ss. 44-45, read in lexifina/thailand-law) is a social security contribution (OECD Interpretative Guide §40-41: 2200), not a payroll tax; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 600000 }] } } []).map (·.due) == [9000]

end ThGlobal.Social
