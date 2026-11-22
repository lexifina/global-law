import TaxKernel.Global2
import R5Common

/-!
# Tunisia 2025: taxe de circulation (vignette) and the annual surtaxes on diesel and LPG cars (5200)

Source: DGELF compendium "Recueil des textes relatifs aux taxes …" (Ministère des Finances, December 2023, up to LF 2023;
`law/recueil2023.pdf`, text `law/tn_recueil2023.txt`), title I chapter I sections 2-6, with the 2024 and 2025 finance
laws read for later changes (JORT texts on disk: `law/Loi2023_13.txt` = LF 2024, `law/Loi2024_48.txt` = LF 2025):
* **Décret beylical du 31 mars 1955, art. 19** (amended by LF 2000 art. 58, LF 2016 art. 90, **LF 2022 art. 55**):
  I-1-a annual tax on cars by fiscal horsepower: up to 4 CV 65 D; 5-7 CV 130; 8-9 CV 180; 10-11 CV 230; 12-13 CV
  1 050; 14-15 CV 1 400; 16 CV and more (and sports cars) 2 100. Motorcycles: under 50 cm³ 35 D; 50 to 125 cm³ scooter
  type 65, other 120; above 125 cm³ 250. I-1-b: **doubled** (+100 %) for vehicles of legal persons other than the
  State, local authorities and administrative public bodies (not for individuals' leasing/ijara). **LF 2024 art. 50(2)**:
  "Ladite taxe est réduite à 50% pour les voitures et motocycles électriques". III: exemptions (goods vehicles above
  300 kg payload, taxis and louages, foreign-registered vehicles for 3 months, official vehicles; LF 2025 art. 16(3):
  8-9 seat vehicles carrying farm workers). The II reduction (vehicles put into circulation before 6/4/1985 and at
  most 15 years old) can no longer apply.
* **Décret-loi 60-22 du 13 septembre 1960** art. 1: annual tax on diesel ("moteurs à huile lourde") tourism cars:
  150 D below 9 CV, 225 D from 9 CV (on top of the vignette).
* **Loi 84-84 du 31/12/1984 art. 34**: additional annual tax on LPG cars: 325 D below 9 CV, 400 D from 9 CV.
LF 2024 and LF 2025 add exemptions only (no tariff change). Annual amounts, no pro rata (the stamp is valid for the
calendar year). The owner pays. Input: vehicle `vehicleKind` "car" with `fiscalHp` and `fuel`; "motorcycle" or
"scooter" with `engineCcm` (or `fuel` electric with `engineCcm`). **Grade A** (official compendium and finance laws
read).
-/

namespace TnGlobal
open TaxKernel TaxKernel.Global R5Common

def tcName : String := "Taxe de circulation (vignette)"

/-- the car tariff (art. 19 I-1-a as amended by LF 2022 art. 55) -/
def carTable : QtyTable := QtyTable.ofCeilings [(4, 65), (7, 130), (9, 180), (11, 230), (13, 1050), (15, 1400)] 2100

/-- `m`: 10000 for natural persons, 20000 for legal persons (I-1-b); electric at half (LF 2024 art. 50(2)); first match. -/
def vignette (m : Int) : List VehicleTax :=
  [{ name := tcName, kinds := ["car"], fuels := [.electric], parts := [(.fiscalHp, carTable)], multiplierBp := m / 2, proRata := false,
     statute := "Décret du 31/3/1955 art. 19 I-1-a (LF 2022 art. 55), I-1-b, LF 2024 art. 50(2) (electric: 50 %)" },
   { name := tcName, kinds := ["car"], parts := [(.fiscalHp, carTable)], multiplierBp := m, proRata := false,
     statute := "Décret du 31/3/1955 art. 19 I-1-a (LF 2022 art. 55: 65 / 130 / 180 / 230 / 1 050 / 1 400 / 2 100 D), I-1-b" },
   { name := tcName, kinds := ["motorcycle", "scooter"], fuels := [.electric], «when» := [(.engineCcm, -1, 49)], fixed := 35, multiplierBp := m / 2, proRata := false,
     statute := "Décret du 31/3/1955 art. 19 I-1-a (under 50 cm³: 35 D), LF 2024 art. 50(2) (electric: 50 %)" },
   { name := tcName, kinds := ["scooter"], fuels := [.electric], «when» := [(.engineCcm, 49, 125)], fixed := 65, multiplierBp := m / 2, proRata := false,
     statute := "Décret du 31/3/1955 art. 19 I-1-a (50-125 cm³ scooter: 65 D), LF 2024 art. 50(2)" },
   { name := tcName, kinds := ["motorcycle"], fuels := [.electric], «when» := [(.engineCcm, 49, 125)], fixed := 120, multiplierBp := m / 2, proRata := false,
     statute := "Décret du 31/3/1955 art. 19 I-1-a (50-125 cm³ other: 120 D), LF 2024 art. 50(2)" },
   { name := tcName, kinds := ["motorcycle", "scooter"], fuels := [.electric], «when» := [(.engineCcm, 125, VehicleTax.noBound)], fixed := 250, multiplierBp := m / 2, proRata := false,
     statute := "Décret du 31/3/1955 art. 19 I-1-a (above 125 cm³: 250 D, LF 2016 art. 90), LF 2024 art. 50(2)" },
   { name := tcName, kinds := ["motorcycle", "scooter"], «when» := [(.engineCcm, -1, 49)], fixed := 35, multiplierBp := m, proRata := false,
     statute := "Décret du 31/3/1955 art. 19 I-1-a (under 50 cm³: 35 D)" },
   { name := tcName, kinds := ["scooter"], «when» := [(.engineCcm, 49, 125)], fixed := 65, multiplierBp := m, proRata := false,
     statute := "Décret du 31/3/1955 art. 19 I-1-a (50-125 cm³ scooter type: 65 D)" },
   { name := tcName, kinds := ["motorcycle"], «when» := [(.engineCcm, 49, 125)], fixed := 120, multiplierBp := m, proRata := false,
     statute := "Décret du 31/3/1955 art. 19 I-1-a (50-125 cm³ other than scooters: 120 D)" },
   { name := tcName, kinds := ["motorcycle", "scooter"], «when» := [(.engineCcm, 125, VehicleTax.noBound)], fixed := 250, multiplierBp := m, proRata := false,
     statute := "Décret du 31/3/1955 art. 19 I-1-a (above 125 cm³: 250 D, LF 2016 art. 90)" }]

def surtaxes : List VehicleTax :=
  [{ name := "Taxe annuelle sur les véhicules de tourisme à moteurs à huile lourde", kinds := ["car"], fuels := [.diesel],
     parts := [(.fiscalHp, QtyTable.ofCeilings [(8, 150)] 225)], proRata := false,
     statute := "Décret-loi 60-22 du 13/9/1960 art. 1-I (below 9 CV 150 D, from 9 CV 225 D)" },
   { name := "Impôt additionnel annuel sur les véhicules utilisant le GPL", kinds := ["car"], fuels := [.lpg],
     parts := [(.fiscalHp, QtyTable.ofCeilings [(8, 325)] 400)], proRata := false,
     statute := "Loi 84-84 du 31/12/1984 art. 34 (below 9 CV 325 D, from 9 CV 400 D)" }]

def vehicles : Family :=
  { name := "5200 taxe de circulation", covers := [.useOfGoods],
    run := fun _ g _ =>
      vehicleTaxCharges (vignette (if g.entity == .company then 20000 else 10000)) g (firstOnly := true)
      ++ vehicleTaxCharges surtaxes g (firstOnly := true) }

def vehiclesUnsupported (g : CanonGlobal) : List String :=
  let ts := vignette 10000
  vehicleTaxUnknown tcName ts g ++ vehicleTaxUnmatched tcName ts g ++ vehicleTaxUnknown "surtaxes" surtaxes g
  ++ (if g.vehicles.isEmpty then [] else
      ["taxe de circulation: exemptions (goods vehicles above 300 kg payload, taxis, louages, official and associations' vehicles) not distinguished; a 50-125 cm³ two-wheeler is taken as 'other than scooter' unless vehicleKind is \"scooter\""])

#guard carTable.amount 4 == 65
#guard carTable.amount 6 == 130
#guard carTable.amount 9 == 180
#guard carTable.amount 12 == 1050
#guard carTable.amount 16 == 2100
#guard (QtyTable.ofCeilings [(8, 150)] 225).amount 9 == 225
#guard ((vignette 20000).getD 1 default).amount 2025 { fiscalHp := 10 } == 460
#guard ((vignette 10000).getD 0 default).amount 2025 { fiscalHp := 5, fuel := .electric } == 65

end TnGlobal
