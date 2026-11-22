import SvGlobal.Pit

/-!
# El Salvador 2025: Impuesto a la Transferencia de Bienes Muebles y a la Prestación de Servicios (5111); FOVIAL, tobacco, alcohol and soft-drink taxes (5121)

Source: Ley de Impuesto a la Transferencia de Bienes Muebles y a la Prestación de Servicios, D.L. 296 of 24 July 1992
(D.O. 143, T. 316, 31 July 1992), Asamblea Legislativa consolidated text (Índice Legislativo, `leyes-y-decretos/view/3544`,
fetched 2026-11-21; `sv/law/ley_iva_dl296_asamblea.pdf`, ARCHIVE_INDEX.tsv). Its reform list runs to D.L. 586 of 20 May
2026; the 2025-2026 entries are special-purpose decrees (projects, CEL contracts, renewable energy, statistics) that do not
touch arts. 46 or 54. Grade A.
* **Art. 54**: "LA TASA DEL IMPUESTO ES EL TRECE POR CIENTO" (reform (2), D.L. 370 of 1995); no reduced rate.
* **Art. 46 (exempt services)**: a) health services by public institutions and those of public utility; b) rent of
  dwellings; e) education by institutions authorised by the Ministry of Education; f) interest on deposits and loans; h)
  water and sewerage by public institutions; i) "De transporte público terrestre de pasajeros"; j) "SEGUROS DE PERSONAS,
  EN LO QUE SE REFIERE AL PAGO DE LAS PRIMAS".
* No exemption for food, medicines, electricity, fuel or books in the Act: all taxed at 13 %.

**Excises (pass 12, grade B - the compilations are of August 2022 and later reforms were not checked (FT reviewer 6); Ministerio de Hacienda "Índice Legislativo" compilations, Wayback captures of 23 Aug 2022,
`sv/law/mh_dc58*.pdf`; reforms after August 2022 not checked):**
* **FOVIAL: Ley del Fondo de Conservación Vial (D.L. 208/2000) art. 26**: "EL VALOR DE LA CONTRIBUCIÓN DE CONSERVACIÓN
  VIAL SERÁ DE VEINTE CENTAVOS DE DÓLAR AMERICANO (US $0.20) POR GALÓN DE DIESEL, GASOLINAS O SUS MEZCLAS": 0.20 /
  3.785 per litre. **COTRANS** (US$ 0.10 per gallon, Ley transitoria de estabilización de tarifas del transporte) is not
  held: not charged (lower bound). **Ley de Impuesto Especial sobre Combustibles (D.L. 225/2009) art. 3**: ad valorem
  1 % / 0.5 % / 0 % by the international reference price of the barrel (above US$ 70: 0 %); the quarterly reference
  price is not an input: not charged, flagged.
* **Tobacco: Ley de Impuestos sobre Productos del Tabaco (D.L. 539/2004, reform D.L. 235/2009) art. 4**: A) "$0.0225
  por cada cigarro, cigarrillo, cigarrito"; B) "treinta y nueve por ciento (39%) sobre el precio sugerido de venta al
  consumidor declarado, excluyendo el [IVA] y el Impuesto Específico" - the ad valorem stays inside its own base, so it
  is 39 % of (price / 1.13 - specific) (custom line `tobDuty`). Puros/habanos 100 % and picado per gram: other tobacco
  not charged (flagged).
* **Alcohol: Ley Reguladora de la Producción y Comercialización del Alcohol y de las Bebidas Alcohólicas (D.L.
  640/1996, reforms D.L. 239/2009 and 462/2010) art. 43**: ad valorem 8 % on the suggested price "excluyendo los
  impuestos establecidos en la presente Ley y el [IVA]" (the kernel line's value before excise and VAT), plus the tax
  on alcohol content per 1 % vol per litre: cerveza 0.0900, vinos 0.0900, ron > 37 % and vodka > 37 % 0.0900, whisky,
  gin, licores 0.1600: US$ 9.00 per litre of pure alcohol for beer, wine and spirits (whisky, gin and liqueurs at
  US$ 16.00 flagged). A line without `abvBp` pays only the ad valorem part.
* **Soft drinks: Ley de Impuesto sobre las Bebidas Gaseosas, Isotónicas, Fortificantes o Energizantes, Jugos, Néctares,
  Refrescos y Preparaciones Concentradas (D.L. 237/2009) art. 4 B) 1**: 10 % on the suggested price excluding this tax
  and IVA (non-alcoholic drinks read as carbonated; juices and isotonic drinks 5 %, energy drinks + US$ 0.20 per litre,
  flagged).
-/

namespace SvGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon SvGlobal

def vat : Vat :=
  { name := "Impuesto a la Transferencia de Bienes Muebles y a la Prestación de Servicios (IVA)", standard := 1300,
    classOf := fun gd => match gd with
      | .health | .rent | .education | .financial | .water | .transport | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "D.L. 296/1992 art. 54 (13 %), art. 46 a), b), e), f), h), i), j) (exempt services); Asamblea consolidated text to D.L. 586/2026"

def vatF : Family := vatFamily "Impuesto a la Transferencia de Bienes Muebles y a la Prestación de Servicios (IVA)" vat vatStatute .vat .central

def lines : List ExLine :=
  [{ good := .petrol, name := "Contribución de Conservación Vial (FOVIAL)", num := 20000, den := 378500, statute := "Ley del Fondo de Conservación Vial art. 26: US$ 0.20 per gallon" },
    { good := .diesel, name := "Contribución de Conservación Vial (FOVIAL)", num := 20000, den := 378500, statute := "Ley del Fondo de Conservación Vial art. 26: US$ 0.20 per gallon" },
    { good := .beer, name := "Impuestos sobre bebidas alcohólicas (cerveza)", num := 9, pure := true, advBp := 800, vatBp := 1300, statute := "D.L. 640/1996 art. 43: 8 % ad valorem + US$ 0.09 per 1 % vol per litre (22.03)" },
    { good := .wine, name := "Impuestos sobre bebidas alcohólicas (vino)", num := 9, pure := true, advBp := 800, vatBp := 1300, statute := "D.L. 640/1996 art. 43: 8 % ad valorem + US$ 0.09 per 1 % vol per litre (22.04)" },
    { good := .spirits, name := "Impuestos sobre bebidas alcohólicas (destiladas)", num := 9, pure := true, advBp := 800, vatBp := 1300, statute := "D.L. 640/1996 art. 43: 8 % ad valorem + US$ 0.09 per 1 % vol per litre (22.08.40.10 ron, 22.08.60 vodka > 37 %)" },
    { good := .nonAlcoholic, name := "Impuesto sobre bebidas gaseosas", advBp := 1000, vatBp := 1300, statute := "D.L. 237/2009 art. 4 B) 1 (10 %)" }]

def exciseF : Family :=
  { name := "5121 excises", covers := [.excise],
    run := fun _ g _ => exciseCharges lines g.consumption }

/-- Ley de Impuestos sobre Productos del Tabaco art. 4 A): US$ 0.0225 per cigarette (`quantity` in thousandths of a stick). -/
def tobSpecific (s : Spend) : Int := divR .down (s.quantity * 225) (10000 * 1000)
/-- art. 4 B): 39 % of the suggested price net of IVA (13 %) and of the specific tax; the ad valorem stays in its base. -/
def tobDuty (s : Spend) : Int :=
  tobSpecific s + divR .down (3900 * pos (divR .down (pos s.amount * BP) 11300 - tobSpecific s)) BP
def tobaccoF : Family :=
  { name := "5121 tabaco", covers := [.excise], run := fun _ g _ => g.consumption.filterMap fun s =>
      if s.good == .cigarettes then
        some (charge .excise "Impuestos sobre productos del tabaco" s.amount id (fun _ => tobDuty s) (event := s.good.name)
          (bearer := .consumer) (statute := "Ley de Impuestos sobre Productos del Tabaco (D.L. 539/2004) art. 4 A), B)"))
      else none }

def families : List Family := [vatF, exciseF, tobaccoF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 231: \"No pueden imponerse contribuciones sino en virtud de una ley y para el servicio público\" (`sv/law/const_art-231.md`). no law read in this build levies a general sales or turnover tax beside the VAT of the 5111 row (laws read include: D.L. 296/1992 arts. 46, 54; Ley del Fondo de Conservación Vial art. 26; D.L. 539/2004 art. 4 (reform D.L. 235/2009); D.L. 640/1996 art. 43 (reforms D.L. 239/2009, 462/2010); D.L. 237/2009 art. 4; Ley de Impuesto sobre la Renta (D.L. 134/1991) art. 41 (D.L. 957/2011): 30 %)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .health) "health services read as public or public-utility providers (exempt, art. 46 a)); private health services are taxed at 13 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .petrol || s.good == .diesel) "fuel: FOVIAL only; COTRANS (US$ 0.10/gal, law not held) and the D.L. 225/2009 ad valorem (0-1 % by the barrel reference price) not charged (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .tobaccoOther) "other tobacco (puros 100 %, picado per gram) not charged"
  ++ when (g.consumption.any fun s => s.good == .spirits) "spirits at US$ 0.09 per % vol per litre (rum, vodka > 37 %); whisky, gin, liqueurs US$ 0.16 (upper rate not applied)"
  ++ when (g.consumption.any fun s => s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .cigarettes || s.good == .nonAlcoholic) "the suggested consumer price taken equal to the price paid; non-alcoholic drinks read as carbonated (10 %)"

#guard vat.embedded { good := .clothing, amount := 1130 } == 130
#guard vat.embedded { good := .food, amount := 1130 } == 130
#guard vat.embedded { good := .rent, amount := 1130 } == 0
#guard vat.embedded { good := .transport, amount := 1130 } == 0
-- 100 litres of petrol: FOVIAL 100 x 0.20 / 3.785 = 5.28
#guard (lines.find? (·.good == .petrol)).get!.duty { good := .petrol, amount := 120, quantity := 100000 } == 5
-- 100 litres of beer at 5 % vol for US$ 300: 5 l pure x 9 = 45; 300 / 1.13 = 265, less 45 = 220, / 1.08 = 203, 8 % = 16
#guard (lines.find? (·.good == .beer)).get!.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 61
-- 1,000 cigarettes for US$ 226: specific 22.5 -> 22; 226 / 1.13 = 200, less 22 = 178, 39 % = 69.4
#guard tobDuty { good := .cigarettes, amount := 226, quantity := 1000000 } == 91
-- soft drinks US$ 113: 100 net of IVA, / 1.10 = 90, 10 % = 9
#guard (lines.find? (·.good == .nonAlcoholic)).get!.duty { good := .nonAlcoholic, amount := 113 } == 9

end SvGlobal.Consumption
