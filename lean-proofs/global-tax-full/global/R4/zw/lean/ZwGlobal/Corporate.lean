import R4Common

/-!
# Zimbabwe 2025: corporate income tax (1200) and withholding (generated from `R4/specs/zw.json`)

No usable 2025 text for these headings: Finance Acts 2024 and Veritas pages are held; the Income Tax Act rates (Charging Schedule) and the VAT Act were not resolved in this pass. Second pass: Finance Act 2025 (No. 7 of 2025) s. 34 (quotes the 2025 wording of the VAT general rate); Finance Acts 2023, 2024, 2024 (No. 2). Finance Act [Chapter 23:04], Income Tax Act [Chapter 23:06] and VAT Act [Chapter 23:12] as updated by ZIMRA to 1 December 2024 (incorporating the Finance (No. 2) Act 7 of 2024 amendments from 1 January 2025), from zimra.co.zw/legislation/17-acts (`cmp20/global/R4/fetch/zw8/`, SHA256SUMS).

Finance Act s. 14 (2): "the income tax with which a person is chargeable in the year of assessment beginning on the 1st January, 2012 or any subsequent year of assessment shall be calculated ... (c) in the case of a company or a trust ... at the specified percentage"; Schedule to Chapter I, Part II (Current rates of income tax on taxable income, "Substituted by the FINANCE ACT - /2024"): "14(2)(c) Taxable income of company or trust 25" (the same 25 % in the 2024 table; 24 % appears only in the tables substituted by Act 10/2020). ZIMRA's corporate 'Tax rates' page: "Income of company or trust 14(2c) 25% ... Aids Levy: Rate is based on tax chargeable 3%".

s. 15: "The non-resident shareholders' tax ... shall be calculated (a) ... listed ... at the rate of 10%; (b) ... Victoria Falls Stock Exchange ... 5%; (c) in the case of any other dividend, at the rate of 15%"; s. 19 ("repealed and substituted by Act - /2024 w.e.f. 1st January, 2025"): "The non-residents' tax on fees ... shall be calculated at the rate of 15% of each dollar of the fees" (10 % for licensed investors); s. 21: "The non-residents' tax on royalties ... shall be calculated at the rate of 15% of each dollar of the royalty". Twelfth pass (kernel 2.3.0 grade-C withholding): interest 0 %: Income Tax Act [Chapter 23:06] s. 29 (non-residents' tax on interest) repealed by Act 5/2009 w.e.f. 30 September 2009: no withholding on interest paid to non-residents
-/

namespace ZwGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Corporate income tax", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2500249
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 250000
def whtR : Wht :=
  { name := "Non-residents' taxes",
    rules := [{ kind := .dividend, rateBp := 1500, statute := "Finance Act s. 15 (c) (15 %)" },
              { kind := .services, rateBp := 1500, statute := "Finance Act s. 19 (fees 15 %, from 1 Jan 2025)" },
              { kind := .royalty, rateBp := 1500, statute := "Finance Act s. 21 (15 %)" },
              { kind := .interest, rateBp := 0, statute := "Income Tax Act [Chapter 23:06] s. 29 (non-residents' tax on interest) repealed by Act 5/2009 w.e.f. 30 September 2009: no withholding on interest paid to non-residents" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 0
def corporate : Family :=
  { name := "1200 Corporate income tax", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Finance Act [Chapter 23:04] s. 14 (2) (c) and Schedule to Chapter I Part II (taxable income of a company or trust 25 %), ZIMRA consolidation to 1 December 2024 incl. the Finance (No. 2) Act 2024 changes from 1 January 2025; the Finance Act 2025 does not amend s. 14 (2) (c)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["the AIDS levy (3 % of the income tax chargeable, imposed outside the Finance Act) is not modelled: the effective rate would be 25,75 %", "licensed investors, mining, BOOT/BOT, special economic zones and export-manufacturing rates (s. 14 (2) (e)-(j), 14 (3)) are not modelled", "listed dividends are at 10 % (5 % on the Victoria Falls Stock Exchange): the company's dividend is taken as unlisted; interest paid to non-residents bears no non-residents' tax (not modelled as a charge)", "non-residents' tax on remittances (15 %, s. 20) on branch remittances not modelled"]

end ZwGlobal
