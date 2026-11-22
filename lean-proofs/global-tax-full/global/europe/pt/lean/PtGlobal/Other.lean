import PtGlobal.Pit
import TaxKernel.Global2

/-!
# PT 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Contribuição extraordinária sobre o setor energético; derrama estadual (recorded under CIT)): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor here: CESE is an energy-sector levy; derrama estadual is under CIT (P2)


## 5200 Imposto único de circulação (categoria B) (pass 11, kernel 2.4.0, grade A)
Source: Código do IUC, info.portaldasfinancas.gov.pt (art. 2, 5, 10 and the table images of art. 10, redação da Lei n.º 82/2023).
* art. 2.º n.º 1 b): category B = passenger cars first registered in Portugal or in the EU/EEA after the code entered into force (1 July 2007)
* art. 10.º n.º 1: cilindrada component up to 1 250 cm3 31,77 EUR, to 1 750 63,74, to 2 500 127,35, above 435,84; CO2 component NEDC up to 120 g/km (WLTP 140) 65,15, to 180 (205) 97,63, to 250 (260) 212,04, above 363,25
* art. 10.º n.º 2: first registration after 1 January 2017: an additional 31,77 EUR for NEDC 180-250 g/km (WLTP 205-260) and 63,74 EUR above
* art. 10.º n.º 3: the sum is multiplied by 1,00 (first registration 2007), 1,05 (2008), 1,10 (2009), 1,15 (2010 and later)
* art. 5.º n.º 1 e): exclusively electric vehicles are exempt
-/

namespace PtGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

/-- Código do IUC art. 10 n.º 1: cilindrada component (cents) -/
def p11ptCc : QtyTable := QtyTable.ofCeilings [(1250, 3177), (1750, 6374), (2500, 12735)] 43584
/-- art. 10 n.º 1: CO2 component, NEDC and WLTP columns (cents) -/
def p11ptCo2N : QtyTable := QtyTable.ofCeilings [(120, 6515), (180, 9763), (250, 21204)] 36325
def p11ptCo2W : QtyTable := QtyTable.ofCeilings [(140, 6515), (205, 9763), (260, 21204)] 36325
/-- art. 10 n.º 2: taxas adicionais for a first registration after 1 January 2017 (cents) -/
def p11ptAddN : QtyTable := QtyTable.ofCeilings [(180, 0), (250, 3177)] 6374
def p11ptAddW : QtyTable := QtyTable.ofCeilings [(205, 0), (260, 3177)] 6374
def p11ptIuc : String := "Imposto único de circulação (categoria B)"
/-- multiplierBp = the art. 10 n.º 3 coefficient (1,00 / 1,05 / 1,10 / 1,15) in hundredths, which also turns cents into euros -/
def p11ptB (f t : Nat) (ps : List (VehicleAttr × QtyTable)) (bp : Int) (st : String) : VehicleTax :=
  { name := p11ptIuc, kinds := ["car"], fuels := [.petrol, .diesel, .hybrid, .pluginHybrid, .lpg, .cng, .hydrogen, .other],   regFrom := f, regTo := t, parts := ps, multiplierBp := bp, statute := st }
def p11ptVeh : List VehicleTax :=
  [{ name := p11ptIuc, kinds := ["car"], fuels := [.electric], regFrom := 2007,    statute := "Código do IUC art. 5.º n.º 1 e): exclusively electric vehicles are exempt" },  p11ptB 2020 0 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2W), (.co2GKm, p11ptAddW)] 115 "Código do IUC art. 10.º n.º 1, 2 (WLTP columns), n.º 3 (coefficient 1,15)",  p11ptB 2017 2019 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2N), (.co2GKm, p11ptAddN)] 115 "Código do IUC art. 10.º n.º 1, 2 (NEDC columns), n.º 3 (coefficient 1,15)",  p11ptB 2010 2016 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2N)] 115 "Código do IUC art. 10.º n.º 1 (NEDC), n.º 3 (coefficient 1,15)",  p11ptB 2009 2009 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2N)] 110 "Código do IUC art. 10.º n.º 1 (NEDC), n.º 3 (coefficient 1,10)",  p11ptB 2008 2008 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2N)] 105 "Código do IUC art. 10.º n.º 1 (NEDC), n.º 3 (coefficient 1,05)",  p11ptB 2007 2007 [(.engineCcm, p11ptCc), (.co2GKm, p11ptCo2N)] 100 "Código do IUC art. 10.º n.º 1 (NEDC), n.º 3 (coefficient 1,00)"]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Imposto único de circulação (categoria B) (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p11ptVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["PT 5200 Imposto único de circulação (categoria B) pass 11: Portal das Finanças, codigos tributarios, read 2026-11-21 (`pt/law/iuc2_portal.txt`, `iuc5_portal.txt`, `iuc10_portal.txt`; the art. 10 n.º 1 and 2 tables are images: `iuc10_oe2024_01.png`, `iuc10_oe2024_02.png`, read by OCR); OE 2025 (Lei 45-A/2024, `pt/law/Lei_45_A_2024.txt`) changes no IUC rate (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)"] else [])
  ++ (if !(vehicleTaxUnknown "Imposto único de circulação (categoria B)" p11ptVeh g).isEmpty then ["5200 Imposto único de circulação (categoria B): a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Imposto único de circulação (categoria B)" p11ptVeh g).isEmpty then ["5200 Imposto único de circulação (categoria B): a vehicle no rule reaches: cars first registered before July 2007 (category A, art. 9), motorcycles, goods vehicles and other categories (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 IUC: CO2 of a car first registered from 2020 is read in the WLTP column, earlier ones in the NEDC column (Lei 119/2019 note); a car of 2007 is taken as registered after 1 July 2007; amounts rounded down to whole euros"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .diesel) then ["5200 adicional de IUC (Lei 82-B/2014 art. 216, kept by Lei 45-A/2024 art. 113) on diesel cars not modelled (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg) then ["5200 ISV (Código do ISV) on a car registered in the year not modelled (grade C)"] else [])

#guard p11amt p11ptVeh { kind := "car", fuel := .petrol, engineCcm := 1499, co2GKm := 130, firstRegYear := 2021 } == 148
#guard p11amt p11ptVeh { kind := "car", fuel := .diesel, engineCcm := 1998, co2GKm := 150, firstRegYear := 2021 } == 258
#guard p11amt p11ptVeh { kind := "car", fuel := .petrol, engineCcm := 2998, co2GKm := 210, firstRegYear := 2018 } == 781
#guard p11amt p11ptVeh { kind := "car", fuel := .petrol, engineCcm := 1600, co2GKm := 150, firstRegYear := 2008 } == 169
#guard p11amt p11ptVeh { kind := "car", fuel := .petrol, engineCcm := 3000, co2GKm := 270, firstRegYear := 2024 } == 992
#guard p11amt p11ptVeh { kind := "car", fuel := .electric, engineCcm := 0, co2GKm := 0, firstRegYear := 2022 } == 0
#guard p11amt p11ptVeh { kind := "car", fuel := .petrol, engineCcm := 1499, co2GKm := 130, firstRegYear := 2005 } == -1

end PtGlobal.Other
