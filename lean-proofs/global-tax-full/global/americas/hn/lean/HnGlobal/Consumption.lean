import HnGlobal.Pit

/-!
# Honduras 2025: Impuesto Sobre Ventas (5111); excise (ISC, producción y consumo) grade C

Source: SAR, "Texto consolidado Ley del Impuesto sobre Ventas, Decreto-Ley Número 24, actualizado hasta el Decreto
Legislativo No. 59-2022" (Dirección Nacional Jurídica; sar.gob.hn, fetched 2026-11-21; `hn/law/`). Official
consolidation; amendments 2023-2025 not checked (the next listed reform is Decreto 7-2026): grade B.
* **Art. 6** (consolidated numbering "Artículo 66"): "La tasa general del impuesto es del quince por ciento (15%)";
  "Cuando este impuesto se aplique en la importación o venta de cerveza, aguardiente, licor compuesto y otras bebidas
  alcohólicas, cigarrillos, la tasa será del diez y ocho por ciento (18%)" (also business-class air tickets).
* **Art. 15 exemptions**: a) "artículos esenciales de consumo popular" (Anexo I, Acuerdo Ejecutivo 005-2014); b)
  "productos farmacéuticos para uso humano"; c) "gasolina, diesel, bunker C, kerosene, gas LPG ... libros, diarios o
  periódicos"; d) services: "energía eléctrica, exceptuando todos los abonados residenciales que tengan un consumo ...
  mayor de setecientos cincuenta kilowatios/hora mensual"; "agua potable y alcantarillado"; "de enseñanza; de
  hospitalización"; "transporte terrestre de pasajeros"; "servicios bancarios y financieros"; "primas de seguros de
  personas"; "el arrendamiento de viviendas excepto en el caso de hoteles".
* The 18 % rate on alcoholic drinks and cigarettes is held in the `reduced` slot of the kernel `Vat` (a higher rate).
  Food read as exempt (Anexo I list only: lower bound).
-/

namespace HnGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon HnGlobal

def vat : Vat :=
  { name := "Impuesto Sobre Ventas", standard := 1500, reduced := 1800,
    classOf := fun gd => match gd with
      | .beer | .wine | .spirits | .cigarettes | .tobaccoOther => .reduced
      | .food | .medicines | .petrol | .diesel | .books | .newspapers | .electricity | .water | .education | .health | .transport | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "Ley del ISV (Decreto-Ley 24, consolidado al Decreto 59-2022) art. 6 (15 %; 18 % alcohol and cigarettes), art. 15 a)-d) (exempt)"

def vatF : Family := vatFamily "Impuesto Sobre Ventas" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 205 num. 35: \"Establecer impuestos y contribuciones así como las cargas públicas\" (`hn/law/const_art-205.md`). no law read in this build levies a general sales or turnover tax beside the VAT of the 5111 row (laws read include: Decreto-Ley 24 de 1963 arts. 6, 15 (texto consolidado al Decreto 59-2022); LISR art. 22 (25 %); LISR (Decreto-Ley 25, SAR consolidation to Acuerdo SAR 07-2025) art. 5 num. 3), 5), 6), 7); 1.x model (see its summary.json); LISR art. 10; Reglamento de Aplicación de la Ley del Seguro Social (Acuerdo 193/1971) art. 28)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food: exempt only for the articles listed in Anexo I of Acuerdo Ejecutivo 005-2014; other food 15 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .electricity || s.good == .insurance) "electricity: residential consumption above 750 kWh a month is taxed; insurance: only personal insurance premiums exempt"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) "Impuesto Selectivo al Consumo / producción y consumo and the fuel contribution not modelled"
  ++ when (g.consumption.any fun s => s.good == .hotels) "4 % tourism tax on hotel stays (Ley de Incentivos al Turismo) not modelled"

#guard vat.embedded { good := .clothing, amount := 1150 } == 150
#guard vat.embedded { good := .beer, amount := 1180 } == 180
#guard vat.embedded { good := .medicines, amount := 1150 } == 0

end HnGlobal.Consumption
