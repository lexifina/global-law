import EsGlobal.Pit

/-!
# Spain 2025 (territorio común): Impuesto sobre el Valor Añadido (5111) and Impuestos Especiales (5121)

Sources: BOE legislación consolidada (`es/law/liva.html` Ley 37/1992, `es/law/liiee.html` Ley 38/1992, current text
"Última actualización publicada el 07/10/2026"; sha256 in `law/SHA256SUMS`). Each provision used carries BOE's
amendment notes, which date the 2025 wording: art. 91 last amended by Ley 7/2024 and, "con efectos desde el 1 de
enero de 2025", by RDL 4/2024; art. 60 "con efectos desde el 1 de enero de 2025" by Ley 7/2024 (disp. final 2.9);
arts. 39 and 50 unchanged since 2016 and 2013.
* **LIVA art. 90 Uno**: "El Impuesto se exigirá al tipo del 21 por ciento"; **art. 91 Uno** 10 %: 1.1.º food
  products, 1.4.º "Las aguas aptas para la alimentación humana", 2.1.º "Los transportes de viajeros", 2.2.º "Los
  servicios de hostelería, acampamento y balneario, los de restaurantes", 2.6.º entry to museums, cinemas, theatres;
  **art. 91 Dos** 4 %: 1.1.º basic foods (bread, milk, eggs, fruit, vegetables ...), 1.2.º "Los libros, periódicos y
  revistas", 1.3.º "Los medicamentos de uso humano". Exemptions art. 20 Uno (medical care, education, insurance,
  financial, residential letting).
* **LIIEE art. 50.1**: epígrafe 1.2.2 "Las demás gasolinas sin plomo: 400,69 euros por 1.000 litros de tipo general y
  72 euros por 1.000 litros de tipo especial"; epígrafe 1.3 "Gasóleos para uso general: 307 euros ... y 72 euros".
  **Art. 60.1 epígrafe 2**: cigarettes "Tipo proporcional: 48,5 por 100. Tipo específico: 33,50 euros por cada 1.000
  cigarrillos. El importe del impuesto no puede ser inferior al tipo único de 150 euros por cada 1.000 cigarrillos."
  **Art. 39**: "El impuesto se exigirá al tipo de 958,94 euros por hectolitro de alcohol puro".

## FT review (2026-11-21, third pass): heating oil
Same BOE consolidated text (`es/law/liiee.txt`). **Ley 38/1992 art. 50.1, epígrafe 1.4**: "Gasóleos utilizables como
carburante en los usos previstos en el apartado 2 del artículo 54 y, en general, como combustible: 78,71 euros por
1.000 litros de tipo general y 18 euros por 1.000 litros de tipo especial" (96,71 euros, the two summed as for
epígrafes 1.2.2 and 1.3). The household's `heatingOil` is gasóleo used as combustible.
-/

namespace EsGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Impuesto sobre el Valor Añadido", standard := 2100, reduced := 1000, superReduced := 400, threshold := 0,
    classOf := fun gd => match gd with
      | .food | .water | .transport | .hotels | .restaurants => .reduced
      | .books | .newspapers | .medicines => .superReduced
      | .health | .education | .insurance | .financial | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "Ley 37/1992 art. 90 (21 %), art. 91 Uno (10 %), Dos (4 %); art. 20 Uno (exenciones)"

def excise : Excise :=
  { rates := [
      { good := .petrol, name := "Impuesto sobre Hidrocarburos (gasolina)", perUnitNum := 47269, perUnitDen := 100000, statute := "Ley 38/1992 art. 50.1 epígrafe 1.2.2: 400,69 + 72 EUR / 1.000 l" },
      { good := .diesel, name := "Impuesto sobre Hidrocarburos (gasóleo)", perUnitNum := 379, perUnitDen := 1000, statute := "Ley 38/1992 art. 50.1 epígrafe 1.3: 307 + 72 EUR / 1.000 l" },
      { good := .cigarettes, name := "Impuesto sobre las Labores del Tabaco (cigarrillos)", perUnitNum := 335, perUnitDen := 10000, adValoremBp := 4850, minNum := 150, minDen := 1000, statute := "Ley 38/1992 art. 60.1 epígrafe 2: 48,5 % + 33,50 EUR / 1.000, mínimo 150 EUR / 1.000" },
      { good := .spirits, name := "Impuesto sobre el Alcohol y Bebidas Derivadas", perUnitNum := 95894, perUnitDen := 10000, onPureAlcohol := true, statute := "Ley 38/1992 art. 39: 958,94 EUR / hl de alcohol puro" },
      { good := .heatingOil, name := "Impuesto sobre Hidrocarburos (gasóleo de calefacción)", perUnitNum := 9671, perUnitDen := 100000, statute := "Ley 38/1992 art. 50.1 epígrafe 1.4: 78,71 + 18 EUR / 1.000 l" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 IVA, 5121 IIEE", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["ES 5111/5121: territorio común (Canarias IGIC, Ceuta and Melilla IPSI not modelled)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["food at 10 % (art. 91 Uno 1.1.º); the basic foods of art. 91 Dos 1.1.º (bread, milk, eggs, fruit, vegetables, oils ...) are 4 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer) then ["Impuesto sobre la Cerveza (by degree Plato, art. 26) not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .recreation) then ["cultural entries at 10 % (art. 91 Uno 2.6.º) not separated from recreation (21 %)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .wine) then ["Impuesto sobre el Vino y Bebidas Fermentadas not modelled (its article not read)"] else [])

#guard vat.embedded { good := .clothing, amount := 121 } == 21
#guard vat.embedded { good := .food, amount := 110 } == 10
#guard vat.embedded { good := .books, amount := 104 } == 4
#guard excise.duty { good := .petrol, amount := 1600, quantity := 1000000 } == 472
#guard excise.duty { good := .diesel, amount := 1500, quantity := 1000000 } == 379
-- 1 000 cigarettes at 200 EUR: 97 + 33 < 150 (the tipo único binds); at 400 EUR: 194 + 33
#guard excise.duty { good := .cigarettes, amount := 200, quantity := 1000000 } == 150
#guard excise.duty { good := .cigarettes, amount := 400, quantity := 1000000 } == 227
#guard excise.duty { good := .spirits, amount := 1500, quantity := 100000, abvBp := 4000 } == 383
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 96

end EsGlobal.Consumption
