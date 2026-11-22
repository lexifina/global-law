import VnGlobal.Pit

/-!
# Viet Nam 2025: employer social, health and unemployment insurance (2200)
(B.) Luật BHXH 41/2024 (from 2025-07-01) art. 33-34: employer 17.5 %; Luật BHYT: 3 %; Luật Việc làm: 1 %; base capped at 20 ×
the reference level (2,340,000: 46.8 m a month, 561.6 m a year; the unemployment cap is 20 × the regional minimum wage, taken
as the same here). Trade union fee 2 % (Law 50/2024) is not a tax (paid to the union).
Gap-closing session: 3000 is a cited absence and the trade union fee is out of scope. Luật Công đoàn 50/2024/QH15 (read in
lexifina/vietnam-law `luat/2024/50-2024-qh15`, official source vbpl.vn; in force 1 July 2025, art. 37, replacing Law
12/2012/QH13) art. 29 (1) (b): kinh phí công đoàn, 2 % of the wage fund on which social insurance is paid, is one of "the
financial sources of the trade union" (nguồn tài chính công đoàn). A levy paid to a trade union is excluded from taxes even
where it is compulsory (OECD Interpretative Guide §6); Law 12/2012 (to 30 June 2025, not read here) had the same 2 %. No
payroll tax (3000) is levied.
-/

namespace VnGlobal.Social
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "2200 employer social contributions", covers := [.sscEmployer],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, k) =>
        charge .sscEmployer "BHXH + BHYT + BHTN (employer 21.5 %)" a.wages (fun w => min (pos w) 561600000) (fun b => divR .down (2150 * b) BP) (event := s!"adult {k + 1}") (level := .social) (bearer := .employer) (statute := "Luật BHXH 41/2024 art. 33-34; Luật BHYT art. 13; Luật Việc làm 38/2013 art. 57")) }

def families : List Family := [fam0]

def absent : List Absent :=
  [{ oecd := .payroll, why := "No payroll tax (3000) in Viet Nam. The trade union fee (kinh phí công đoàn, 2 % of the social-insurance wage fund; Luật Công đoàn 50/2024/QH15 art. 29 (1) (b), read in lexifina/vietnam-law) is a financial source of the trade union, not general government: not a tax (OECD Interpretative Guide §6); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (fam0.run [] { id := "t", household := { id := "t", adults := [{ wages := 100000000 }] } } []).map (·.due) == [21500000]

end VnGlobal.Social
