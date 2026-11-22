import TaxKernel.Global2
import R5Common

/-!
# Türkiye 2025: motorlu taşıtlar vergisi (MTV, 5200) on cars

Law 197 (Motorlu Taşıtlar Vergisi Kanunu) art. 5 (I) tariff for cars registered from 1/1/2018 (by engine size, vehicle
value and age) and provisional art. 8 (I/A) tariff for cars registered up to 31/12/2017 (by engine size and age), amounts
for 2025 as revalued by 43,93 % (VUK General Communiqué 574) and announced in **MTV General Communiqué Serial No. 57**
(Resmî Gazete 32768, 2nd repeated, 30/12/2024; in force 1/1/2025), read directly on resmigazete.gov.tr
(`law/rg_20241230M2-6.txt`). Age bands 1-3, 4-6, 7-11, 12-15, 16+ years; value bands "not exceeding" (upper bound
included). Payer: the registered owner (art. 3).
Model: cars (`vehicleKind` "car") with `engineCcm`, `firstRegYear`, and for 2018+ cars `value`; the law's age counts the
model year as year 1: model year taken = `firstRegYear` (kernel age 0-2 = 1-3 yaş); the (I) tariff's "taşıt değeri" (value
at first registration, revalued) taken as the asset `value`; months held pro rata (the law charges by half-year
instalments: not modelled). Electric cars: see the section "Electric cars (pass 3n)";
(II) tariff vehicles: no rule (listed). Pass 3m: motorcycles added (I) tariff part 2 (100-250 / 251-650 / 651-1200 / 1201+ cm³ by age; none below 100 cm³). **Grade A** (communiqué text read; it prints the statutory tariffs).
-/

namespace TrGlobal
open TaxKernel TaxKernel.Global

def mtvI1 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, -1, 1300), (.value, -1, 259900)],
    parts := [(.age, QtyTable.ofCeilings [(2, 4834), (5, 3372), (10, 1882), (14, 1420)] 499)],
    statute := "Law 197 art. 5 (I) tariff row 1; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI2 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, -1, 1300), (.value, 259900, 455300)],
    parts := [(.age, QtyTable.ofCeilings [(2, 5313), (5, 3707), (10, 2068), (14, 1565)] 551)],
    statute := "Law 197 art. 5 (I) tariff row 2; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI3 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, -1, 1300), (.value, 455300, 1000000000000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 5803), (5, 4042), (10, 2264), (14, 1709)] 594)],
    statute := "Law 197 art. 5 (I) tariff row 3; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI4 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 1300, 1600), (.value, -1, 259900)],
    parts := [(.age, QtyTable.ofCeilings [(2, 8421), (5, 6314), (10, 3661), (14, 2587)] 993)],
    statute := "Law 197 art. 5 (I) tariff row 4; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI5 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 1300, 1600), (.value, 259900, 455300)],
    parts := [(.age, QtyTable.ofCeilings [(2, 9267), (5, 6948), (10, 4031), (14, 2838)] 1085)],
    statute := "Law 197 art. 5 (I) tariff row 5; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI6 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 1300, 1600), (.value, 455300, 1000000000000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 10112), (5, 7577), (10, 4389), (14, 3098)] 1184)],
    statute := "Law 197 art. 5 (I) tariff row 6; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI7 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 1600, 1800), (.value, -1, 651700)],
    parts := [(.age, QtyTable.ofCeilings [(2, 16370), (5, 12801), (10, 7523), (14, 4589)] 1777)],
    statute := "Law 197 art. 5 (I) tariff row 7; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI8 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 1600, 1800), (.value, 651700, 1000000000000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 17866), (5, 13956), (10, 8218), (14, 5014)] 1940)],
    statute := "Law 197 art. 5 (I) tariff row 8; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI9 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 1800, 2000), (.value, -1, 651700)],
    parts := [(.age, QtyTable.ofCeilings [(2, 25792), (5, 19862), (10, 11674), (14, 6948)] 2731)],
    statute := "Law 197 art. 5 (I) tariff row 9; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI10 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 1800, 2000), (.value, 651700, 1000000000000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 28142), (5, 21677), (10, 12734), (14, 7577)] 2982)],
    statute := "Law 197 art. 5 (I) tariff row 10; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI11 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 2000, 2500), (.value, -1, 813900)],
    parts := [(.age, QtyTable.ofCeilings [(2, 38695), (5, 28090), (10, 17549), (14, 10480)] 4145)],
    statute := "Law 197 art. 5 (I) tariff row 11; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI12 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 2000, 2500), (.value, 813900, 1000000000000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 42217), (5, 30642), (10, 19141), (14, 11439)] 4522)],
    statute := "Law 197 art. 5 (I) tariff row 12; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI13 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 2500, 3000), (.value, -1, 1628900)],
    parts := [(.age, QtyTable.ofCeilings [(2, 53952), (5, 46942), (10, 29322), (14, 15770)] 5780)],
    statute := "Law 197 art. 5 (I) tariff row 13; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI14 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 2500, 3000), (.value, 1628900, 1000000000000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 58864), (5, 51203), (10, 31991), (14, 17206)] 6308)],
    statute := "Law 197 art. 5 (I) tariff row 14; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI15 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 3000, 3500), (.value, -1, 1628900)],
    parts := [(.age, QtyTable.ofCeilings [(2, 82173), (5, 73942), (10, 44537), (14, 22231)] 8142)],
    statute := "Law 197 art. 5 (I) tariff row 15; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI16 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 3000, 3500), (.value, 1628900, 1000000000000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 89652), (5, 80656), (10, 48585), (14, 24245)] 8893)],
    statute := "Law 197 art. 5 (I) tariff row 16; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI17 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 3500, 4000), (.value, -1, 2607700)],
    parts := [(.age, QtyTable.ofCeilings [(2, 129201), (5, 111570), (10, 65702), (14, 29322)] 11674)],
    statute := "Law 197 art. 5 (I) tariff row 17; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI18 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 3500, 4000), (.value, 2607700, 1000000000000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 140960), (5, 121707), (10, 71687), (14, 31991)] 12734)],
    statute := "Law 197 art. 5 (I) tariff row 18; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI19 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 4000, 1000000000000), (.value, -1, 3096500)],
    parts := [(.age, QtyTable.ofCeilings [(2, 211479), (5, 158577), (10, 93917), (14, 42208)] 16370)],
    statute := "Law 197 art. 5 (I) tariff row 19; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvI20 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regFrom := 2018,
    when := [(.engineCcm, 4000, 1000000000000), (.value, 3096500, 1000000000000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 230698), (5, 172998), (10, 102458), (14, 46044)] 17866)],
    statute := "Law 197 art. 5 (I) tariff row 20; MTV General Communiqué No. 57 (RG 32768 M2, 30/12/2024) art. 4(1)" }

def mtvIA1 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regTo := 2017,
    when := [(.engineCcm, -1, 1300)],
    parts := [(.age, QtyTable.ofCeilings [(2, 4834), (5, 3372), (10, 1882), (14, 1420)] 499)],
    statute := "Law 197 provisional art. 8 (I/A) tariff (up to 1300 cm³); MTV General Communiqué No. 57 art. 4(4)" }

def mtvIA2 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regTo := 2017,
    when := [(.engineCcm, 1300, 1600)],
    parts := [(.age, QtyTable.ofCeilings [(2, 8421), (5, 6314), (10, 3661), (14, 2587)] 993)],
    statute := "Law 197 provisional art. 8 (I/A) tariff (1301-1600 cm³); MTV General Communiqué No. 57 art. 4(4)" }

def mtvIA3 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regTo := 2017,
    when := [(.engineCcm, 1600, 1800)],
    parts := [(.age, QtyTable.ofCeilings [(2, 14885), (5, 11626), (10, 6848), (14, 4168)] 1612)],
    statute := "Law 197 provisional art. 8 (I/A) tariff (1601-1800 cm³); MTV General Communiqué No. 57 art. 4(4)" }

def mtvIA4 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regTo := 2017,
    when := [(.engineCcm, 1800, 2000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 23454), (5, 18057), (10, 10613), (14, 6314)] 2487)],
    statute := "Law 197 provisional art. 8 (I/A) tariff (1801-2000 cm³); MTV General Communiqué No. 57 art. 4(4)" }

def mtvIA5 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regTo := 2017,
    when := [(.engineCcm, 2000, 2500)],
    parts := [(.age, QtyTable.ofCeilings [(2, 35175), (5, 25534), (10, 15954), (14, 9528)] 3766)],
    statute := "Law 197 provisional art. 8 (I/A) tariff (2001-2500 cm³); MTV General Communiqué No. 57 art. 4(4)" }

def mtvIA6 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regTo := 2017,
    when := [(.engineCcm, 2500, 3000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 49052), (5, 42669), (10, 26654), (14, 14329)] 5259)],
    statute := "Law 197 provisional art. 8 (I/A) tariff (2501-3000 cm³); MTV General Communiqué No. 57 art. 4(4)" }

def mtvIA7 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regTo := 2017,
    when := [(.engineCcm, 3000, 3500)],
    parts := [(.age, QtyTable.ofCeilings [(2, 74703), (5, 67218), (10, 40486), (14, 20203)] 7409)],
    statute := "Law 197 provisional art. 8 (I/A) tariff (3001-3500 cm³); MTV General Communiqué No. 57 art. 4(4)" }

def mtvIA8 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regTo := 2017,
    when := [(.engineCcm, 3500, 4000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 117462), (5, 101427), (10, 59730), (14, 26654)] 10613)],
    statute := "Law 197 provisional art. 8 (I/A) tariff (3501-4000 cm³); MTV General Communiqué No. 57 art. 4(4)" }

def mtvIA9 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["car"], regTo := 2017,
    when := [(.engineCcm, 4000, 1000000000000)],
    parts := [(.age, QtyTable.ofCeilings [(2, 192250), (5, 144166), (10, 85377), (14, 38363)] 14885)],
    statute := "Law 197 provisional art. 8 (I/A) tariff (from 4001 cm³); MTV General Communiqué No. 57 art. 4(4)" }

def mtvM1 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["motorcycle"],
    when := [(.engineCcm, 99, 250)],
    parts := [(.age, QtyTable.ofCeilings [(2, 899), (5, 672), (10, 496), (14, 305)] 115)],
    statute := "Law 197 art. 5 (I) tariff, 2- Motosikletler (100-250 cm³); MTV General Communiqué No. 57 art. 4(1)" }

def mtvM2 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["motorcycle"],
    when := [(.engineCcm, 250, 650)],
    parts := [(.age, QtyTable.ofCeilings [(2, 1862), (5, 1409), (10, 899), (14, 496)] 305)],
    statute := "Law 197 art. 5 (I) tariff, 2- Motosikletler (251-650 cm³); MTV General Communiqué No. 57 art. 4(1)" }

def mtvM3 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["motorcycle"],
    when := [(.engineCcm, 650, 1200)],
    parts := [(.age, QtyTable.ofCeilings [(2, 4808), (5, 2857), (10, 1409), (14, 899)] 496)],
    statute := "Law 197 art. 5 (I) tariff, 2- Motosikletler (651-1200 cm³); MTV General Communiqué No. 57 art. 4(1)" }

def mtvM4 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["motorcycle"],
    when := [(.engineCcm, 1200, VehicleTax.noBound)],
    parts := [(.age, QtyTable.ofCeilings [(2, 11666), (5, 7707), (10, 4808), (14, 3817)] 1862)],
    statute := "Law 197 art. 5 (I) tariff, 2- Motosikletler (from 1201 cm³); MTV General Communiqué No. 57 art. 4(1)" }

/-- (I) tariff part 2 starts at 100 cm³: a smaller motorcycle has no row (cited zero). -/
def mtvM0 : VehicleTax :=
  { name := "motorlu taşıtlar vergisi", kinds := ["motorcycle"], when := [(.engineCcm, -1, 99)],
    statute := "Law 197 art. 5 (I) tariff, 2- Motosikletler: rows from 100 cm³ only (below: no tax); MTV General Communiqué No. 57 art. 4(1)" }

/-! ## Electric cars (pass 3n)

Law 197 art. 5 fourth paragraph (added by Law 7103 art. 18, 21/3/2018; GİB article text `law/tr_gib_madde_197.json`,
article 5 as published by GİB, read 2026-11-21): cars of the (I) tariff part 1 with **only an electric motor** are taxed at
**25 %** of the amount of the row for their value and age among rows 1-3 (motor power up to 70 kW), 4-6 (70-85), 7-8
(85-105), 9-10 (105-120), 11-12 (120-150), 13-14 (150-180), 15-16 (180-210), 17-18 (210-240), 19-20 (above 240 kW).
Model: `fuel` "electric", `engineKw`, `value`, first registration from 2018 (the (I) tariff); the row's value band and
age table as for other cars, × 25 % (kernel `multiplierBp`, rounded down to the lira). Hybrids are not "only electric":
they stay on the engine-size rows. Electric motorcycles (art. 5 fifth paragraph): section below (pass 3o). -/

def evOf (r : VehicleTax) (lo hi : Int) (row : Nat) : VehicleTax :=
  let w : List (VehicleAttr × Int × Int) := (VehicleAttr.engineKw, lo, hi) :: r.when.drop 1
  let st := s!"Law 197 art. 5 fourth paragraph (Law 7103): only-electric car, motor power band of (I) tariff row {row}: 25 % of that row; MTV General Communiqué No. 57 art. 4(1)"
  { r with fuels := [VehicleFuel.electric], multiplierBp := 2500, statute := st, when := w }

def mtvEV : List VehicleTax :=
  [evOf mtvI1 (-1) 70 1,
   evOf mtvI2 (-1) 70 2,
   evOf mtvI3 (-1) 70 3,
   evOf mtvI4 70 85 4,
   evOf mtvI5 70 85 5,
   evOf mtvI6 70 85 6,
   evOf mtvI7 85 105 7,
   evOf mtvI8 85 105 8,
   evOf mtvI9 105 120 9,
   evOf mtvI10 105 120 10,
   evOf mtvI11 120 150 11,
   evOf mtvI12 120 150 12,
   evOf mtvI13 150 180 13,
   evOf mtvI14 150 180 14,
   evOf mtvI15 180 210 15,
   evOf mtvI16 180 210 16,
   evOf mtvI17 210 240 17,
   evOf mtvI18 210 240 18,
   evOf mtvI19 240 VehicleTax.noBound 19,
   evOf mtvI20 240 VehicleTax.noBound 20]

#guard mtvEV.length == 20

/-! ## Electric motorcycles (pass 3o)

Law 197 art. 5 fifth paragraph (added by Law 7103 art. 18, 21/3/2018; same GİB article text `law/tr_gib_madde_197.json`):
motorcycles of the (I) tariff part 2 with **only an electric motor** are taxed at **25 %** of the amount, by age, of the
part's first row (motor power above 6 kW up to 15 kW), second (15-40 kW), third (40-60 kW) or fourth (above 60 kW). A
motor of at most 6 kW is in no row (cited zero, as `mtvM0` below 100 cm³). Model: `vehicleKind` "motorcycle", `fuel`
"electric", `engineKw`; × 25 % (`multiplierBp`), rounded down to the lira. -/

def evMoto (r : VehicleTax) (lo hi : Int) (row : Nat) : VehicleTax :=
  let st := s!"Law 197 art. 5 fifth paragraph (Law 7103): only-electric motorcycle, motor power band of (I) tariff part 2 row {row}: 25 % of that row; MTV General Communiqué No. 57 art. 4(1)"
  { r with fuels := [VehicleFuel.electric], multiplierBp := 2500, statute := st, «when» := [(VehicleAttr.engineKw, lo, hi)] }

def mtvMEV : List VehicleTax :=
  [{ name := "motorlu taşıtlar vergisi", kinds := ["motorcycle"], fuels := [VehicleFuel.electric], «when» := [(VehicleAttr.engineKw, -1, 6)],
     statute := "Law 197 art. 5 fifth paragraph: only-electric motorcycles from 6 kW only (up to 6 kW: no row, no tax)" },
   evMoto mtvM1 6 15 1,
   evMoto mtvM2 15 40 2,
   evMoto mtvM3 40 60 3,
   evMoto mtvM4 60 VehicleTax.noBound 4]

#guard mtvMEV.length == 5

def mtv : List VehicleTax := mtvEV ++ mtvMEV ++ [mtvM0, mtvM1, mtvM2, mtvM3, mtvM4, mtvI1, mtvI2, mtvI3, mtvI4, mtvI5, mtvI6, mtvI7, mtvI8, mtvI9, mtvI10, mtvI11, mtvI12, mtvI13, mtvI14, mtvI15, mtvI16, mtvI17, mtvI18, mtvI19, mtvI20, mtvIA1, mtvIA2, mtvIA3, mtvIA4, mtvIA5, mtvIA6, mtvIA7, mtvIA8, mtvIA9]

def vehicles : Family := vehicleTaxFamily "motorlu taşıtlar vergisi" mtv

def vehiclesUnsupported (g : CanonGlobal) : List String :=
  vehicleTaxUnknown "motorlu taşıtlar vergisi" mtv g ++ vehicleTaxUnmatched "motorlu taşıtlar vergisi" mtv g
  ++ (if g.vehicles.isEmpty then [] else
      ["MTV: model year taken as the first-registration year; (I) tariff value taken as the asset value; motorcycles by the (I) tariff part 2 (age from the first-registration year); only-electric cars from 2018 at 25 % of the row matched by engineKw (art. 5 fourth paragraph); only-electric motorcycles at 25 % of the part 2 row matched by engineKw (art. 5 fifth paragraph); (II) tariff vehicles not computed"])

#guard (QtyTable.ofCeilings [(2, 4834), (5, 3372), (10, 1882), (14, 1420)] 499).amount 0 == 4834
#guard (QtyTable.ofCeilings [(2, 28142), (5, 21677), (10, 12734), (14, 7577)] 2982).amount 3 == 21677
#guard (QtyTable.ofCeilings [(2, 192250), (5, 144166), (10, 85377), (14, 38363)] 14885).amount 15 == 14885
#guard (QtyTable.ofCeilings [(2, 1862), (5, 1409), (10, 899), (14, 496)] 305).amount 4 == 1409

end TrGlobal
