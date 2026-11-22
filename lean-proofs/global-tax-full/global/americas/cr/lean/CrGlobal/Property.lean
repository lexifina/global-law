import CrGlobal.Pit
import TaxKernel.Global2

/-!
# CR 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (none read): tried not read in this pass; would unlock: the act's 2025 text.

**Pass 15 (2026-11-21), impuesto a la propiedad de vehículos (5200, A):** Ley 7088 art. 9 (as reformed by Ley 10390 of 2 Oct 2023), SINALEVI version 36 of 16 Sep 2024 (`cr/law/ley7088_sinalevi_v144138.json`; tables are images, `cr/law/img36/`, read by OCR and checked by eye). Art. 9 d): devengo at inscription and then on 30 September of the year before the período (1 Jan-31 Dec), so the período 2025 uses the tramos in force on 30 Sep 2024: Decreto 44658 of 16 Sep 2024 (version 37's Decreto 44867 of 8 Jan 2025 sets the slightly lower tramos of the período 2026). Art. 9 f): value depreciated by the yearly table (15 years; motorcycles 10), floor at the last year; I = [M + sum of (VM - L) x T over the tramos] - D, M = 5 % of a salario base (₡23.100; motorcycles 0,65 %, ₡3.000), D = the weight-and-emission deduction on the tax for automóviles up to nine years old (3,84 % ... 1,00 %), +0,1 % for electric automóviles. Taxis, buses, heavy goods: 2 % of a salario base (₡9.200).


**4300 (gap pass 2, 2026-11-22)**: not levied (grade B): Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Costa Rica (DSD_REV_LAC@DF_REVCRI v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/CRI.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published.
-/

namespace CrGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon CrGlobal

/-- Ley 7088 art. 9 f): accumulated depreciation by year (bp), vehicles, boats, aircraft (15-year life; image002). -/
def crDepCar : List Int := [0, 1030, 2030, 2980, 3870, 4650, 5330, 5930, 6450, 6900, 7300, 7650, 7960, 8240, 8490, 8710]
/-- motorcycles (10-year life; image004, image006). -/
def crDepMoto : List Int := [0, 1500, 2775, 3859, 4780, 5563, 6229, 6794, 7275, 7684, 8031]
/-- Tramos above the minimum (Decreto 44658 of 16 Sep 2024 arts. 1-2; image008, image010): (lower bound, rate bp). -/
def crCarTr : List (Int × Int) :=
  [(220000, 60), (3020000, 180), (4020000, 210), (5030000, 250), (6030000, 280), (10050000, 315), (13070000, 350)]
def crMotoTr : List (Int × Int) := [(1760000, 25), (2210000, 50), (4020000, 75), (7040000, 100), (10050000, 125)]
/-- Deduction for weight and emissions, automóviles, by age 0-9 (bp; image012, image014); none after nine years. -/
def crDed : List Int := [384, 384, 372, 360, 248, 236, 224, 212, 200, 100]
def crFuels : List VehicleFuel := [.petrol, .diesel, .hybrid, .pluginHybrid, .lpg, .cng, .other, .unknown]
def crSt : String := "Ley 7088 art. 9 f) (Ley 10390; SINALEVI version of 16 Sep 2024): tramos of Decreto 44658, devengo 30 Sep 2024 for the período 2025"

/-- The tramos on the depreciated value VM = V x r / 10000, written on V: thresholds L x 10000 / r (rounded down: within one colón of the statute), marginal
rate T x r / 10^8 per colón of V, so that the sum is T x (VM - L) per tramo. -/
def crTable (tr : List (Int × Int)) (r : Int) : QtyTable :=
  { steps := tr.map (fun p => ((p.1 * 10000) / r, p.2 * r)), den := 100000000 }

def crAgeWhen (a lastAge : Nat) : List (VehicleAttr × Int × Int) :=
  if a < lastAge then [(.age, (a : Int) - 1, (a : Int))] else [(.age, (a : Int) - 1, VehicleTax.noBound)]

/-- Vehicles first registered by 2024 (período 2025), by age; minimum M = 5 % of a salario base (₡23.100). -/
def crCar (a : Nat) (kinds : List String) (ded : Bool) : VehicleTax :=
  let r := 10000 - crDepCar.getD a 8710
  let d := if ded then crDed.getD a 0 else 0
  { name := s!"Impuesto a la propiedad de vehículos (período 2025, {kinds.headD "car"}, age {a})", kinds := kinds,
    fuels := crFuels, regTo := 2024, «when» := crAgeWhen a 15, fixed := 23100, parts := [(.value, crTable crCarTr r)],
    multiplierBp := 10000 - d,
    statute := crSt ++ s!": depreciation {10000 - r} bp, deduction for weight and emissions {d} bp" }

/-- Motorcycles; minimum 0,65 % of a salario base (₡3.000). -/
def crMoto (a : Nat) : VehicleTax :=
  let r := 10000 - crDepMoto.getD a 8031
  { name := s!"Impuesto a la propiedad de vehículos (período 2025, motorcycle, age {a})", kinds := ["motorcycle"],
    fuels := crFuels, regTo := 2024, «when» := crAgeWhen a 10, fixed := 3000, parts := [(.value, crTable crMotoTr r)],
    statute := crSt ++ s!" (motorcycles): depreciation {10000 - r} bp" }

/-- Taxis, buses and heavy goods vehicles: 2 % of a salario base (₡9.200, Decreto 44658 art. 3); buses only here. -/
def crBus : VehicleTax :=
  { name := "Impuesto a la propiedad de vehículos (período 2025, bus)", kinds := ["bus"], regTo := 2024, fixed := 9200,
    statute := crSt ++ "; taxis, buses, heavy goods: 2 % of a salario base, ₡9.200" }

def crTs : List VehicleTax :=
  (List.range 16).flatMap (fun a => [crCar a ["car"] (decide (a ≤ 9)), crCar a ["stationWagon", "suv", "van", "pickup", "pickupSingleCab"] false])
  ++ (List.range 11).map crMoto ++ [crBus]

def vehF : Family := vehicleTaxFamily "impuesto a la propiedad de vehículos" crTs

def families : List Family := [vehF]

def absent : List Absent :=
  [{ oecd := .estate, why := "Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Costa Rica (DSD_REV_LAC@DF_REVCRI v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/CRI.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if !g.vehicles.isEmpty then ["impuesto a la propiedad de vehículos (CR): the vehicle's value is read as its value before depreciation (customs or purchase value, art. 9 b)); age = 2025 - first registration year, standing for the age by model year; vehicles first registered in 2025 (devengo at inscription) not computed; electric vehicles not computed (Ley 9518 exemption scale not read; grade C); the weight-and-emission deduction given to kind car only (automóvil, Ley 9078 art. 2 (8) not read); taxis and heavy goods vehicles (₡9.200) not identified: trucks not computed; used first imports' one-year depreciation pause not applied"] else []) ++ vehicleTaxUnknown "impuesto a la propiedad de vehículos" crTs g ++ vehicleTaxUnmatched "impuesto a la propiedad de vehículos" crTs g

-- car first registered 2020 (age 5, depreciation 46,5 %), value 10.000.000: VM 5.350.000; 23.100 + 16.800 + 18.000 + 21.210 + 8.000 = 87.110; less 2,36 % = 85.054
#guard (crCar 5 ["car"] true).amount 2025 { value := 10000000, firstRegYear := 2020 } == 85054
-- same value, kind pickup (no deduction): 87.110
#guard (crCar 5 ["pickup"] false).amount 2025 { value := 10000000, firstRegYear := 2020 } == 87110
-- motorcycle first registered 2023 (age 2, 27,75 %), 3.000.000: VM 2.167.500; 3.000 + 0,25 % x 407.500 = 1.018 -> 4.018
#guard (crMoto 2).amount 2025 { value := 3000000, firstRegYear := 2023 } == 4018

end CrGlobal.Property
