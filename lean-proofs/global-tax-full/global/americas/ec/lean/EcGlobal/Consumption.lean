import EcGlobal.Pit

/-!
# Ecuador 2025: IVA (5111); ICE (5121) unsupported

Source: Ley de Régimen Tributario Interno, SRI consolidation "Última reforma: 24 de octubre de 2025"
(`world/B12-latin-america/ec/src/lrti.txt`), which carries every 2024-2025 amendment note.
* **art. 65**: "La tarifa del impuesto al valor agregado es del 13%" … "En ningún caso la tarifa podrá ser inferior al
  13% ni mayor al 15%"; note: "Decreto Ejecutivo No. 470, publicado en Registro Oficial Suplemento 700 de 10 de
  Diciembre del 2024 … se mantiene la modificación de la tarifa general … del 13% al 15% para el año 2025": 15 %.
* **art. 55** (tarifa cero, goods): 1-3 food in its natural state, milk, bread, sugar, oils and listed staples (the
  basket's food line is read as these: processed food is taxed, flagged); 6 medicines; 7 "Papel bond, papel periódico
  y libros"; 11 "Energía Eléctrica".
* **art. 56** (tarifa cero, services): 1 passenger transport; 2 health; 3 rent of housing; 4 water, sewerage; 5
  education. (Num. 11, financial services, derogated by DLE 742 of 2023: their present treatment not read.)
* **ICE, art. 82**: the Grupo I ad valorem table is "ver Registro Oficial Suplemento 111 de 31 de diciembre de 2019,
  página 17" (not in the text) and the specific rates for cigarettes and alcohol are adjusted every year (art. 82,
  Disposición: "ajustada anualmente"): unsupported.
-/

namespace EcGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon EcGlobal

def vat : Vat :=
  { name := "Impuesto al Valor Agregado", standard := 1500,
    classOf := fun gd => match gd with
      | .food | .medicines | .books | .newspapers | .electricity | .water | .transport | .health | .rent | .education => .zero
      | .financial | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "LRTI art. 65 (15 % for 2025, D.E. 470), art. 55 num. 1-3, 6, 7, 11, art. 56 num. 1-5"

def vatF : Family := vatFamily "Impuesto al Valor Agregado" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 301: \"Sólo por iniciativa de la Función Ejecutiva y mediante ley sancionada por la Asamblea Nacional se podrá establecer, modificar, exonerar o extinguir impuestos\" (`ec/law/const_art-301.md`). no law read in this build levies a general sales or turnover tax beside the VAT of the 5111 row (laws read include: LRTI arts. 55, 56, 65; LRTI art. 37 (25 %); LRTI arts. 37, 39, 39.2 num. 4; 1.x model (see its summary.json); LRTI art. innumerado (enajenación de acciones), art. 9 num. 14, 24; IESS Resolución C.D. 515 de 2016, Disposición Transitoria Primera)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .financial || s.good == .insurance) "financial services and insurance: art. 56 num. 11 derogated (2023), present treatment not read: not charged"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic) "ICE (LRTI art. 82): Grupo I table published only in R.O. S. 111 (2019) and specific rates adjusted yearly: not charged"
  ++ when (!g.consumption.isEmpty) "food read as natural/basic food (art. 55 num. 1-3, zero); processed food not on the list is taxed at 15 %"

#guard vat.embedded { good := .clothing, amount := 1150 } == 150
#guard vat.embedded { good := .food, amount := 1150 } == 0
#guard vat.embedded { good := .education, amount := 1150 } == 0

end EcGlobal.Consumption
