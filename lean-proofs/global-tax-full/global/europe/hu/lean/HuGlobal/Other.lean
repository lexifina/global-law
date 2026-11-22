import HuGlobal.Pit
import TaxKernel.Global2

/-!
# HU 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Helyi iparűzési adó (local business tax on adjusted turnover, up to 2 %); KATA/KIVA small-business regimes; windfall/sector surtaxes (2022-2025)): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: model (high revenue): helyi iparűzési adó up to 2 % of adjusted turnover (Budapest 2 %); KATA/KIVA optional regimes


## 5200 Gépjárműadó (pass 11, kernel 2.4.0, grade A)
Source: 1991. évi LXXXII. törvény a gépjárműadóról, net.jogtar.hu via the Internet Archive 2025-06-17 (`hu/law/gjt1991_wb2025.txt`); NAV, "Belföldi gépjárműadó 2025. évre valorizált adómértéke" (`hu/law/nav_gjt_valorizalt_2025.txt`).
* 6. § (1): the base of a passenger vehicle is its registered power in kW (horsepower / 1,36 where only hp is registered)
* 7. § (1): per kW, by calendar years after the year of manufacture: in that year and the 3 following 345 Ft, 4th-7th 300, 8th-11th 230, 12th-15th 185, from the 16th 140 (the 2024 amounts)
* 7/A. §: after 2024 each rate is the previous year's rate indexed by the July CPI change and rounded; NAV publishes the rates by 31 October: for 2025, 360 / 310 / 240 / 195 / 145 Ft/kW
* 5. § g): the környezetkímélő gépkocsi is exempt (electric and hydrogen cars read as such)
-/

namespace HuGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

def p11huRow (lo hi r : Int) (st : String) : VehicleTax :=
  { name := "Gépjárműadó", kinds := ["car"], fuels := [.petrol, .diesel, .hybrid, .pluginHybrid, .lpg, .cng, .other],   «when» := [(.age, lo, hi)], parts := [(.engineKw, QtyTable.perUnit r 1)], statute := st }
def p11huVeh : List VehicleTax :=
  [{ name := "Gépjárműadó", kinds := ["car"], fuels := [.electric, .hydrogen],    statute := "Gjt. 5. § g): a környezetkímélő gépkocsi (KöHÉM 2. § (6): purely electric and other zero-emission cars) is exempt" },  p11huRow (-1) 3 360 "Gjt. 6. § (1), 7. § (1), 7/A. §: year of manufacture and the 3 following calendar years, 360 Ft/kW (2025, NAV)",  p11huRow 3 7 310 "Gjt. 6. § (1), 7. § (1), 7/A. §: 4th-7th calendar year after the year of manufacture, 310 Ft/kW (2025, NAV)",  p11huRow 7 11 240 "Gjt. 6. § (1), 7. § (1), 7/A. §: 8th-11th calendar year, 240 Ft/kW (2025, NAV)",  p11huRow 11 15 195 "Gjt. 6. § (1), 7. § (1), 7/A. §: 12th-15th calendar year, 195 Ft/kW (2025, NAV)",  p11huRow 15 VehicleTax.noBound 145 "Gjt. 6. § (1), 7. § (1), 7/A. §: 16th calendar year and later, 145 Ft/kW (2025, NAV)"]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Gépjárműadó (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p11huVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["HU 5200 Gépjárműadó pass 11: Gjt. via the Internet Archive 2025-06-17 (`hu/law/gjt1991_wb2025.txt`); 2025 rates as published by NAV under 7/A. § (`hu/law/nav_gjt_valorizalt_2025.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)"] else [])
  ++ (if !(vehicleTaxUnknown "Gépjárműadó" p11huVeh g).isEmpty then ["5200 Gépjárműadó: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Gépjárműadó" p11huVeh g).isEmpty then ["5200 Gépjárműadó: a vehicle no rule reaches: motorcycles, buses, lorries (7. § (2) per 100 kg), trailers (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 gépjárműadó: the year of first registration is read as the year of manufacture (7. § (1) counts from the year of manufacture)"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .pluginHybrid) then ["5200 gépjárműadó: a plug-in hybrid is taxed by kW; it is exempt only if classed környezetkímélő (KöHÉM 2. § (6)), which the input does not give"] else [])
  ++ (if g.entity == .company && !g.vehicles.isEmpty then ["5200 cégautóadó (Gjt. 17/A-17/G. §, company cars, gépjárműadó deductible under 17/F. §) not modelled (grade C)"] else [])

#guard p11amt p11huVeh { kind := "car", fuel := .petrol, engineKw := 110, firstRegYear := 2019 } == 34100
#guard p11amt p11huVeh { kind := "car", fuel := .diesel, engineKw := 85, firstRegYear := 2022 } == 30600
#guard p11amt p11huVeh { kind := "car", fuel := .petrol, engineKw := 100, firstRegYear := 2021 } == 31000
#guard p11amt p11huVeh { kind := "car", fuel := .petrol, engineKw := 100, firstRegYear := 2017 } == 24000
#guard p11amt p11huVeh { kind := "car", fuel := .petrol, engineKw := 100, firstRegYear := 2010 } == 19500
#guard p11amt p11huVeh { kind := "car", fuel := .petrol, engineKw := 100, firstRegYear := 2009 } == 14500
#guard p11amt p11huVeh { kind := "car", fuel := .electric, engineKw := 150, firstRegYear := 2024 } == 0

end HuGlobal.Other
