import PlGlobal.Pit
import TaxKernel.Global2

/-!
# PL 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Podatek od niektórych instytucji finansowych (bank tax 0.0366 %/month); podatek od sprzedaży detalicznej): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor here: bank tax and retail sales tax are sector taxes


## 5200 Akcyza od samochodów osobowych (pass 11, kernel 2.4.0, grade A)
Source: Ustawa z dnia 6 grudnia 2008 r. o podatku akcyzowym, tekst jednolity Dz. U. 2025 poz. 126, api.sejm.gov.pl (`pl/law/akcyza_tj2025.txt`).
* art. 100 ust. 1: the excise on passenger cars falls on the import, the intra-Community acquisition and the first sale in Poland of a car not yet registered in Poland
* art. 104 ust. 1: the base is the price of the sale net of VAT and excise, the amount paid on an intra-Community acquisition, or the customs value plus duty on import
* art. 105: 18,6 % for an engine above 2000 cm3; 9,3 % for hybrids (charged or not from an external source) above 2000 and not above 3500 cm3; 1,55 % for hybrids not charged externally of 2000 cm3 or less; 3,1 % for other cars
* art. 109a ust. 1: electric and hydrogen cars are exempt; art. 163a ust. 1: plug-in hybrids of 2000 cm3 or less are exempt to 31 December 2029
* OECD classification: an excise on a good (5121), booked in the vehicle family because the event is the car's first registration in Poland


## 5200 Podatek od środków transportowych (pass 11, kernel 2.4.0, grade A)
Source: Ustawa z dnia 12 stycznia 1991 r. o podatkach i opłatach lokalnych, tekst jednolity Dz. U. 2025 poz. 707, api.sejm.gov.pl (`pl/law/upol_tj2025_707.txt`).
* art. 8: the tax falls on lorries above 3,5 t, tractor units, trailers and semi-trailers from 7 t with the vehicle, and buses: passenger cars, motorcycles and vans are outside it (cited 0)
-/

namespace PlGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

def p11plAkc (fs : List VehicleFuel) (lo hi bp : Int) (st : String) : VehicleTax :=
  { name := "Akcyza od samochodów osobowych", oecd := .excise, kinds := ["car"], fuels := fs, occasion := .registration,   «when» := [(.engineCcm, lo, hi)], parts := [(.value, QtyTable.perUnit bp 10000)], statute := st }
def p11plIce : List VehicleFuel := [.petrol, .diesel, .lpg, .cng, .other]
def p11plAkcyza : List VehicleTax :=
  [{ name := "Akcyza od samochodów osobowych", oecd := .excise, kinds := ["car"], fuels := [.electric, .hydrogen], occasion := .registration,    statute := "ustawa o podatku akcyzowym art. 109a ust. 1: a passenger car that is an electric vehicle or a hydrogen-driven vehicle is exempt" },  { name := "Akcyza od samochodów osobowych", oecd := .excise, kinds := ["car"], fuels := [.pluginHybrid], occasion := .registration,    «when» := [(.engineCcm, -1, 2000)],    statute := "ustawa o podatku akcyzowym art. 163a ust. 1: to 31 December 2029 a plug-in hybrid (art. 2 pkt 13 ustawy o elektromobilności) with an engine of 2000 cm3 or less is exempt" },  p11plAkc [.hybrid, .pluginHybrid] 2000 3500 930 "ustawa o podatku akcyzowym art. 104, art. 105 pkt 1a: hybrid with an engine above 2000 and not above 3500 cm3, 9,3 % of the base",  p11plAkc [.hybrid] (-1) 2000 155 "ustawa o podatku akcyzowym art. 104, art. 105 pkt 1b: hybrid not charged from an external source, engine of 2000 cm3 or less, 1,55 % of the base",  p11plAkc (p11plIce ++ [.hybrid, .pluginHybrid]) 2000 VehicleTax.noBound 1860 "ustawa o podatku akcyzowym art. 104, art. 105 pkt 1: engine above 2000 cm3, 18,6 % of the base",  p11plAkc p11plIce (-1) 2000 310 "ustawa o podatku akcyzowym art. 104, art. 105 pkt 2: other passenger cars, 3,1 % of the base"]
def p11plSt : List VehicleTax :=
  [{ name := "Podatek od środków transportowych", kinds := ["car", "motorcycle", "van"], level := .local,    statute := "ustawa o podatkach i opłatach lokalnych art. 8: only lorries above 3,5 t, tractor units, trailers from 7 t and buses are taxable: cars, motorcycles and vans are not" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5121 Akcyza od samochodów osobowych (pass 11)", covers := [.excise],
     run := fun args g prev =>
       vehicleTaxCharges p11plAkcyza g (firstOnly := true) },
   { name := "5200 Podatek od środków transportowych (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p11plSt g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["PL 5200 Akcyza od samochodów osobowych pass 11: tekst jednolity Dz. U. 2025 poz. 126 (`pl/law/akcyza_tj2025.txt`) (grade A)", "PL 5200 Podatek od środków transportowych pass 11: tekst jednolity Dz. U. 2025 poz. 707 (`pl/law/upol_tj2025_707.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)"] else [])
  ++ (if !(vehicleTaxUnknown "Akcyza od samochodów osobowych" p11plAkcyza g).isEmpty then ["5200 Akcyza od samochodów osobowych: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg && !(p11plAkcyza.any (·.selects g.year v))) then ["5200 Akcyza od samochodów osobowych: a vehicle no rule reaches: vehicles other than passenger cars, cars without engine size (an electric car needs none) (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg) then ["5121 akcyza: the vehicle's value is taken as the art. 104 base (price net of VAT and excise, or the amount paid abroad); a car first registered in Poland in the year is taken as not yet registered there (art. 100 ust. 1)"] else [])
  ++ (if !(vehicleTaxUnknown "Podatek od środków transportowych" p11plSt g).isEmpty then ["5200 Podatek od środków transportowych: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Podatek od środków transportowych" p11plSt g).isEmpty then ["5200 Podatek od środków transportowych: a vehicle no rule reaches: lorries, tractor units, trailers and buses (taxable at the municipality's rates, not modelled) (grade C)"] else [])

#guard p11amt p11plAkcyza { kind := "car", fuel := .petrol, engineCcm := 1498, value := 100000, firstRegYear := 2025, newReg := true } == 3100
#guard p11amt p11plAkcyza { kind := "car", fuel := .diesel, engineCcm := 2500, value := 200000, firstRegYear := 2025, newReg := true } == 37200
#guard p11amt p11plAkcyza { kind := "car", fuel := .hybrid, engineCcm := 1800, value := 120000, firstRegYear := 2025, newReg := true } == 1860
#guard p11amt p11plAkcyza { kind := "car", fuel := .hybrid, engineCcm := 2500, value := 200000, firstRegYear := 2025, newReg := true } == 18600
#guard p11amt p11plAkcyza { kind := "car", fuel := .pluginHybrid, engineCcm := 1500, value := 150000, firstRegYear := 2025, newReg := true } == 0
#guard p11amt p11plAkcyza { kind := "car", fuel := .pluginHybrid, engineCcm := 2500, value := 200000, firstRegYear := 2025, newReg := true } == 18600
#guard p11amt p11plAkcyza { kind := "car", fuel := .hybrid, engineCcm := 3600, value := 200000, firstRegYear := 2025, newReg := true } == 37200
#guard p11amt p11plAkcyza { kind := "car", fuel := .electric, engineCcm := 0, value := 200000, firstRegYear := 2025, newReg := true } == 0
#guard p11amt p11plAkcyza { kind := "car", fuel := .petrol, engineCcm := 2000, value := 100000, firstRegYear := 2025, newReg := true } == 3100
#guard p11amt p11plAkcyza { kind := "car", fuel := .petrol, engineCcm := 2001, value := 100000, firstRegYear := 2025, newReg := true } == 18600
#guard p11amt p11plAkcyza { kind := "car", fuel := .petrol, engineCcm := 1498, value := 100000, firstRegYear := 2020 } == -1
#guard p11amt p11plSt { kind := "car", fuel := .petrol, engineCcm := 1498, firstRegYear := 2020 } == 0
#guard p11amt p11plSt { kind := "truck", fuel := .diesel, firstRegYear := 2020 } == -1

end PlGlobal.Other
