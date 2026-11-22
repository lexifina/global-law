import SeGlobal.Pit

/-!
# SE 2025: Statlig inkomstskatt för juridiska personer (1200) and withholding on payments abroad

Source: Inkomstskattelag (1999:1229), data.riksdagen.se `sfs-1999-1229.text` (ändrad t.o.m. SFS 2026:1393; `se/law/isl_riksdagen.txt`); sha256 in `law/SHA256SUMS`.
* 65 kap. 10 §: "För juridiska personer är den statliga inkomstskatten 20,6 procent av den beskattningsbara inkomsten. Lag (2018:1206)."
* övergångsbestämmelser 2018:1206 p. 11: 21,4 procent for years beginning after 31 December 2018 but before 1 January 2021 (so 20,6 % for 2025)


## 1200 Kupongskatt: dividend (pass 8, grade A)
Source: Kupongskattelag (1970:624), data.riksdagen.se (`se/law/sfs-1970-624.txt`).
* 5 §: "Kupongskatt utgår med trettio procent av utdelningen."


## 1200 Withholding on interest, royalties, services: interest, royalty, services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Sweden, Corporate - Withholding taxes, accessed 2025-06-17 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* non-treaty: dividends 30 %, royalties 20,6 %; no tax on interest or service fees paid to non-residents
-/

namespace SeGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Statlig inkomstskatt för juridiska personer",   sched := Schedule.flat 2060 }

def citStatute : String := "Inkomstskattelagen (1999:1229) 65 kap. 10 § (20,6 procent), Lag (2018:1206)"

/-- kupongskattelag (1970:624) 5 § -/
def p8wht : Wht :=
  { name := "Kupongskatt", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 3000, statute := "kupongskattelag (1970:624) 5 §: 30 procent of the dividend" }] }

/-- inkomstskattelagen (deemed PE for royalties; no tax on interest and service fees) -/
def p8wht2 : Wht :=
  { name := "Withholding on interest, royalties, services", rules := [
    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "no Swedish tax on interest paid to non-resident corporations or individuals" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "no Swedish tax on service fees paid to non-residents" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2060, statute := "royalties to non-residents are taxed as income of a deemed permanent establishment at 20,6 %" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Statlig inkomstskatt för juridiska personer", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Kupongskatt (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) },
   { name := "1200 Withholding on interest, royalties, services (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["SE 1200: 65 kap. 10 § unchanged since Lag (2018:1206) (in force for years from 2021)", "SE 1200 withholding pass 8 (dividend): data.riksdagen.se, fetched 2026-11-21 (`se/law/sfs-1970-624.txt`) (grade A)", "SE 1200 withholding pass 8 (interest, royalty, services): 2025-06-17 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .dividend) then ["1200 withholding: the exemptions for EU/treaty parent companies (4 §) not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .royalty) then ["1200 withholding: royalties are assessed on the recipient (deemed PE), not withheld: booked as a withheld charge"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 20600
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 206000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 30000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 30000
#guard p8wht2.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 20600
#guard p8wht2.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 20600

end SeGlobal.Corporate
