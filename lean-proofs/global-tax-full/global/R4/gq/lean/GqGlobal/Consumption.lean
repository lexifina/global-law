import R4Common

/-!
# Equatorial Guinea 2025: VAT (5111) and excises (5121) (generated from `R4/specs/gq.json` by `R4/tools/gen_country.py`)

Source: Ley Núm. 1/2024 (Ley Tributaria), OCR of the BOE-style edition (`cmp20/world/B08-central-africa-fr/gq/law/rescue3/Ley1-2024_ocr_spa.txt`).

art. 155: "2) Tipo general de 15%: aplicable a todas las operaciones imponibles, con exclusión de las sujetas al tipo reducido de 5% y 0%. 3) Tipo reducido de 5% aplicable a los productos recogidos en el cuadro siguiente: Productos de alimentación de los niños; Productos de higiene personal e infantil; Leche …". Exemptions not read.

art. 176: "1) Para las bebidas alcohólicas: un impuesto proporcional del 30%, incrementado de 75 FCFA por grado de alcohol y por litro; 2) Para la cerveza, esta tarifa está incrementada en 200 FCFA por litro. 3) Para las bebidas no-alcohólicas: un impuesto proporcional del 30%, incrementado de: a) para bebidas con azúcar … 50 FCFA por litro …; 4) Tabaco: un impuesto proporcional del 30%, incrementado de … b) 15.000 FCFA por cada 1.000 unidades de cigarrillos". 75 FCFA per degree and litre = 7 500 FCFA per litre of pure alcohol. The beer surcharge of 200 FCFA per litre is a second line (its amount is not netted out of the ad valorem base: small overstatement of the base).
-/

namespace GqGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Impuesto sobre el Valor Añadido", standard := 1500, reduced := 500, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Ley 1/2024 art. 155 (15 %; 5 %; 0 %)"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500
def accises : List R4.Exc :=
  [ { good := .beer, name := "Impuesto especial (bebidas alcohólicas)", perUnitNum := 7500, advBp := 3000, vatBp := 1500, onPureAlcohol := true, statute := "Ley 1/2024 art. 176 1) (30 % + 75 FCFA per degree and litre)" },
    { good := .beer, name := "Impuesto especial (cerveza, recargo)", perUnitNum := 200, statute := "Ley 1/2024 art. 176 2) (+200 FCFA per litre)" },
    { good := .wine, name := "Impuesto especial (bebidas alcohólicas)", perUnitNum := 7500, advBp := 3000, vatBp := 1500, onPureAlcohol := true, statute := "Ley 1/2024 art. 176 1)" },
    { good := .spirits, name := "Impuesto especial (bebidas alcohólicas)", perUnitNum := 7500, advBp := 3000, vatBp := 1500, onPureAlcohol := true, statute := "Ley 1/2024 art. 176 1)" },
    { good := .nonAlcoholic, name := "Impuesto especial (bebidas no alcohólicas)", perUnitNum := 50, advBp := 3000, vatBp := 1500, statute := "Ley 1/2024 art. 176 3) a) (30 % + 50 FCFA/l, sugared)" },
    { good := .cigarettes, name := "Impuesto especial (tabaco)", perUnitNum := 15000, perUnitDen := 1000, advBp := 3000, vatBp := 1500, statute := "Ley 1/2024 art. 176 4) b) (30 % + 15.000 FCFA per 1.000)" } ]
def excise : Family := R4.exciseFamily "Impuestos especiales al consumo" accises
-- Ley 1/2024 art. 176 1) (30 % + 75 FCFA per degree and litre): 10000 paid for 1 unit(s) at 5 % vol → 2295
#guard (R4.exciseCharges [{ good := .beer, name := "Impuesto especial (bebidas alcohólicas)", perUnitNum := 7500, advBp := 3000, vatBp := 1500, onPureAlcohol := true, statute := "Ley 1/2024 art. 176 1) (30 % + 75 FCFA per degree and litre)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [2295]
-- Ley 1/2024 art. 176 2) (+200 FCFA per litre): 10000 paid for 1 unit(s) at 5 % vol → 200
#guard (R4.exciseCharges [{ good := .beer, name := "Impuesto especial (cerveza, recargo)", perUnitNum := 200, statute := "Ley 1/2024 art. 176 2) (+200 FCFA per litre)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [200]
-- Ley 1/2024 art. 176 1): 10000 paid for 1 unit(s) at 12 % vol → 2698
#guard (R4.exciseCharges [{ good := .wine, name := "Impuesto especial (bebidas alcohólicas)", perUnitNum := 7500, advBp := 3000, vatBp := 1500, onPureAlcohol := true, statute := "Ley 1/2024 art. 176 1)" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [2698]
-- Ley 1/2024 art. 176 1): 10000 paid for 1 unit(s) at 40 % vol → 4314
#guard (R4.exciseCharges [{ good := .spirits, name := "Impuesto especial (bebidas alcohólicas)", perUnitNum := 7500, advBp := 3000, vatBp := 1500, onPureAlcohol := true, statute := "Ley 1/2024 art. 176 1)" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [4314]
-- Ley 1/2024 art. 176 3) a) (30 % + 50 FCFA/l, sugared): 10000 paid for 1 unit(s) at 0 % vol → 2045
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Impuesto especial (bebidas no alcohólicas)", perUnitNum := 50, advBp := 3000, vatBp := 1500, statute := "Ley 1/2024 art. 176 3) a) (30 % + 50 FCFA/l, sugared)" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [2045]
-- Ley 1/2024 art. 176 4) b) (30 % + 15.000 FCFA per 1.000): 10000 paid for 1 unit(s) at 0 % vol → 2017
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Impuesto especial (tabaco)", perUnitNum := 15000, perUnitDen := 1000, advBp := 3000, vatBp := 1500, statute := "Ley 1/2024 art. 176 4) b) (30 % + 15.000 FCFA per 1.000)" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [2017]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["Ley 1/2024 art. 155: the 5 % list (children's food, hygiene, milk …) sits inside the food and other lines, taxed at 15 %; exemptions not read", "Ley 1/2024 art. 176 3): energy drinks (+100 FCFA/l) and other soft drinks (+30 FCFA/l) not separated from sugared drinks (+50)", "fuel: no impuesto especial line read for petrol and diesel"]

end GqGlobal
