import DoGlobal.Pit

/-!
# Dominican Republic 2025: ITBIS (5111); Impuesto Selectivo al Consumo on alcohol and tobacco (5121, lower bound)

Source: Código Tributario (Ley 11-92), Título III, DGII consolidated PDF (dgii.gov.do, "Modificado: 18/06/2019",
fetched 2026-11-21; `do/law/ct_titulo3_itbis.pdf`). Grade B (see the rate condition below).
* **Art. 335**: the tax is paid "con una tasa del 16%*" with the DGII note: the applicable rate is the one in **art. 345**
  as amended by Ley 253-12: "i) 18% para el año 2013; ii) 18% para el año 2014; iii) 16% a partir del año 2015";
  **Párrafo I**: "La reducción contemplada ... se aplicara en la medida que permita alcanzar y mantener la meta de
  presión tributaria al año 2015" (Ley 01-12 art. 26, indicator 3.25). The condition was not met and the 18 % rate is
  the one administered in 2025 (a fact outside the text: flagged, hence grade B). Párrafo II: reduced rates for listed
  goods (yogurt, butter, coffee, oils ...) reaching 16 % "a partir" of 2016.
* **Art. 343 (exempt goods)**: unprocessed food (live animals, fresh meat, vegetables, fruit, rice ...), "Agua natural",
  gasolines and other fuels (taxed by separate fuel levies), "Energía eléctrica", "Medicamentos", books 4901 and
  periodicals 4902.
* **Art. 344 (exempt services)**: "1) Servicios financieros, incluyendo seguros. ... 3) Servicios de transporte
  terrestre de personas y de carga. 4) Servicios de electricidad, agua y recogida de basura. 5) Servicios de alquiler de
  viviendas. 6) Servicios de salud. 7) Servicios educativos y culturales."

**Pass 12 (2026-11-21), ISC on alcohol and tobacco (grade B, lower bound):** Código Tributario Título IV (DGII
consolidated PDF, `do/law/ct_titulo4_isc.pdf`) **art. 375** (Ley 253-12): Párrafo I table, ISC específico per litre of
absolute alcohol, "A partir de 2017" RD$ 595.4 for every heading 22.03-22.08 (unified from 2017, Párrafo VI); Párrafo
II: "diez por ciento (10%) sobre el precio al por menor"; Párrafo VII cigarettes per cajetilla of 20, 2015 column
RD$ 50.0 (RD$ 2.50 a cigarette); Párrafo VIII: "veinte por ciento (20%) ad-valorem sobre el precio al por menor".
Párrafos III and IX adjust the specific amounts quarterly by the inflation published by the Banco Central (from 2017
and 2016); the 2025 DGII amounts are not held, so the statutory 2017 / 2015 amounts are charged: a lower bound, since
the adjustment only raises them. The "precio al por menor" is defined in the regulations (not held): read as the price
before ISC and ITBIS (18 %), also a lower bound. A line without `abvBp` pays only the ad valorem part. Fuels (Ley
112-00, indexed), telecommunications (art. 381, 10 %) and insurance (16 %) stay unmodelled.
-/

namespace DoGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon DoGlobal

def vat : Vat :=
  { name := "Impuesto sobre Transferencias de Bienes Industrializados y Servicios", standard := 1800,
    classOf := fun gd => match gd with
      | .food | .water | .petrol | .diesel | .electricity | .medicines | .books | .newspapers | .financial | .insurance | .transport | .rent | .health | .education => .exempt
      | _ => .standard }

def vatStatute : String := "Código Tributario arts. 335, 345 (Ley 253-12: 18 %; the 2015 reduction to 16 % conditional on the tax-pressure target, not applied), 343, 344 (exempt)"

def vatF : Family := vatFamily "Impuesto sobre Transferencias de Bienes Industrializados y Servicios" vat vatStatute .vat .central

def lines : List ExLine :=
  [{ good := .beer, name := "Impuesto Selectivo al Consumo (alcohol)", num := 5954, den := 10, pure := true, advBp := 1000, vatBp := 1800, statute := "Código Tributario art. 375 Párrafo I (RD$ 595.4 per litre of absolute alcohol, 2017 column; indexation not applied), Párrafo II (10 %)" },
    { good := .wine, name := "Impuesto Selectivo al Consumo (alcohol)", num := 5954, den := 10, pure := true, advBp := 1000, vatBp := 1800, statute := "Código Tributario art. 375 Párrafo I (RD$ 595.4 per litre of absolute alcohol, 2017 column; indexation not applied), Párrafo II (10 %)" },
    { good := .spirits, name := "Impuesto Selectivo al Consumo (alcohol)", num := 5954, den := 10, pure := true, advBp := 1000, vatBp := 1800, statute := "Código Tributario art. 375 Párrafo I (RD$ 595.4 per litre of absolute alcohol, 2017 column; indexation not applied), Párrafo II (10 %)" },
    { good := .cigarettes, name := "Impuesto Selectivo al Consumo (cigarrillos)", num := 25, den := 10, advBp := 2000, vatBp := 1800, statute := "Código Tributario art. 375 Párrafo VII (RD$ 50.0 per pack of 20, 2015 column; indexation not applied), Párrafo VIII (20 %)" }]

def exciseF : Family :=
  { name := "5121 excises", covers := [.excise],
    run := fun _ g _ => exciseCharges lines g.consumption }

def families : List Family := [vatF, exciseF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 93 num. 1 a): \"Establecer los impuestos, tributos o contribuciones generales\" (`do/law/const_articulo-093.md`); Constitución art. 243: \"El régimen tributario está basado en los principios de legalidad\" (`do/law/const_articulo-243.md`). no law read in this build levies a general sales or turnover tax beside the VAT of the 5111 row (laws read include: Código Tributario (Ley 11-92) Título III arts. 335, 343, 344, 345 (Ley 253-12); Código Tributario (Ley 11-92) art. 375 (Ley 253-12) Párrafos I, II, VII, VIII; Código Tributario art. 297 (27 %); Código Tributario arts. 305, 306, 308 (Ley 253-12); 1.x model (see its summary.json); Código Tributario arts. 283, 289, 296, 299 m))." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "ITBIS rate: art. 345 iii) sets 16 % from 2015 subject to the tax-pressure target of Ley 01-12 (Párrafo I); the 18 % administered in 2025 is charged"
  ++ when (g.consumption.any fun s => s.good == .food) "food: only the goods listed in art. 343 are exempt and those in art. 345 Párrafo II bear 16 %; processed food 18 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel || s.good == .communication || s.good == .insurance) "ISC on fuels (Ley 112-00, indexed), other tobacco, telecommunications (art. 381, 10 %) and insurance (16 %) not modelled"
  ++ when (g.consumption.any fun s => s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .cigarettes) "ISC alcohol/tobacco: specific amounts of the statute's last column (2017 alcohol, 2015 cigarettes) without the quarterly inflation adjustment (Párrafos III, IX); ad valorem on the price before ISC and ITBIS (the regulation's precio al por menor not held): lower bound"

#guard vat.embedded { good := .clothing, amount := 1180 } == 180
#guard vat.embedded { good := .rent, amount := 1180 } == 0
#guard vat.embedded { good := .books, amount := 1180 } == 0
-- 10 litres of beer at 5 % vol for RD$ 2,000: 0.5 l absolute x 595.4 = 297.7 -> 297; 2,000 / 1.18 = 1,694, less 297 = 1,397, / 1.10 = 1,270, 10 % = 127
#guard (lines.find? (·.good == .beer)).get!.duty { good := .beer, amount := 2000, quantity := 10000, abvBp := 500 } == 424
-- 200 cigarettes for RD$ 3,000: 200 x 2.50 = 500; 3,000 / 1.18 = 2,542, less 500 = 2,042, / 1.20 = 1,701, 20 % = 340
#guard (lines.find? (·.good == .cigarettes)).get!.duty { good := .cigarettes, amount := 3000, quantity := 200000 } == 840

end DoGlobal.Consumption
