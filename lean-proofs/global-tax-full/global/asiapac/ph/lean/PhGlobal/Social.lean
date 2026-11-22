import PhGlobal.Pit

/-!
# Philippines 2025: employer SSS and PhilHealth (2200); Pag-IBIG and the SSS Provident Fund are not taxes
Gap-closing session (texts read in lexifina/philippines-law, official source elibrary.judiciary.gov.ph):
* **RA 11199 s. 4 (a) (9)** (showdocs/2/86333): the schedule's 2025 row: contribution rate 15 %, employer 10 %, employee 5 %,
  monthly salary credit (MSC) 5,000 minimum, 35,000 maximum; members below the minimum or above the maximum pay on the
  minimum or maximum MSC. **s. 4 (a) (2)**: a Provident Fund "based on ... (ii) monthly salary credit in excess of Twenty
  thousand pesos (P20,000.00) up to the prescribed maximum": individual accounts with their earnings. Under the OECD
  Interpretative Guide §43 provident funds are not social security contributions: the employer's 10 % is booked on the MSC
  from 5,000 to 20,000 a month (60,000 to 240,000 a year); the part above 20,000 is not a tax. **This corrects the earlier
  model**, which booked 10 % on wages up to 35,000 a month. The MSC brackets are not rounded (wages taken as the MSC).
* **RA 11223 s. 10** (PhilHealth: 5 % in 2024-2025, employer half, income ceiling 100,000 a month): not read (B).
* **RA 9679 ss. 5, 7, 8** (showdocs/2/19155): the Home Development Mutual Fund (Pag-IBIG) is "a mutual provident savings
  system ... supported by matching mandatory contributions of their respective employers", members withdraw "the total
  accumulated value" after 20 years: a provident fund, not a tax (OECD guide §43). **Removed from 2200** (it was booked at
  2 % of wages up to 10,000 a month).
-/

namespace PhGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "PhilHealth (employer 2.5 %)" a.wages (fun w => min (pos w) 1200000) (fun b => divR .down (250 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "RA 11223 s. 10")) }

/-- RA 11199 s. 4 (a) (9) (2025: employer 10 % of the MSC, MSC 5,000-35,000) and s. 4 (a) (2) (the MSC above 20,000 goes to
the Provident Fund: OECD guide §43, not a tax): 10 % of the yearly wages clamped to [60,000, 240,000]. -/
def sssF : Family :=
  { name := "2200 SSS employer contribution (social security part)", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "SSS (employer 10 % of the MSC from 5,000 to 20,000 a month)" a.wages (fun w => max 60000 (min w 240000))
          (fun b => divR .down (1000 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer)
          (statute := "RA 11199 s. 4 (a) (9) (2025 row: employer 10 %, MSC 5,000-35,000) and s. 4 (a) (2) (MSC above 20,000: Provident Fund, not a tax)") }

def families : List Family := [fam0, sssF]

def absent : List Absent :=
  [{ oecd := .payroll, why := "No payroll tax; grade B" }]

def notes : List String := ["Pag-IBIG (HDMF; RA 9679 ss. 5, 7, 8: a mutual provident savings system, accumulated value withdrawable) and the SSS Provident Fund part of the contribution (RA 11199 s. 4 (a) (2): MSC above 20,000) are provident funds: not taxes (OECD Interpretative Guide §43)"]

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 600000 }] } } []).map (·.due) == [15000]
#guard (sssF.run [] { id := "t", household := { id := "t", adults := [{ wages := 600000 }] } } []).map (·.due) == [24000]
#guard (sssF.run [] { id := "t", household := { id := "t", adults := [{ wages := 30000 }] } } []).map (·.due) == [6000]
#guard (sssF.run [] { id := "t", household := { id := "t", adults := [{ wages := 150000 }] } } []).map (·.due) == [15000]

end PhGlobal.Social
