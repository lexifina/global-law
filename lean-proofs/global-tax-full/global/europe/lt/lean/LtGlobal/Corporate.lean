import LtGlobal.Pit

/-!
# LT 2025: Pelno mokestis (1200) and withholding on payments abroad

Source: Pelno mokesčio įstatymas, e-seimas consolidated edition "nuo 2025-01-01" (TAIS.157066) as captured by the Internet Archive on 2025-06-16 (`lt/law/pmi_ed20250101_wb.html`); sha256 in `law/SHA256SUMS`.
* 5 str. 1 d. 1 p.: "Lietuvos vieneto, nuolatinių buveinių apmokestinamasis pelnas apmokestinamas taikant 16 procentų mokesčio tarifą, jeigu šis Įstatymas nenustato ko kita"
* 5 str. 2 d.: entities with at most 10 employees and revenue up to 300 000 eurų: "pirmojo mokestinio laikotarpio apmokestinamasis pelnas apmokestinamas taikant 0 procentų ..., kitų mokestinių laikotarpių ... 6 procentų mokesčio tarifą"


## 1200 withholding on payments abroad (pass 6)
Source: PwC Worldwide Tax Summaries, Lithuania, Corporate - Withholding taxes, accessed 2025-06-17 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* WHT on a foreign entity without PE: interest 10 %; dividends 16 % (from 1.1.2025); royalties 10 %; 0 % under domestic exemptions (participation, EU interest)


## 1200 Pelno mokestis prie šaltinio (paslaugos): services (pass 8, grade A)
Source: Pelno mokesčio įstatymas, e-TAR redakcija nuo 2025-01-01 (`lt/law/pmi_ed20250101_wb.txt`).
* 4 str. 4 d.: the Lithuanian-source income of a foreign entity not through a PE is listed in items 1-7 (interest; distributed profit; royalties; real estate; copyright compensation; performers and sport; supervisory board fees)
* 5 str. 2 d. 2 p.: items 3 and 5 at 10 %, items 4, 6 and 7 at 16 %
-/

namespace LtGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Pelno mokestis",   sched := Schedule.flat 1600 }

def citStatute : String := "Pelno mokesčio įstatymas (IX-675) 5 str. 1 d. 1 p. (16 %), as amended by XIV-2774 (in force 1.1.2025, for 2025 profit only: 17 % from 2026)"

/-- Pelno mokesčio įstatymas 37 str. (distributed profits 16 % from 1.1.2025; interest and royalties 10 %) -/
def p6wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1600, statute := "Pelno mokesčio įstatymas 37 str. (distributed profits 16 % from 1.1.2025; interest and royalties 10 %)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "Pelno mokesčio įstatymas 37 str. (distributed profits 16 % from 1.1.2025; interest and royalties 10 %)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "Pelno mokesčio įstatymas 37 str. (distributed profits 16 % from 1.1.2025; interest and royalties 10 %)" }] }

/-- Pelno mokesčio įstatymas 4 str. 4 d., 5 str. 2 d. 2 p. -/
def p8wht2 : Wht :=
  { name := "Pelno mokestis prie šaltinio (paslaugos)", rules := [
    { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "PMĮ 4 str. 4 d. (Lithuanian-source income of foreign entities without a PE: interest, distributed profit, royalties, real estate, copyright compensation, performers and sport, supervisory board): service fees not listed, none" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Pelno mokestis", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 withholding on payments abroad (pass 6)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p6wht.charges g.company else []) },
   { name := "1200 Pelno mokestis prie šaltinio (paslaugos) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["LT 1200: e-seimas edition from 2025-01-01", "LT 1200 withholding: PwC WWTS Corporate - Withholding taxes, 2025-06-17 (Wayback capture) (grade B)", "LT 1200 withholding pass 8 (services): redakcija nuo 2025-01-01 (`lt/law/pmi_ed20250101_wb.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company then ["1200 withholding: EU parent-subsidiary / interest-royalty exemptions and the higher tax-haven rates not modelled"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 16000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 160000
#guard p6wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 16000
#guard p6wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p6wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0

end LtGlobal.Corporate
