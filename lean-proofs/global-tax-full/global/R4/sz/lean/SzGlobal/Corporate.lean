import R4Common

/-!
# Eswatini 2025: corporate income tax (1200) and withholding (generated from `R4/specs/sz.json`)

No usable 2025 text for these headings: the Income Tax Order 1975 extraction shows only individual tables; the company rate and the VAT Act 2011 text were not located. Fetched from ers.org.sz (`cmp20/global/R4/fetch/sz8/`, SHA256SUMS): VAT Act 2011, VAT Regulations, VAT (Rates) (Amendment) Regulations 2018 (OCR), VAT (Amendment) Act 2022 (OCR), LN 130 of 2025 (OCR), ERS pages 'Rates and thresholds', 'Withholding', 'VAT'. Pass 9 (excise): the Eswatini Revenue Service's Excise page (ers.org.sz/CustomExcise/Excisepage, saved in `R4/fetch/sz8/CustomExcise_Excisepage.html`) states that excise is charged at the rates of the SACU tariff schedule and links to SARS's 'Schedules to the Customs and Excise Act'; the 2025/2026 SACU rates are those read for ZA (Act 3 of 2026 Sch. II, `R4/fetch/za8/`).

ERS 'Rates and thresholds' (live 2026-11-21; facts restated): companies pay 27,5 % of taxable income, since 1 July 2013. The Income Tax Order 1975 held prints only individual tables; the Income Tax (Amendment) Act 2023 (scanned) was not read. Grade B.

ERS 'Withholding' (live 2026-11-21): "Every person who makes any payment of royalty or management fee or both to a person not ordinarily resident in Swaziland is required to withhold tax. The rate of tax is fifteen percent of the gross amount of any management charge. The tax is final"; "The non-resident person is liable to withholding tax at the rate of fifteen percent on the gross amount of any payment derived by the non-resident under a Swaziland source services contract"; "The debtor ... shall withhold and remit to ERS tax equal to ten per cent of the interest that accrues to or in favour of the non-resident." Twelfth pass (kernel 2.3.0 grade-C withholding): dividend 15 %: Income Tax Order 1975 s. 21 (2) (non-resident shareholders tax 15 %; the 12,5 % SACU proviso deleted by the Income Tax (Amendment) Act 2023 s. 10)
-/

namespace SzGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Corporate income tax", sched := Schedule.flat 2750, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2750274
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 275000
def whtR : Wht :=
  { name := "Withholding on payments to non-residents",
    rules := [{ kind := .royalty, rateBp := 1500, statute := "ITO 1975 (ERS guide): royalties 15 %" },
              { kind := .services, rateBp := 1500, statute := "ITO 1975 (ERS guide): management fees and services contracts 15 %" },
              { kind := .interest, rateBp := 1000, statute := "ITO 1975 (ERS guide): non-resident interest 10 %" },
              { kind := .dividend, rateBp := 1500, statute := "Income Tax Order 1975 s. 21 (2) (non-resident shareholders tax 15 %; the 12,5 % SACU proviso deleted by the Income Tax (Amendment) Act 2023 s. 10)" }] }
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 100000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Corporate income tax", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Income Tax Order 1975 (company rate 27,5 % since 1 July 2013), per the Eswatini Revenue Service guide (official secondary)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["the guide's sentence is undated beyond 'since 1 July 2013'; no later change found on the ERS pages", "non-resident shareholders tax on dividends: the guide's rate table is garbled (SACU / outside SACU rows) and the prose gives no rate: not applied"]

end SzGlobal
