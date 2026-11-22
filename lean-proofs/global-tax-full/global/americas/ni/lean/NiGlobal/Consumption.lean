import NiGlobal.Pit

/-!
# Nicaragua 2025: IVA (5111); ISC (5121) unsupported

Source: Ley N° 822, Ley de Concertación Tributaria, La Gaceta N° 241 of 17.12.2012 (`world/B12-latin-america/ni/src/
raw822.txt`, the 1.x builder's copy) with Ley 891 (2014) read by the 1.x builder; the 2019 reform (Ley 987) was not
reached: grade B.
* **art. 109**: "La alícuota del IVA es del quince por ciento (15%), salvo en las exportaciones … cero por ciento".
* **art. 127** (exenciones objetivas, goods): 1 "Libros, folletos, revistas, materiales escolares y científicos,
  diarios"; 2 "Medicamentos, vacunas y sueros de consumo humano"; 4-7 domestic unprocessed agricultural goods, rice,
  eggs, tortilla, salt, flour, milk (the basket's food line read as these basic foods, flagged).
* Services exemptions (Título III, Capítulo V) were not read in a clean text: services are taxed at 15 % here and
  flagged.
* **ISC, art. 151**: "Las alícuotas … están contenidas en los Anexos I, II y III": the annexes as amended by Ley 987
  were not read: unsupported.
-/

namespace NiGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon NiGlobal

def vat : Vat :=
  { name := "Impuesto al Valor Agregado", standard := 1500,
    classOf := fun gd => match gd with
      | .food | .medicines | .books | .newspapers => .exempt
      | _ => .standard }

def vatStatute : String := "Ley 822 art. 109 (15 %), art. 127 num. 1, 2, 4-7"

def vatF : Family := vatFamily "Impuesto al Valor Agregado" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 108: \"Los tributos se crean, modifican y derogan por ley\" (`ni/law/const_articulo-108.md`). no law read in this build levies a general sales or turnover tax beside the VAT of the 5111 row (laws read include: Ley 822 arts. 109, 127; Ley 822 art. 52 (30 %); Ley 822 arts. 53, 87, 89 (Ley 891 of 2014, Ley 987 of 2019); 1.x model (see its summary.json); Ley 822 arts. 82, 83, 87 (Ley 891, Ley 987); Decreto 975 arts. 11 (2), 16 as reformed by Decreto Presidencial 06-2019)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .education || s.good == .health || s.good == .transport || s.good == .rent || s.good == .financial || s.good == .insurance || s.good == .electricity || s.good == .water) "IVA services exemptions (Ley 822 Título III Cap. V, as amended by Ley 987) not read: services taxed at 15 %"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic || s.good == .petrol || s.good == .diesel) "ISC (Ley 822 art. 151, Anexos I-III as amended by Ley 987) not read: not charged"
  ++ when (!g.consumption.isEmpty) "food read as the basic foods of art. 127 num. 4-7 (exempt); other food is taxed at 15 %"

#guard vat.embedded { good := .clothing, amount := 1150 } == 150
#guard vat.embedded { good := .medicines, amount := 1150 } == 0

end NiGlobal.Consumption
