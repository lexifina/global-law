import PyGlobal.Pit

/-!
# Paraguay 2025: IVA (5111); ISC (5121) unsupported

Source: Ley N° 6380/19 "De modernización y simplificación del sistema tributario nacional", DNIT portal text
(`world/B12-latin-america/py/src/l6380page.txt`; the act as enacted; later amendments not checked: grade B).
* **art. 90**: 5 % for a) rent of housing, c) the family basket (rice, pasta, vegetable oil, yerba mate, milk, eggs,
  flour, iodised salt), d), e) agricultural, horticultural, fruit and livestock products, f) "medicamentos de uso
  humano"; "g) 10% (diez por ciento) para todos los demás casos". art. 93: prices are quoted "con el IVA incluido".
* **art. 100** exonerations: 1 d) "Libros y periódicos"; i) "Los combustibles derivados del petróleo, incluidos los
  biocombustibles"; 3 a), d) interest and bank deposits; f) education; h) urban and interurban public passenger
  transport.
* **ISC, arts. 112-120**: the tables give "Tasa Máxima en %"; the rates in force are fixed by the executive (art. 120,
  decrees not read): unsupported.
-/

namespace PyGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon PyGlobal

def vat : Vat :=
  { name := "Impuesto al Valor Agregado", standard := 1000, reduced := 500,
    classOf := fun gd => match gd with
      | .food | .medicines | .rent => .reduced
      | .books | .newspapers | .petrol | .diesel | .financial | .education | .transport => .exempt
      | _ => .standard }

def vatStatute : String := "Ley 6380/19 art. 90 (10 %; 5 % a), c)-f)), art. 100 1 d), i), 3 a), d), f), h)"

def vatF : Family := vatFamily "Impuesto al Valor Agregado" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 179: \"Todo tributo, cualquiera sea su naturaleza o denominación, será establecido exclusivamente por la ley\" (`py/law/const_art-179.md`). no law read in this build levies a general sales or turnover tax beside the VAT of the 5111 row (laws read include: Ley 6380/19 arts. 85-100; Ley 6380/19 art. 21 (10 %); Ley 6380/19 art. 43 2 (IDU 15 %, non-resident); 1.x model (see its summary.json); Ley 6380/2019 arts. 53, 56, 59, 60; Ley 98/1992 (not read))." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic || s.good == .petrol || s.good == .diesel) "ISC (Ley 6380 arts. 112-120): only maximum rates in the act; the rates in force are set by decree (not read): not charged"
  ++ when (!g.consumption.isEmpty) "food read as the 5 % basket and fresh produce of art. 90 c)-e); other food is at 10 %"

#guard vat.embedded { good := .clothing, amount := 1100 } == 100
#guard vat.embedded { good := .food, amount := 1050 } == 50
#guard vat.embedded { good := .petrol, amount := 1100 } == 0

end PyGlobal.Consumption
