import R4Common
import R4Common.K21

/-!
# Tanzania 2025: VAT (5111) — grade B; excise not modelled

Source: Value Added Tax Act Cap. 148 (registry fetch `global/registry/afm_data/fetch/TZ/tz_vat.pdf.txt`): s. 5 (1)
"… the value added tax rate, which shall be eighteen percent" (Act No. 2 of 2016 s. 91); (2) "Where the supply or
import is zero-rated, the value added tax rate shall be zero percent". The Schedule of exempt supplies was not read
(OCR watermark noise): every basket line at 18 %. Finance Act 2025 s. 124 adds s. 5 (5) (supplies to withholding agents: 18 %,
of which the agent withholds 3 % on goods and 6 % on services) and s. 5 (6) (16 % for unregistered buyers paying through a bank or an
approved electronic system, from 1 September 2025, eligible persons by public notice): the payment method is not an input, 18 % kept
all year (twentieth pass).

Excise (Cap. 147 R.E. 2023 Fourth Schedule, `global/registry/afm_data/fetch/TZ/tz_exc.pdf.txt`, TRA's print of the Act): the table prints two rate columns per line (e.g.
non-alcoholic beer "Tshs. 561.00 per litre | Tshs. 673.20 per litre") and the Finance Act 2025 (from 1 July 2025)
re-rates many headings; which column and which half-year apply was not settled: not modelled (`unsupported`).
-/

namespace TzGlobal
open TaxKernel TaxKernel.Global

def vatT : Vat := { name := "Value Added Tax", standard := 1800 }

def vat : Family := R4.vatFamily vatT "VAT Act Cap. 148 s. 5 (1) (18 %); exempt schedule not read"

def consumptionNotes (g : CanonGlobal) : List String :=
  (if g.consumption.isEmpty then [] else
    ["VAT Act Cap. 148 Schedule (exemptions) not read: every basket line at 18 %",
     "fuel levies (Road and Fuel Tolls Act): not modelled",
     "VAT Act Cap. 148 s. 5 (6) (added by FA 2025 s. 124, in operation 1 September 2025): 16 % on standard-rated supplies to an unregistered person who pays through a bank or an electronic payment system approved by the Commissioner General, the persons eligible and the manner by public notice (not held); the payment method is not an input: 18 % applied to every line"])

#guard vatT.embedded { good := .food, amount := 11800 } == 1800


/-! Excise (5121), beer made from malt (HS 2203.00): Finance Act 2025 (No. 11) amending the Fourth Schedule to the
Excise (Management and Tariff) Act Cap. 147: "Beer made from malt ... Made from wholly or partially Imported Barley
Tshs. 918.00 per litre [old] Tshs. 928.00 per litre [new] ... Imported TZS. 963.90 per litre [old] TZS. 973.90 per
litre [new]" (100 % locally grown barley: 620.00 / 630.00). The new rates apply from 1 July 2025: kernel 2.1 dated
rules, an undated basket line is split by days. Local beer is taken as brewed from imported or partly imported
barley. -/
def beerRules : List ExciseRule :=
  [{ good := .beer, name := "Excise duty (beer, local)", perUnitNum := 918, imported := some false, validTo := "2025-07-01", statute := "Cap. 147 Fourth Schedule 2203.00 (Tshs 918/l to 30 June 2025, FA 2025 old rate)" },
   { good := .beer, name := "Excise duty (beer, local)", perUnitNum := 928, imported := some false, validFrom := "2025-07-01", statute := "Cap. 147 Fourth Schedule 2203.00 as amended by FA 2025 (Tshs 928/l from 1 July 2025)" },
   { good := .beer, name := "Excise duty (beer, imported)", perUnitNum := 96390, perUnitDen := 100, imported := some true, validTo := "2025-07-01", statute := "Cap. 147 Fourth Schedule 2203.00 (Tshs 963.90/l to 30 June 2025)" },
   { good := .beer, name := "Excise duty (beer, imported)", perUnitNum := 97390, perUnitDen := 100, imported := some true, validFrom := "2025-07-01", statute := "Cap. 147 Fourth Schedule 2203.00 as amended by FA 2025 (Tshs 973.90/l from 1 July 2025)" },
   { good := .spirits, name := "Excise duty (spirits)", perUnitNum := 438606, perUnitDen := 100, validTo := "2025-07-01", statute := "Cap. 147 Fourth Schedule 2208.30-2208.70 (whisky, rum, gin, vodka, liqueurs: Tshs 4,386.06/l, FA 2025 old rate)" },
   { good := .spirits, name := "Excise duty (spirits)", perUnitNum := 441106, perUnitDen := 100, validFrom := "2025-07-01", statute := "Cap. 147 Fourth Schedule 2208.30-2208.70 as amended by FA 2025 (Tshs 4,411.06/l from 1 July 2025)" },
   { good := .nonAlcoholic, name := "Excise duty (sweetened / flavoured waters)", perUnitNum := 6710, perUnitDen := 100, statute := "Cap. 147 R.E. 2023 Fourth Schedule 2202.10.00 (Tshs 67.10/l, local and imported; not amended by FA 2024 or FA 2025)" },
   { good := .wine, name := "Excise duty (wine, domestic grapes > 75 %)", perUnitNum := 200, imported := some false, validTo := "2025-07-01", statute := "Cap. 147 R.E. 2023 Fourth Schedule 2204.21.00 (Tshs 200/l to 30 June 2025)" },
   { good := .wine, name := "Excise duty (wine, domestic grapes > 75 %)", perUnitNum := 215, imported := some false, validFrom := "2025-07-01", statute := "Cap. 147 Fourth Schedule 2204.21.00 as substituted by FA 2025 (Tshs 215/l from 1 July 2025)" },
   { good := .wine, name := "Excise duty (wine, other)", perUnitNum := 5600, imported := some true, validTo := "2025-07-01", statute := "Cap. 147 R.E. 2023 Fourth Schedule 2204.21.00 other (Tshs 5,600/l to 30 June 2025)" },
   { good := .wine, name := "Excise duty (wine, other)", perUnitNum := 5615, imported := some true, validFrom := "2025-07-01", statute := "Cap. 147 Fourth Schedule 2204.21.00 other, as substituted by FA 2025 (Tshs 5,615/l from 1 July 2025)" },
   { good := .cigarettes, name := "Excise duty (cigarettes, filter, domestic tobacco > 75 %)", perUnitNum := 3531, perUnitDen := 100, imported := some false, statute := "Cap. 147 R.E. 2023 Fourth Schedule 2402.20.10 (Tshs 35,310 per mille; FA 2024 only adds the words 'Locally produced', FA 2025 does not amend it)" },
   { good := .cigarettes, name := "Excise duty (cigarettes, other)", perUnitNum := 670761, perUnitDen := 10000, imported := some true, statute := "Cap. 147 R.E. 2023 Fourth Schedule 2402.20.10 other (Tshs 67,076.10 per mille)" },
   { good := .petrol, name := "Excise duty (motor spirit)", perUnitNum := 379, statute := "Cap. 147 R.E. 2023 Fourth Schedule 2710.12.10 (Tshs 379/l; not amended by FA 2024-2025)" },
   { good := .diesel, name := "Excise duty (gas oil)", perUnitNum := 255, statute := "Cap. 147 R.E. 2023 Fourth Schedule 2710.19.31 (Tshs 255/l; not amended by FA 2024-2025)" }]

def excise : Family := exciseRuleFamily "excise duty (Cap. 147 Fourth Schedule, FA 2025)" beerRules

def excT1 : CanonGlobal := { id := "x", household := { id := "x" }, consumption := [{ good := .beer, amount := 0, quantity := 1000000 }] }
-- 1 000 litres of local beer bought over the year: two dated charges (181 days at 918, 184 at 928), between the two rates
#guard (exciseRuleCharges beerRules excT1).length == 2
#guard let t := ((exciseRuleCharges beerRules excT1).map (·.due)).foldl (· + ·) 0; 918000 ≤ t && t ≤ 928000

def excT2 : CanonGlobal := { id := "x", household := { id := "x" }, consumption := [{ good := .spirits, amount := 0, quantity := 1000000, abvBp := 4000 }] }
#guard let t := ((exciseRuleCharges beerRules excT2).map (·.due)).foldl (· + ·) 0; 4386060 ≤ t && t ≤ 4411060

-- the other goods' printed rates: 1 000 l of soft drinks, 1 000 l of local wine (half a year at 200, half at 215),
-- 1 000 local filter cigarettes, 1 000 l of petrol and of diesel
def excT3 : CanonGlobal := { id := "x", household := { id := "x" }, consumption := [{ good := .nonAlcoholic, amount := 0, quantity := 1000000 }, { good := .cigarettes, amount := 0, quantity := 1000000 }, { good := .petrol, amount := 0, quantity := 1000000 }, { good := .diesel, amount := 0, quantity := 1000000 }] }
#guard ((exciseRuleCharges beerRules excT3).map (·.due)) == [67100, 35310, 379000, 255000]
def excT4 : CanonGlobal := { id := "x", household := { id := "x" }, consumption := [{ good := .wine, amount := 0, quantity := 1000000, abvBp := 1200 }] }
#guard let t := ((exciseRuleCharges beerRules excT4).map (·.due)).foldl (· + ·) 0; 200000 ≤ t && t ≤ 215000

end TzGlobal
