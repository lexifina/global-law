import R4Common

/-!
# Mauritius 2025: VAT (5111) and excise duty (5121)

Sources (MRA consolidated texts, registry fetch `global/registry/afm_data/fetch/MU/`; the Excise Act endnotes run to
the Finance Act 2025):
* **VAT Act 1998**, Fourth Schedule (section 10): "Rate of VAT … 15 per cent". The First (exempt) and Fifth
  (zero-rated) Schedules list medical, hospital and dental services, educational services, pharmaceutical products of
  headings 30.01-30.06, water supplied by the Central Water Authority and electricity supplied by the CEB, but the
  extracted text does not show which of the two schedules each item sits in: every basket line is at 15 % here
  (grade B; listed in `unsupported`).
* **Excise Act 1994**, First Schedule: "22.03 Beer made from malt: Of an alcoholic strength not exceeding 9 degrees:
  … 2203.00.19 Other … Rs 58.10 per litre" (cans: plus Rs 2 per can); "Of an alcoholic strength … other … Rs 80.65";
  whiskies and other spirits "2208.30.90 … Rs 2,705.70 per litre absolute alcohol"; "2402.20.00 Cigarettes
  containing tobacco … Rs 8,237 per thousand"; "2710.19.19 Other (Mogas) … 0"; "2710.19.50 Gas oils … Rs 4.22 per
  litre"; sugar-sweetened drinks "15 cents per gram of sugar" (sugar content not an input: not modelled).
-/

namespace MuGlobal
open TaxKernel TaxKernel.Global

def vatM : Vat := { name := "Value Added Tax", standard := 1500 }

def vat : Family := R4.vatFamily vatM "VAT Act 1998 s. 10 and Fourth Schedule (15 %)"

def excises : List R4.Exc :=
  [ { good := .beer, name := "Excise duty (beer)", perUnitNum := 5810, perUnitDen := 100, maxAbvBp := 900,
      statute := "Excise Act First Schedule 2203.00.19 (Rs 58.10 per litre, ≤ 9°)" },
    { good := .beer, name := "Excise duty (beer)", perUnitNum := 8065, perUnitDen := 100, minAbvBp := 900,
      statute := "Excise Act First Schedule 2203.00.99 (Rs 80.65 per litre)" },
    { good := .spirits, name := "Excise duty (spirits)", perUnitNum := 270570, perUnitDen := 100, onPureAlcohol := true,
      statute := "Excise Act First Schedule 2208.30.90 / 2208.90.19 (Rs 2,705.70 per litre absolute alcohol)" },
    { good := .cigarettes, name := "Excise duty (cigarettes)", perUnitNum := 8237, perUnitDen := 1000,
      statute := "Excise Act First Schedule 2402.20.00 (Rs 8,237 per thousand)" },
    { good := .diesel, name := "Excise duty (gas oil)", perUnitNum := 422, perUnitDen := 100,
      statute := "Excise Act First Schedule 2710.19.50 (Rs 4.22 per litre)" } ]

def excise : Family := R4.exciseFamily "excise duty (Excise Act 1994, First Schedule)" excises

def consumptionNotes (g : CanonGlobal) : List String :=
  (if g.consumption.isEmpty then [] else
    ["VAT Act First / Fifth Schedules (exempt and zero-rated supplies: medical, educational, pharmaceutical, CWA water, CEB electricity, basic foods) not resolved: every line at 15 %"])
  ++ (if g.consumption.any (·.good == .wine) then ["Excise Act: wines (per-litre rates by type and strength) not mapped"] else [])
  ++ (if g.consumption.any (·.good == .nonAlcoholic) then ["Excise Act: sugar-sweetened drinks taxed per gram of sugar (sugar content not an input)"] else [])
  ++ (if g.consumption.any (·.good == .petrol) then ["Excise Act 2710.19.19 Mogas: excise 0; petroleum levies outside the Excise Act not modelled"] else [])

-- a litre of 5 % beer: Rs 58.10; a litre of 40 % whisky: 0,4 l absolute alcohol × Rs 2 705.70 = 1 082.28
#guard (R4.exciseCharges excises [{ good := .beer, amount := 200, quantity := 1000, abvBp := 500 }]).map (·.due) == [58]
#guard (R4.exciseCharges excises [{ good := .spirits, amount := 2000, quantity := 1000, abvBp := 4000 }]).map (·.due) == [1082]
#guard vatM.embedded { good := .food, amount := 11500 } == 1500

end MuGlobal
