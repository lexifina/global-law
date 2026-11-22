import R4Common
import TaxKernel.Global2

/-!
# Liberia 2025: VAT (5111) and excises (5121) (generated from `R4/specs/lr.json` by `R4/tools/gen_country.py`)

Sources: Consolidated Liberia Revenue Code as amended 2020 (`cmp20/world/B10-anglophone-africa/lr/law/REVENUE-CODE-LIBERIA-REVENUE-CODE-AMENDEMENT-2020-min.txt`) and the Tax Amendment Act of December 2024 (approved 17 December 2024; OCR of `world/B10-anglophone-africa/lr/law/TAX-AMENDMENT-ACT-OF-DECEMBER-2024-AMENDING-THE-LIBERIA-CONSOLIDATED-REVENUE-CODE-AS-AMENDED.pdf`: it amends ss. 50, 55, 74, 203, 204, 211, 602, 702, 704, 741, 806 and 905 and leaves s. 200 as the 2020 consolidation prints it; not the later Tax Amendment Act of December 2025, `LRC-Amendment-December-2025.pdf`, approved 2026). Pass 10 (GST): Liberia Revenue Code as amended (2020 consolidation, `world/B10-anglophone-africa/lr/law/REVENUE-CODE-LIBERIA-REVENUE-CODE-AMENDEMENT-2020-min.txt`) Part III Chapter 10 s. 1000-1002, 1021-1022 (the sections are in the text body, not only the table of contents); Tax Amendment Act of 2024 amending certain portions of Chapters 8 and 10 (approved 17 Dec 2024, printed 20 Dec 2024, OCR `TAX-AMENDMENT-ACT-OF-2024-AMENDING-CERTAIN-PORTIONS-…_ocr.txt`). The December 2024 excise schedule was read on the page image (p. 12 of the Tax Amendment Act of December 2024): US$ per litre, imported / local columns. The LRC Amendment of December 2025 (services tax 13 %) applies from 2026.

Tax Amendment Act of 2024 Part 2 s. 1: "Section 1000(b)(3) is amended to read as follows: (3) The rate of goods tax is 12 percent of the Section 1004 taxable amount, except that if the supply is an export of goods, the rate of tax is zero (0) percent." "Section 1021(b)(1) and Section 1021(b)(2) are amended to read as follows: (b) Rate of Tax. (1) General Rule. The rate of services tax is 12 percent of the taxable amount described in Section 1025. (2) Exceptions. The rate of services tax at 12 percent of the taxable amount shall not apply to telecommunication services." Part 3: "this Act shall take effect upon publication into handbills" (printed 20 December 2024). LRC s. 1000 (a): goods tax on "(1) Every taxable supply ... by a registered manufacturer, and (2) Every taxable import"; s. 1022 (a) taxable services: "(1) Electricity services; (2) Telecommunications services; (3) The Provision of water for a fee; (4) Services supplied in carrying on the business of a hotel ...; (5) ... a restaurant or café ...; (6) Gambling services ...; (7) Sale of tickets by international transport services ...; (8) Services of a travel agency ...; (9) Sporting or game arranger services ...; (10) Other services (specified in regulations) ...". Former s. 1021 (b) (2) (2020 text): "An additional 5 percent surtax applies to telecommunications services" (with the 10 % general rate).

Tax Amendment Act of December 2024, excise schedule (page image p. 12): US$ per litre, imported / local columns: beer, wine and other fermented beverages 0.80 / 0.30; spirits 1.50 / 0.50. Nineteenth pass: kernel 2.7.0 converts US$ amounts at a declared rate; the model declares none (no official 2025 Central Bank of Liberia rate publication was reached: the CBL 'Reference Rate' page captured 15 January 2025 prints no figure), so the duty is computed at the line's own fxRates.USD and the goods are listed as grade C without it.
-/

namespace LrGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Goods and services tax (goods tax and services tax)", standard := 1200, reduced := 1500, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .communication => .reduced
      | .rent | .health | .medicines | .education | .financial | .insurance | .transport => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Liberia Revenue Code s. 1000 (b) (3) (goods tax) and s. 1021 (b) (1) (services tax) as amended by the Tax Amendment Act of 2024 (Chapters 8 and 10), in force on publication 20 Dec 2024: 12 %; s. 1022 (a) list of taxable services; s. 1001 (e) exempt supplies"

-- the standard rate as printed: 12 % inside a tax-inclusive 11200
#guard vatX.embedded { good := .other, amount := 11200 } == 1200
#guard vatX.embedded { good := .communication, amount := 11500 } == 1500
#guard vatX.embedded { good := .rent, amount := 10000 } == 0
#guard vatX.embedded { good := .health, amount := 10000 } == 0
def accisesUsd (r : FxRate) : List R4.Exc :=
  [ { good := .beer, name := "Excise tax (beer, imported)", perUnitNum := 80 * r.num, perUnitDen := 100 * r.den, imported := some true, statute := "Schedule (Dec 2024): beer US$0.80 a litre, imported" ++ "; " ++ r.note },
    { good := .beer, name := "Excise tax (beer, local)", perUnitNum := 30 * r.num, perUnitDen := 100 * r.den, imported := some false, statute := "Schedule (Dec 2024): beer US$0.30 a litre, local" ++ "; " ++ r.note },
    { good := .wine, name := "Excise tax (wine and other fermented beverages, imported)", perUnitNum := 80 * r.num, perUnitDen := 100 * r.den, imported := some true, statute := "Schedule (Dec 2024): wine and other fermented beverages US$0.80 a litre, imported" ++ "; " ++ r.note },
    { good := .wine, name := "Excise tax (wine and other fermented beverages, local)", perUnitNum := 30 * r.num, perUnitDen := 100 * r.den, imported := some false, statute := "Schedule (Dec 2024): wine and other fermented beverages US$0.30 a litre, local" ++ "; " ++ r.note },
    { good := .spirits, name := "Excise tax (spirits, imported)", perUnitNum := 150 * r.num, perUnitDen := 100 * r.den, imported := some true, statute := "Schedule (Dec 2024): spirits US$1.50 a litre, imported" ++ "; " ++ r.note },
    { good := .spirits, name := "Excise tax (spirits, local)", perUnitNum := 50 * r.num, perUnitDen := 100 * r.den, imported := some false, statute := "Schedule (Dec 2024): spirits US$0.50 a litre, local" ++ "; " ++ r.note } ]
def exciseUsdGoods : List Good := [.beer, .spirits, .wine]
def exciseUsd : Family :=
  { name := "5121 Excise tax (US$ duties)", covers := [.excise],
    run := fun a g p => match fxFor g "USD" none with
      | some r => (R4.exciseFamily "Excise tax (US$ duties)" (accisesUsd r)).run a g p
      | none => [] }
def exciseUsdNotes (g : CanonGlobal) : List String :=
  if (fxFor g "USD" none).isNone && g.consumption.any (fun s => exciseUsdGoods.contains s.good)
  then [fxUnknownLine "5121" "Excise tax" "USD"] else []
def usdTestRate0 : FxRate := { currency := "USD", num := 18500, den := 100, source := "test rate", date := "2025-07-01" }
#guard (R4.exciseCharges (accisesUsd usdTestRate0) [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [55]
def usdTestRate1 : FxRate := { currency := "USD", num := 18500, den := 100, source := "test rate", date := "2025-07-01" }
#guard (R4.exciseCharges (accisesUsd usdTestRate1) [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 0 }] ["beer"]).map (·.due) == [148]
def usdTestRate2 : FxRate := { currency := "USD", num := 18500, den := 100, source := "test rate", date := "2025-07-01" }
#guard (R4.exciseCharges (accisesUsd usdTestRate2) [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 0 }] ["spirits"]).map (·.due) == [277]
def usdTestRate3 : FxRate := { currency := "USD", num := 18500, den := 100, source := "test rate", date := "2025-07-01" }
#guard (R4.exciseCharges (accisesUsd usdTestRate3) [{ good := .wine, amount := 10000, quantity := 750, abvBp := 0 }] []).map (·.due) == [41]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["the goods tax falls on imports and on supplies by registered manufacturers, not on retail margins: charging 12 % on the tax-inclusive basket price overstates it (convention: whole price)", "services outside the s. 1022 list (rent, health, education, financial, insurance, local transport) are untaxed", "telecommunications: the 2024 amendment takes them out of the 12 % rate without stating another; the former 10 % + 5 % surtax (15 %) is used (flagged); the December 2025 amendment (2026) restores '13 % + 5 % surtax'", "pharmaceuticals are exempt as specified by regulation (s. 1001 (e) (3)); only school textbooks are exempt among books", "nineteenth pass (kernel 2.7.0 Fx): C -> A. The December 2024 schedule's US$ amounts are converted at the line's own fxRates.USD (fxFor, no declared rate); without it beer, wine and spirits lines are listed (grade C, 'fxRates.USD not given'). Hand cases at L$185.00 per US$: 1 litre of local beer -> 55 (0.30 x 185 = 55.50, rounded down); imported beer -> 148; imported spirits -> 277; 75 cl of local wine -> 41", "origin: a good is imported when the line lists it in importedGoods (default local)"] ++ exciseUsdNotes g

end LrGlobal
