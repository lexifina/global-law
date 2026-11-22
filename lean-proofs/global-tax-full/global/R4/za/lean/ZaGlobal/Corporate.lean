import R4Common

/-!
# South Africa 2025: corporate income tax (1200) and withholding (generated from `R4/specs/za.json`)

Sources: SARS web pages saved locally (`cmp20/world/B02-g20/za/law/sars_intdiv.html`); the acts held by Global law are not reached (GL) in this pass. Amending acts fetched from sars.gov.za (redirects to wp-content/uploads/Legal/AmendActs/*.pdf), saved in `cmp20/global/R4/fetch/za8/` with SHA256SUMS and layout text.

Act 3 of 2026, Schedule I para 3: "The rate of tax referred to in section 2(1) to be levied in respect of the taxable income of a company (other than a public benefit organization, recreational club or small business funding entity referred to in paragraph 4 or a small business corporation referred to in paragraph 5), in respect of any year of assessment ending on or after 1 April 2025 is, subject to the provisions of paragraph 12, as follows: (a) 27 per cent of the taxable income of any company". Act 19 of 2023 para 3 (a) prints the same 27 % for years ending on or after 1 April 2023.

SARS dividends-tax page (budget update of 25 February 2026: no change; facts, paraphrased): 20 % dividends tax, withheld by the company paying the dividend. Withholding tax on interest and royalties (15 %) not read. Twelfth pass (kernel 2.3.0 grade-C withholding): interest 15 %: Income Tax Act 1962 s. 50A-50H (withholding tax on interest 15 %, final; SARS page fetched 2026-11-21, R4/fetch/za12, official secondary); royalty 15 %: Income Tax Act 1962 s. 49A-49H (withholding tax on royalties 15 %, final; SARS page fetched 2026-11-21, R4/fetch/za12, official secondary)
-/

namespace ZaGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Corporate income tax", sched := Schedule.flat 2700, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2700269
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 270000
def whtR : Wht :=
  { name := "Dividends tax",
    rules := [{ kind := .dividend, rateBp := 2000, statute := "ITA 1962 s. 64E (20 %; SARS, official secondary)" },
              { kind := .interest, rateBp := 1500, statute := "Income Tax Act 1962 s. 50A-50H (withholding tax on interest 15 %, final; SARS page fetched 2026-11-21, R4/fetch/za12, official secondary)" },
              { kind := .royalty, rateBp := 1500, statute := "Income Tax Act 1962 s. 49A-49H (withholding tax on royalties 15 %, final; SARS page fetched 2026-11-21, R4/fetch/za12, official secondary)" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 200000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Corporate income tax", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Income Tax Act 1962 s. 5 (2); Rates and Monetary Amounts and Amendment of Revenue Laws Act 3 of 2026 Schedule I para 3 (a) (27 %, years of assessment ending on or after 1 April 2025); Act 19 of 2023 Schedule para 3 (a) (27 %, years ending on or after 1 April 2023)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["small business corporations (para 5, 0-27 % bands), gold mining formula and long-term insurers' funds (para 3 (b)-(d)) not modelled; assessed losses are carried forward under s. 20 (80 % limit above R1 million from 2023, not modelled)", "South Africa: dividends tax, withholding tax on interest and on royalties (SARS pages, official secondary); services left C (taxed by assessment)"]

end ZaGlobal
