import R4Common

/-!
# Rwanda 2025: corporate income tax (1200) and withholding (generated from `R4/specs/rw.json`)

Sources: Official Gazette texts (trilingual) in `cmp20/world/B10-anglophone-africa/rw/law/` (law027_2022.txt, law051_2023.txt, law014_2025.txt). Third pass: VAT Law 049/2023 and Excise Law 011/2025 fetched from apis.amategeko.gov.rw (documents-files/4497, /10055).

Law 051/2023 amending art. 48 (1): "Taxable Business profit is rounded down to the nearest 1000 Rwandan Francs and taxable at a rate of 28%" (the 2022 text said thirty percent). Law 014/2025 amends the capital gains rate (10 %) and gaming, not art. 48.

art. 60: "A withholding tax of fifteen percent (15%) of the total amount excluding value added tax … is levied on payments made by resident persons"; payments subject to it: "1° dividends …", interest, royalties, service fees (5 % for listed securities' dividends and interest).
-/

namespace RwGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Corporate income tax", sched := Schedule.flat 2800, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 2800000
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 280000
def whtR : Wht :=
  { name := "Withholding tax (art. 60)",
    rules := [{ kind := .dividend, rateBp := 1500, statute := "Law 027/2022 art. 60 (15 %)" },
              { kind := .interest, rateBp := 1500, statute := "Law 027/2022 art. 60 (15 %)" },
              { kind := .royalty, rateBp := 1500, statute := "Law 027/2022 art. 60 (15 %)" },
              { kind := .services, rateBp := 1500, statute := "Law 027/2022 art. 60 (15 %)" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Corporate income tax", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Law 027/2022 art. 48 (1) as amended by Law 051/2023 (28 %, rounded down to FRW 1 000)" (step := 1000)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["Law 027/2022 art. 48: reduced rates for newly listed companies and incentive regimes not applied"]

end RwGlobal
