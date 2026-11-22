import R4Common

/-!
# Sierra Leone 2025: VAT (5111) and excises (5121) (generated from `R4/specs/sl.json` by `R4/tools/gen_country.py`)

Sources: Income Tax Act 2000 as amended to the Finance Act 2017 (`cmp20/world/B10-anglophone-africa/sl/law/Income_Tax_Act_2000_as_amended_to_Finance_Act_2017_1_83760e046c.txt`). Finance Acts 2020 (OCR), 2023, 2024 and 2025 (`cmp20/world/B10-anglophone-africa/sl/law/`). GST Act 2009 compilation to 2016 (nra.gov.sl/tax-laws, `cmp20/global/R4/fetch/sl8/`, SHA256SUMS); Finance Acts 2017-2025 checked for s. 14.

s. 14 (3): "The rate of GST applicable to a taxable supply or import is (a) if the supply or import is zero-rated under the First Schedule, zero per cent; (b) in any other case, 15 per cent." Second Schedule: "4. Supply: Water. 5. Supply: Printed matter (books and newspapers). 6. Supply: Education services 7. Supply: Medical services and pharmaceuticals. 8. Supply: Transportation of passengers 9. Supply: Crude oil and hydrocarbon products. 10. Supply: Financial services." The Finance Acts 2017-2025 amend ss. 2, 6, 8, 15, 19, 31, 34, 37, 58, 90, 99 and the Second Schedule (additions such as teaching materials and local vegetable oil), not s. 14.

FA 2024 s. 4 (b), heading 2204 (wine of fresh grapes), alcohol content '>10 but <20': "Le6.30 per litre" local, "Le12 per litre" import; '<10': Le4.20 / Le10. FA 2024 s. 4 (k), tariff item 27.10: "B. Petrol Le 2.80 per litre C. Diesel Le 1.22 per litre effective 1st January 2024 Le 1.62 per litre effective 1st April 2024 Le 2.01 per litre effective 1st July 2024 Le 2.4 per litre effective 1st day of October 2024". FA 2025 s. 6 (b): "24.02 ... Cigarette containing tobacco NLe 2.0 per packet of 20 sticks" (FA 2023 had NLe20 per packet: the printed 2025 figure is applied). Amounts in new Leones. Grade B: the FA 2024 beer line is internally inconsistent ("Le0.01 per cl or Le10 per litre"), and the spirits (2208) table is an image not in the text.
-/

namespace SlGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Goods and Services Tax", standard := 1500, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .water | .books | .newspapers | .education | .health | .medicines | .transport | .petrol | .diesel | .financial => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Goods and Services Tax Act 2009 s. 14 (3) (b) (15 %), Second Schedule items 4-10 (exempt supplies), NRA compilation to 2016; s. 14 not amended by the Finance Acts 2017-2025"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500
#guard vatX.embedded { good := .water, amount := 10000 } == 0
#guard vatX.embedded { good := .books, amount := 10000 } == 0
#guard vatX.embedded { good := .newspapers, amount := 10000 } == 0
def accises : List R4.Exc :=
  [ { good := .wine, name := "Excise wine 10-20 % (local)", perUnitNum := 6300, perUnitDen := 1000, vatBp := 1500, minAbvBp := 1000, maxAbvBp := 1999, imported := some false, statute := "Excise Act First Schedule 2204 (FA 2024): Le6.30 per litre local" },
    { good := .wine, name := "Excise wine 10-20 % (import)", perUnitNum := 12000, perUnitDen := 1000, vatBp := 1500, minAbvBp := 1000, maxAbvBp := 1999, imported := some true, statute := "Excise Act First Schedule 2204 (FA 2024): Le12 per litre import" },
    { good := .wine, name := "Excise wine < 10 % (local)", perUnitNum := 4200, perUnitDen := 1000, vatBp := 1500, maxAbvBp := 999, imported := some false, statute := "Excise Act First Schedule 2204 (FA 2024): Le4.20 per litre local" },
    { good := .wine, name := "Excise wine < 10 % (import)", perUnitNum := 10000, perUnitDen := 1000, vatBp := 1500, maxAbvBp := 999, imported := some true, statute := "Excise Act First Schedule 2204 (FA 2024): Le10 per litre import" },
    { good := .petrol, name := "Excise petrol", perUnitNum := 2800, perUnitDen := 1000, vatBp := 1500, statute := "Excise Act First Schedule 27.10 B (FA 2024): Le2.80 per litre" },
    { good := .diesel, name := "Excise diesel", perUnitNum := 2400, perUnitDen := 1000, vatBp := 1500, statute := "Excise Act First Schedule 27.10 C (FA 2024): Le2.4 per litre from 1 Oct 2024" },
    { good := .cigarettes, name := "Excise cigarettes", perUnitNum := 100, perUnitDen := 1000, vatBp := 1500, statute := "Excise Act First Schedule 24.02 (FA 2025 s. 6 (b)): NLe2.0 per packet of 20 sticks" } ]
def excise : Family := R4.exciseFamily "Excise duty" accises
-- Excise Act First Schedule 2204 (FA 2024): Le6.30 per litre local: 10000 paid for 1 unit(s) at 12 % vol → 6
#guard (R4.exciseCharges [{ good := .wine, name := "Excise wine 10-20 % (local)", perUnitNum := 6300, perUnitDen := 1000, vatBp := 1500, minAbvBp := 1000, maxAbvBp := 1999, imported := some false, statute := "Excise Act First Schedule 2204 (FA 2024): Le6.30 per litre local" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [6]
-- Excise Act First Schedule 2204 (FA 2024): Le12 per litre import: 10000 paid for 1 unit(s) at 12 % vol → 12
#guard (R4.exciseCharges [{ good := .wine, name := "Excise wine 10-20 % (import)", perUnitNum := 12000, perUnitDen := 1000, vatBp := 1500, minAbvBp := 1000, maxAbvBp := 1999, imported := some true, statute := "Excise Act First Schedule 2204 (FA 2024): Le12 per litre import" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] ["wine"]).map (·.due) == [12]
-- Excise Act First Schedule 2204 (FA 2024): Le4.20 per litre local: 10000 paid for 1 unit(s) at 0.99 % vol → 4
#guard (R4.exciseCharges [{ good := .wine, name := "Excise wine < 10 % (local)", perUnitNum := 4200, perUnitDen := 1000, vatBp := 1500, maxAbvBp := 999, imported := some false, statute := "Excise Act First Schedule 2204 (FA 2024): Le4.20 per litre local" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 99 }] []).map (·.due) == [4]
-- Excise Act First Schedule 2204 (FA 2024): Le10 per litre import: 10000 paid for 1 unit(s) at 0.99 % vol → 10
#guard (R4.exciseCharges [{ good := .wine, name := "Excise wine < 10 % (import)", perUnitNum := 10000, perUnitDen := 1000, vatBp := 1500, maxAbvBp := 999, imported := some true, statute := "Excise Act First Schedule 2204 (FA 2024): Le10 per litre import" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 99 }] ["wine"]).map (·.due) == [10]
-- Excise Act First Schedule 27.10 B (FA 2024): Le2.80 per litre: 10000 paid for 1 unit(s) at 0 % vol → 2
#guard (R4.exciseCharges [{ good := .petrol, name := "Excise petrol", perUnitNum := 2800, perUnitDen := 1000, vatBp := 1500, statute := "Excise Act First Schedule 27.10 B (FA 2024): Le2.80 per litre" }] [{ good := .petrol, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [2]
-- Excise Act First Schedule 27.10 C (FA 2024): Le2.4 per litre from 1 Oct 2024: 10000 paid for 1 unit(s) at 0 % vol → 2
#guard (R4.exciseCharges [{ good := .diesel, name := "Excise diesel", perUnitNum := 2400, perUnitDen := 1000, vatBp := 1500, statute := "Excise Act First Schedule 27.10 C (FA 2024): Le2.4 per litre from 1 Oct 2024" }] [{ good := .diesel, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [2]
-- Excise Act First Schedule 24.02 (FA 2025 s. 6 (b)): NLe2.0 per packet of 20 sticks: 10000 paid for 1 unit(s) at 0 % vol → 0
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise cigarettes", perUnitNum := 100, perUnitDen := 1000, vatBp := 1500, statute := "Excise Act First Schedule 24.02 (FA 2025 s. 6 (b)): NLe2.0 per packet of 20 sticks" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [0]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["Second Schedule descriptions limit some items (e.g. passenger transport, hydrocarbon products); the basket lines are taken as exempt in full", "land and buildings (item 12) not separable from rent; later Second Schedule additions (FA 2021-2024) not applied", "beer (2203): FA 2024 prints 'Le0.01 per cl or Le10 per litre' (the two figures differ tenfold): not applied; spirits (2208) and other drinks: the FA 2024 tables are images; local spirits by local content (FA 2025 tariff 22.09 D1-D4, 5-20 %) not separable", "the GST rate (VAT 1500) used in the excise base split is the 15 % of the GST Act 2009 (not held)"]

end SlGlobal
