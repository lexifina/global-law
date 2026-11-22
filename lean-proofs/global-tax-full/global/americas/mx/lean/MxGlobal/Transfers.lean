import MxGlobal.Pit
import TaxKernel.Global2

/-!
# MX 2025: Transfers family — no dated statute text reached (grade C)

* Transfer, stamp and recurrent property taxes (Código Fiscal CDMX (ISAI, predial)): tried not read in this pass (texts not local); would unlock: the acts and the 2025 municipal rates.

**Pass 14 (kernel 2.6.0): CDMX tenencia on new vehicles.** Código Fiscal de la Ciudad de México, consolidation to the reform of 26 Dec 2023 (Wayback 2025-08-06); the 2025 decree (G.O.CDMX 27 Dec 2024) changes only the cuotas of arts. 161 BIS 7 (aircraft) and 161 BIS 16 (model years before 2002) in this chapter. New vehicles first acquired in 2025: art. 161 BIS 5 I, 3 % of the price without IVA for automobiles of up to 15 passengers; 161 BIS 5 II, 0.245 % for pick-ups; 161 BIS 9, 3 % for motorcycles; 161 BIS 10, 0 % for electric and hybrid vehicles; 161 BIS 4, times the factor of the month of acquisition (February 0.92 to December 0.08). Used vehicles stay grade C (the INPC factor of 161 BIS 1 and the 2025 cuotas are not held); the yearly subsidy resolution is not applied.
-/

namespace MxGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon MxGlobal

/-- Código Fiscal CDMX art. 161 BIS 4: factor by the month of acquisition of a new vehicle (January: 1). -/
def tenFactorBp : List Int := [10000, 9200, 8300, 7500, 6700, 5800, 5000, 4200, 3300, 2500, 1700, 800]

/-- A new-vehicle rule of 2025 for each month of acquisition (161 BIS 4), the month's factor as multiplier. -/
def tenMonths (t : VehicleTax) : List VehicleTax := (List.range 12).map fun (k : Nat) =>
  { t with
      name := s!"{t.name} (acquired in month {k + 1} of 2025)", occasion := .registration, proRata := false,
      «when» := [(.firstRegMonth, (k : Int), (k : Int) + 1)], multiplierBp := tenFactorBp.getD k 0,
      statute := t.statute ++ s!"; art. 161 BIS 4: month {k + 1}, factor {tenFactorBp.getD k 0} bp" }

def tenCombustion : List VehicleFuel := [.petrol, .diesel, .lpg, .cng, .other]

def tenCar : VehicleTax :=
  { name := "Impuesto sobre Tenencia o Uso de Vehículos (CDMX), new automobile", kinds := ["car", "stationWagon", "van"],
    fuels := tenCombustion, parts := [(.value, QtyTable.perUnit 300 10000)], level := .state,
    statute := "Código Fiscal CDMX art. 161 BIS 5 I: new automobiles for up to 15 passengers, 3 % of the valor total (161 BIS 2 VIII: price without IVA)" }
def tenMoto : VehicleTax :=
  { name := "Impuesto sobre Tenencia o Uso de Vehículos (CDMX), new motorcycle", kinds := ["motorcycle"],
    fuels := tenCombustion, parts := [(.value, QtyTable.perUnit 300 10000)], level := .state,
    statute := "Código Fiscal CDMX art. 161 BIS 9: new motorcycles, 3 % of the invoice value" }
def tenPickup : VehicleTax :=
  { name := "Impuesto sobre Tenencia o Uso de Vehículos (CDMX), new pick-up", kinds := ["pickup", "pickupSingleCab"],
    fuels := tenCombustion, parts := [(.value, QtyTable.perUnit 245 100000)], level := .state,
    statute := "Código Fiscal CDMX art. 161 BIS 5 II: goods vehicles under 15 t gross weight, pick-ups whatever their weight, 0.245 % of the valor total" }
def tenElectric : VehicleTax :=
  { name := "Impuesto sobre Tenencia o Uso de Vehículos (CDMX), electric or hybrid", kinds := ["car", "stationWagon", "van", "motorcycle", "pickup", "pickupSingleCab"],
    fuels := [.electric, .hybrid, .pluginHybrid, .hydrogen], occasion := .registration, level := .state,
    statute := "Código Fiscal CDMX art. 161 BIS 10: electric motorcycles and automobiles, also with a combustion or hydrogen engine: 0 %" }

def tenTs : List VehicleTax := tenElectric :: (tenMonths tenCar ++ tenMonths tenMoto ++ tenMonths tenPickup)

def tenF : Family := vehicleTaxFamily "tenencia (CDMX)" tenTs

def families : List Family := [tenF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if true then ["Transfer, stamp and recurrent property taxes: statute not reached in a dated form (grade C): not computed"] else []) ++ (if !g.vehicles.isEmpty then ["tenencia (CDMX): every vehicle taken as held by an owner domiciled in Mexico City (Código Fiscal CDMX art. 160; other States' taxes not modelled); value taken as the valor total without IVA; the yearly 100 % subsidy for vehicles up to $250,000 (an administrative resolution) not applied; trucks and buses (161 BIS 5 II by gross weight) not computed"] else []) ++ (if g.vehicles.any (fun v => v.firstRegYear != 2025) then ["tenencia (CDMX): vehicles first registered before 2025 (or without firstRegYear): used-vehicle tax (161 BIS 13, 15: value x depreciation x INPC factor of 161 BIS 1; 161 BIS 16 cuotas of the 27 Dec 2024 decree) not computed (grade C)"] else []) ++ vehicleTaxUnknown "tenencia (CDMX)" tenTs g

-- new petrol car bought in March 2025 for 400.000 (without IVA): 3 % = 12.000; x 0.83 = 9.960
#guard ((tenMonths tenCar).getD 2 tenCar).amount 2025 { value := 400000, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 3, newReg := true } == 9960
-- January, 600.000: 18.000 (factor 1)
#guard ((tenMonths tenCar).getD 0 tenCar).amount 2025 { value := 600000, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 1, newReg := true } == 18000
-- motorcycle December, 50.000: 1.500 x 0.08 = 120
#guard ((tenMonths tenMoto).getD 11 tenMoto).amount 2025 { kind := "motorcycle", value := 50000, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 12, newReg := true } == 120
-- pick-up June, 500.000: 0.245 % = 1.225; x 0.58 = 710.5
#guard ((tenMonths tenPickup).getD 5 tenPickup).amount 2025 { kind := "pickup", value := 500000, fuel := .diesel, firstRegYear := 2025, firstRegMonth := 6, newReg := true } == 710
#guard tenElectric.amount 2025 { value := 900000, fuel := .electric, firstRegYear := 2025, firstRegMonth := 4, newReg := true } == 0
#guard (tenTs.filter (·.computes 2025 { value := 400000, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 3, newReg := true })).length == 1
#guard (tenTs.filter (·.computes 2025 { value := 400000, fuel := .petrol, firstRegYear := 2025, newReg := true })).isEmpty
#guard (tenTs.filter (·.computes 2025 { value := 400000, fuel := .electric, firstRegYear := 2025, newReg := true })).length == 1

end MxGlobal.Transfers
