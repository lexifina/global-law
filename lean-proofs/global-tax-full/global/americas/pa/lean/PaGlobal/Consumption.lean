import PaGlobal.Pit
import TaxKernel.Global2

/-!
# Panama 2025: ITBMS (5111); Impuesto Selectivo al Consumo on alcoholic drinks (5121)

Source: Ley 8 of 15 March 2010 (G.O. 26489-A), Legispan copy held by the 1.x builder
(`world/B12-latin-america/pa/src/ley8_2010.txt`), which rewrites parts of Código Fiscal art. 1057-V. The full Código
Fiscal text was not reached (dgi.mef.gob.pa answers 500; no Wayback copy of a consolidated code): grade B.
* **Art. 1057-V Parágrafo 6** (Ley 8 art. 76): "La tarifa de este impuesto será de siete por ciento (7%) a partir del 1
  de julio de 2010"; 10 % on alcoholic beverages, 15 % on tobacco products, 10 % on "El servicio de hospedaje o
  alojamiento".
* **Parágrafo 8 (exempt)**: a 5 (Ley 8 art. 79) crude oil, diesel, gasolines, LPG, kerosene; a 14 (art. 80) "Productos
  medicinales y farmacéuticos especificados en el Capítulo 30 del Arancel"; b 5 (art. 81) "el transporte marítimo y
  terrestre de pasajeros".
* **Parágrafo 9** (art. 84): no taxpayer whose gross annual income is below "treinta y seis mil balboas (B/.36,000.00)".
* The rest of the Parágrafo 8 exemptions (food, health, education, financial services, residential rent, electricity)
  is in the parts of the Código Fiscal that Ley 8 does not reprint: those goods are charged at 7 % (upper bound, flagged).

**Pass 12 (2026-11-21), ISC on alcoholic drinks (grade A):** Ley 15 de 2013 (G.O. 12 March 2013; Legispan text in
lexifina/panama-law `ley/2013/0015`) art. 1 adds **art. 7-A to Ley 45 de 1995**; arts. 2, 5, 6 make it the rule for
licores (art. 11), vinos (art. 20) and cerveza (art. 25). For drinks whose wholesale price is under B/. 18.00 a litre:
"0.6% a 4.99% ... tasa específica de trece centavos y un cuarto (B/.0.1325) por litro de bebida"; "5% a 20% ... cuatro
centavos (B/.0.04) por grado de contenido de alcohol por litro de bebida"; "Más de 20% ... (B/.0.062) por grado": per
litre of pure alcohol B/. 4.00 and B/. 6.20. Above B/. 18.00 wholesale a litre: B/. 0.105 per degree (B/. 10.50 per
litre of pure alcohol) - the wholesale price is not an input, the lower table is charged (flagged). Kernel
`ExciseRule` strength bands (`minAbvBp < abv <= maxAbvBp`); a line without `abvBp` is not charged. Amendments after
2019 (the end of the repository's coverage) not checked. Tobacco ISC (Ley 69 de 2009) and the fuel consumption tax
are not held: separate C row.
-/

namespace PaGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon PaGlobal

def vat : Vat :=
  { name := "Impuesto de Transferencia de Bienes Corporales Muebles y la Prestación de Servicios (ITBMS)", standard := 700, reduced := 1000, reduced2 := 1500, threshold := 36000,
    classOf := fun gd => match gd with
      | .beer | .wine | .spirits | .hotels => .reduced
      | .cigarettes | .tobaccoOther => .reduced2
      | .petrol | .diesel | .medicines | .transport => .exempt
      | _ => .standard }

def vatStatute : String := "Código Fiscal art. 1057-V Parágrafo 6 (7 %; 10 % alcohol and lodging; 15 % tobacco), Parágrafo 8 a 5, a 14, b 5 (exempt), Parágrafo 9 (B/.36,000), as amended by Ley 8 de 2010 arts. 76, 79-81, 84"

def vatF : Family := vatFamily "Impuesto de Transferencia de Bienes Corporales Muebles y la Prestación de Servicios (ITBMS)" vat vatStatute .vat .central

/-- Ley 45 de 1995 art. 7-A (Ley 15 de 2013 art. 1): wholesale price under B/. 18.00 a litre. -/
def iscBands (g : Good) : List ExciseRule :=
  [{ good := g, name := "Impuesto Selectivo al Consumo (bebidas alcohólicas)", perUnitNum := 1325, perUnitDen := 10000,
     minAbvBp := 59, maxAbvBp := 499, statute := "Ley 45 de 1995 art. 7-A num. 1 (Ley 15 de 2013): B/. 0.1325 per litre, 0.6 % to 4.99 % vol" },
   { good := g, name := "Impuesto Selectivo al Consumo (bebidas alcohólicas)", perUnitNum := 4, onPureAlcohol := true,
     minAbvBp := 499, maxAbvBp := 2000, statute := "Ley 45 de 1995 art. 7-A num. 2 (Ley 15 de 2013): B/. 0.04 per degree per litre, 5 % to 20 % vol" },
   { good := g, name := "Impuesto Selectivo al Consumo (bebidas alcohólicas)", perUnitNum := 62, perUnitDen := 10, onPureAlcohol := true,
     minAbvBp := 2000, statute := "Ley 45 de 1995 art. 7-A num. 3 (Ley 15 de 2013): B/. 0.062 per degree per litre, above 20 % vol" }]

def isc : List ExciseRule := iscBands .beer ++ iscBands .wine ++ iscBands .spirits

def exciseF : Family := exciseRuleFamily "Impuesto Selectivo al Consumo (bebidas alcohólicas)" isc

def families : List Family := [vatF, exciseF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 52: \"Nadie está obligado a pagar contribución ni impuesto que no estuvieren legalmente establecidos\" (`pa/law/const_art-052.md`). no law read in this build levies a general sales or turnover tax beside the VAT of the 5111 row (laws read include: Código Fiscal art. 1057-V Parágrafos 6, 8, 9 (Ley 8 de 2010 arts. 76, 79-81, 84); Ley 45 de 1995 arts. 7-A, 11, 20, 25 (Ley 15 de 2013 arts. 1, 2, 5, 6); Código Fiscal art. 699 (Ley 8/2010): 25 %; Código Fiscal art. 733 (dividends 10 %); 1.x model (see its summary.json); Ley 51 de 2005 art. 101 as replaced by Ley 462 de 2025 art. 84)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food || s.good == .health || s.good == .education || s.good == .financial || s.good == .rent || s.good == .electricity || s.good == .water || s.good == .insurance) "Parágrafo 8 exemptions outside Ley 8 de 2010 (food, health, education, financial services, rent, utilities) not held: charged at 7 % (upper bound)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel || s.good == .nonAlcoholic) "ISC on tobacco (Ley 69 de 2009), soft drinks and the fuel consumption tax not modelled"
  ++ when (g.consumption.any fun s => s.good == .beer || s.good == .wine || s.good == .spirits) "alcohol ISC: the table for a wholesale price under B/. 18.00 a litre is charged (above it B/. 0.105 per degree); a line without abvBp is not charged; amendments after 2019 not checked"

#guard vat.embedded { good := .clothing, amount := 1070 } == 70
#guard vat.embedded { good := .spirits, amount := 1100 } == 100
#guard vat.embedded { good := .cigarettes, amount := 1150 } == 150
#guard vat.embedded { good := .petrol, amount := 1070 } == 0
#guard vat.threshold == 36000
-- 10 litres of beer at 4.8 % vol: 10 x 0.1325 = 1.325 -> 1; at 5 %: 0.5 l pure x 4.00 = 2; 2 litres of rum at 40 %: 0.8 l x 6.20 = 4.96 -> 4
#guard ((isc.filter (·.appliesTo 2025 { good := .beer, amount := 30, quantity := 10000, abvBp := 480 } {})).map (·.dutyOn { good := .beer, amount := 30, quantity := 10000, abvBp := 480 } {})) == [1]
#guard ((isc.filter (·.appliesTo 2025 { good := .beer, amount := 30, quantity := 10000, abvBp := 500 } {})).map (·.dutyOn { good := .beer, amount := 30, quantity := 10000, abvBp := 500 } {})) == [2]
#guard ((isc.filter (·.appliesTo 2025 { good := .spirits, amount := 40, quantity := 2000, abvBp := 4000 } {})).map (·.dutyOn { good := .spirits, amount := 40, quantity := 2000, abvBp := 4000 } {})) == [4]

end PaGlobal.Consumption
