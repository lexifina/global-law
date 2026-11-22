import UyGlobal.Pit

/-!
# Uruguay 2025: IVA (5111); IMESI (5121) unsupported

Source: Texto Ordenado 1996 (DGI), "Documento actualizado durante su vigencia", i.e. until the T.O. 2023 approved on
04/04/2024 (`world/B12-latin-america/uy/src/to1996.txt`). The T.O. 2023 on IMPO needs a subscription: the 2024-2025
state was not read (grade B).
* **Título 10 art. 16**: "A) Básica del 22% (veintidós por ciento). B) Mínima del 10% (diez por ciento)".
* **art. 18** (tasa mínima): A) bread, fresh meat and fish, oils, rice, flour, pasta, salt, sugar, yerba, coffee, tea
  (the basket's food line read as these: 10 %); B) "Medicamentos y especialidades farmacéuticas"; C) hotel lodging;
  D) health services outside employment.
* **art. 19** (exonerations): 1) E) "Combustibles derivados del petróleo, excepto fueloil y gasoil" (petrol exempt,
  diesel taxed); H) "Diarios, periódicos, revistas, libros"; I) basic family water supply; 2) A), E) interest and
  banking operations; C) "Arrendamientos de inmuebles"; D), M) insurance against fire, death, old age.
* **IMESI (Título 11)**: rates fixed by the executive within statutory maxima (decrees not read): unsupported.
-/

namespace UyGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon UyGlobal

def vat : Vat :=
  { name := "Impuesto al Valor Agregado", standard := 2200, reduced := 1000,
    classOf := fun gd => match gd with
      | .food | .medicines | .hotels | .health => .reduced
      | .petrol | .books | .newspapers | .water | .financial | .rent | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "T.O. 1996 Título 10 arts. 16, 18, 19"

def vatF : Family := vatFamily "Impuesto al Valor Agregado" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic || s.good == .petrol || s.good == .diesel) "IMESI (T.O. Título 11): rates set by decree within statutory maxima, not read: not charged"
  ++ when (g.consumption.any fun s => s.good == .education || s.good == .transport) "education and passenger transport: exonerations not identified in art. 19 as read (subjective exemptions of Título 3 institutions not modelled): taxed at 22 %"
  ++ when (!g.consumption.isEmpty) "food read as the basic foods of Título 10 art. 18 A) (10 %); other food is at 22 %"

#guard vat.embedded { good := .clothing, amount := 1220 } == 220
#guard vat.embedded { good := .food, amount := 1100 } == 100
#guard vat.embedded { good := .rent, amount := 1220 } == 0

end UyGlobal.Consumption
