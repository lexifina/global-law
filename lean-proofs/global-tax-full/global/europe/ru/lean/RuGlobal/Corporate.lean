import RuGlobal.Pit

/-!
# RU 2025: Налог на прибыль организаций (1200) and withholding on payments abroad

Source: Федеральный закон от 12.07.2024 № 176-ФЗ (text kept by the 1.x model, `ru/law/fz176_2024_clean.txt`), which restates НК РФ ст. 284 п. 1 from 1 January 2025; sha256 in `law/SHA256SUMS`.
* 176-ФЗ п. 50 (ст. 284): "1. Налоговая ставка устанавливается в размере 25 процентов, если иное не установлено настоящей статьей. При этом: сумма налога, исчисленная по налоговой ставке в размере 7 процентов (8 процентов в 2025 - 2030 годах), зачисляется в федеральный бюджет"


## 1200 Налог у источника (иностранные организации): dividend, interest, royalty (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Russian Federation, Corporate - Withholding taxes, accessed 2021-09-24 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* non-treaty rates: dividends 15 %, interest 20 %, royalties 20 %


## 1200 withholding still grade C (pass 9)
* НК РФ ст. 309 п. 2 (legalacts.ru mirror, ред. 04.08.2026): income of a foreign organisation from works and services in Russia not listed in п. 1 is not taxed at source; п. 1 пп. 9.4 taxes services to a related party (ст. 105.1), its rate and date of entry not read
* would unlock: the rate for ст. 309 п. 1 пп. 9.4 (ст. 284) and a related-party flag on the payment (stake ≥ 25 %); then a 0 rule for the rest


## 1200 withholding on payments to foreign organisations (pass 15: the 2025 redaction)
Source: НК РФ ст. 284 and 309, legalacts.ru, ред. от 28.12.2024 с изм. от 21.01.2025 (Internet Archive 2025-08-14: `ru/law/nkrf284_legalacts_wb20250814.txt`, `ru/law/nkrf309_legalacts_wb20250814.txt`); 176-ФЗ of 12.07.2024 ст. 2 п. 50 ж) and ст. 7 ч. 2 (`ru/law/fz176_2024_clean.txt`: п. 2 пп. 1 raised from 20 to 25 % from 1 January 2025).
* ст. 309 п. 1 lists the Russian-source income of a foreign organisation taxed at source (dividends пп. 1, interest пп. 3, royalties пп. 4, services in Russia to a related party пп. 9.4, the buyer's place of activity deciding where a service is rendered); п. 2: other sales, works and services in Russia are not taxed at source
* ст. 284 п. 2 пп. 1: 25 % on that income unless another rate applies (20 % until 2024: the pass-8 rows, from a 2021 secondary page, used 20 %); пп. 4: 15 % on the пп. 9.4 services; п. 3 пп. 3: dividends to a foreign organisation 15 %
* ст. 105.1 п. 2 пп. 1: organisations are related where one holds more than 25 % of the other (the payment's stake; other relations not seen)
* ст. 284 п. 1 (same capture): 25 %, of which 8 % to the federal budget in 2025-2030 and 17 % to the regions: the CIT entry is now read in the consolidated text (grade A)
* Hand check: interest of 100 000 to a foreign company: 25 000; services of 100 000 to a parent holding 30 %: 15 000; to an unrelated provider: 0


## 1200 НДФЛ withheld on payments to non-resident individuals (pass 18, grade A)
Source: НК РФ ст. 224 (ред. от 28.12.2024, с изм. от 21.01.2025; legalacts.ru, Internet Archive 2025-02-19: `ru/law/nkrf224_legalacts_wb20250219.*`) and ст. 208 (ред. от 31.07.2025; Internet Archive 2025-09-18: `ru/law/nkrf208_legalacts_wb20250918.*`).
* ст. 224 п. 3: 30 % on all income of an individual who is not a tax resident, except (among others) dividends of Russian organisations (15 %), interest on deposits with banks in Russia (15 %) and the employment cases of п. 3.1
* ст. 208 п. 1: Russian-source income includes dividends and interest from a Russian organisation (пп. 1), royalties for use in Russia (пп. 3) and services performed in Russia (пп. 6); a service performed abroad is foreign-source (п. 3 пп. 6), and the place is not an input, so services stay grade C
* Hand check: interest of 100 000 to a non-resident individual: 30 000; dividends of 100 000: 15 000
-/

namespace RuGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Налог на прибыль организаций",   sched := Schedule.flat 2500 }

def citStatute : String := "НК РФ ст. 284 п. 1 (25 %; 8 % федеральный бюджет в 2025-2030 годах) в редакции Федерального закона от 12.07.2024 № 176-ФЗ"

/-- p15 RU: НК РФ ст. 284 п. 2-3, ст. 309, ст. 310 in the 2025 redaction (ред. от 28.12.2024); payments to foreign organisations only (ст. 246, 309); p18 RU: payments to non-resident individuals: НДФЛ at source (ст. 224 п. 3) -/
def p8wht : Wht :=
  { name := "Налог у источника (иностранные организации)", rules := [
    { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 1500, statute := "НК РФ ст. 284 п. 3 пп. 3, ст. 309 п. 1 пп. 1, ст. 310: dividends to a foreign organisation 15 %" },   { kind := .interest, toCompany := some true, minStakeBp := 0, rateBp := 2500, statute := "НК РФ ст. 284 п. 2 пп. 1 (25 % from 1.1.2025: 176-ФЗ ст. 2 п. 50 ж), ст. 309 п. 1 пп. 3: interest 25 %" },   { kind := .royalty, toCompany := some true, minStakeBp := 0, rateBp := 2500, statute := "НК РФ ст. 284 п. 2 пп. 1 (25 % from 1.1.2025: 176-ФЗ ст. 2 п. 50 ж), ст. 309 п. 1 пп. 4: royalties 25 %" },   { kind := .services, toCompany := some true, minStakeBp := 2501, rateBp := 1500, statute := "НК РФ ст. 309 п. 1 пп. 9.4, ст. 105.1 п. 2 пп. 1 (a stake of more than 25 %), ст. 284 п. 2 пп. 4: services in Russia to a related party 15 %" },   { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "НК РФ ст. 309 п. 2: other works and services of a foreign organisation in Russia are not taxed at source" },   { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 1500, statute := "НК РФ ст. 224 п. 3 абз. 2, ст. 208 п. 1 пп. 1: dividends from a Russian organisation to a non-resident individual 15 %" },   { kind := .interest, toCompany := some false, minStakeBp := 0, rateBp := 3000, statute := "НК РФ ст. 224 п. 3, ст. 208 п. 1 пп. 1: interest from a Russian organisation to a non-resident individual 30 %" },   { kind := .royalty, toCompany := some false, minStakeBp := 0, rateBp := 3000, statute := "НК РФ ст. 224 п. 3, ст. 208 п. 1 пп. 3: royalties for use in Russia to a non-resident individual 30 %" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Налог на прибыль организаций", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Налог у источника (иностранные организации) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["RU 1200: 176-ФЗ amending text (the consolidated НК РФ not read)", "RU 1200 withholding: НК РФ ст. 284, 309, 310 in the 2025 redaction (ред. от 28.12.2024; interest and royalties 25 % from 1.1.2025, dividends 15 %, related-party services 15 %, other services 0) (grade A, pass 15)", "RU 1200 pass 18: НДФЛ at source on payments to non-resident individuals (ст. 224 п. 3, 2025 redaction): dividends 15 %, interest and royalties 30 % (grade A); services grade C (place of performance)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => !p.toCompany && p.kind == .services) then ["1200 НДФЛ on services of a non-resident individual: taxed at 30 % only if performed in Russia (ст. 208 п. 1 пп. 6, п. 3 пп. 6); the place is not an input (grade C)"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => !p.toCompany && p.kind == .interest) then ["1200 НДФЛ on interest to a non-resident individual taken at 30 %: interest on deposits with a Russian bank is 15 % (ст. 224 п. 3)"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 25000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 250000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 2501 } == 15000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 2500 } == 0
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 15000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 30000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 30000
#guard (p8wht.ruleFor { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 }).isNone

end RuGlobal.Corporate
