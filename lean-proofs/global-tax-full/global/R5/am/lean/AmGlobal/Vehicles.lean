import TaxKernel.Global2
import R5Common

/-!
# Armenia 2025: vehicle property tax (5200, local), pass 3l

Tax Code HO-165-N, official English translation (arlis.am acts/229632, to HO-487-N of 17/12/2025;
`law/am_tc_en_arlis229632.txt`), Section 12 (art. 240-249). **Grade A** (text read).
* art. 244(1)(1) passenger cars up to 10 seats, by engine horsepower (whole power at the rate of its band):
  1-120 hp AMD 200 per hp; 121-250 hp AMD 300 per hp plus AMD 1 000 per hp above 150; 251 hp and more AMD 500 per hp
  plus AMD 1 000 per hp above 150. (1)(2) cars and trucks with 10 seats or more: 1-200 hp AMD 100, 201 and more AMD 200.
  (2) motorcycles AMD 40 per hp.
* art. 244(4)-(5): 100 % in the year of release and the two following tax years; then reduced by 10 % of the tax for
  each further year, at most 50 %. (6) trucks: none from the 20th year (not modelled: lines carry no truck flag).
* art. 244(7): power in kilowatts × 1,36. (8) community surcharge up to 10 % not applied.
* art. 246: liability from the month after ownership: the vehicle's `months`.
Inputs: vehicle assets (kernel 2.4.0) `"vehicleKind"` car / motorcycle, `"engineKw"`, `"seats"`, `"firstRegYear"`
(taken as the release year), `"months"`. A vehicle without `engineKw` or `firstRegYear` is listed as grade C.
The annual environmental tax on vehicles (art. 168(1)(2), AMD 2,5-50 per hp by power and age) is not computed (noted).
-/

namespace AmGlobal
open TaxKernel TaxKernel.Global

/-- tax in AMD × 100 per (hp × 100): rates by art. 244(1)-(2); `hp100` = horsepower × 100 -/
def vptFull (kind : String) (seats : Int) (hp100 : Int) : Int :=
  if kind == "motorcycle" then 40 * hp100
  else if seats ≥ 10 then (if hp100 ≤ 20000 then 100 * hp100 else 200 * hp100)
  else if hp100 ≤ 12000 then 200 * hp100
  else if hp100 ≤ 25000 then 300 * hp100 + 1000 * pos (hp100 - 15000)
  else 500 * hp100 + 1000 * pos (hp100 - 15000)

/-- art. 244(4)-(5): percent of the tax due in tax year `y` for a vehicle released in year `r` -/
def vptAgePct (y r : Nat) : Int :=
  let n : Int := (y : Int) - (r : Int)
  if n ≤ 2 then 100 else 100 - min 50 (10 * (n - 2))

def vptAmount (y : Nat) (v : Vehicle) : Int :=
  divR .down (vptFull v.kind v.seats (v.engineKw * 136) * vptAgePct y v.firstRegYear * (v.months : Int)) (100 * 100 * 12)

def vptApplies (v : Vehicle) : Bool := v.kind == "car" || v.kind == "motorcycle"

def vptReady (v : Vehicle) : Bool := v.engineKw > 0 && v.firstRegYear > 0

/-! ## Annual environmental tax on vehicles (pass 3m)
Tax Code art. 168(1)(2) (as edited by HO-338-N of 21/06/2018 and HO-68-N of 25/06/2019; art. 168(2) repealed): for
motor vehicles other than cargo vehicles registered and operated in Armenia, an **annual rate per horsepower by power
band and production year**: bands ≤ 50, 51-80, 81-100, 101-150, 151-200, 201-250, 251-300, 301+ hp at AMD 2,5 / 5 /
7,5 / 10 / 12,5 / 15 / 17,5 / 25 per hp in the 1st-3rd year, rising to 1,2 / 1,4 / 1,6 / 1,8 / 2 times those in the
4th / 5th / 6th / 7th / 8th and later year (the table's columns); kW × 1,36; art. 175(2): annual tax = base × rate, to
the State Budget. Cargo vehicles (art. 168(1)(1), AMD 5 000 / 10 000 / 15 000 by mass) are not inputs here.
Production year = `firstRegYear`; 1st year = the production year. -/

/-- art. 168(1)(2): base rate (AMD × 10 per hp) of the power band (`hp100` = hp × 100). -/
def envBase10 (hp100 : Int) : Int :=
  if hp100 ≤ 5000 then 25 else if hp100 ≤ 8000 then 50 else if hp100 ≤ 10000 then 75
  else if hp100 ≤ 15000 then 100 else if hp100 ≤ 20000 then 125 else if hp100 ≤ 25000 then 150
  else if hp100 ≤ 30000 then 175 else 250

/-- the table's year columns as tenths of the 1st-year rate: years 1-3 ×1, 4th ×1,2 … 8th and later ×2 -/
def envYearFactor10 (y r : Nat) : Int :=
  let n : Int := (y : Int) - (r : Int) + 1
  if n ≤ 3 then 10 else if n ≥ 8 then 20 else 10 + 2 * (n - 3)

def envAmount (y : Nat) (v : Vehicle) : Int :=
  let hp100 := v.engineKw * 136
  divR .down (hp100 * envBase10 hp100 * envYearFactor10 y v.firstRegYear) (100 * 10 * 10)

def envCharges (g : CanonGlobal) : List Charge :=
  g.vehicles.zipIdx.filterMap fun (v, k) =>
    if vptApplies v && vptReady v then
      some (charge .useOfGoods "Environmental tax (mobile sources)" (v.engineKw * 136 / 100) id (fun _ => envAmount g.year v)
        (event := s!"vehicle {k + 1} (environmental tax)") (level := .central)
        (statute := "Tax Code art. 168(1)(2) (AMD per hp by power band and production year; kW x 1,36), art. 175(2)"))
    else none

def vehicles : Family :=
  { name := "5200 vehicle property tax", covers := [.useOfGoods],
    run := fun _ g _ =>
      (g.vehicles.zipIdx.filterMap fun (v, k) =>
        if vptApplies v && vptReady v then
          some (charge .useOfGoods "Vehicle property tax" (v.engineKw * 136 / 100) id (fun _ => vptAmount g.year v)
            (event := s!"vehicle {k + 1}") (level := .local)
            (statute := "Tax Code art. 243, 244(1)(1)-(2), (2), (4)-(5), (7) (AMD per hp; age reduction 10 %/year after 2 years, max 50 %)"))
        else none) ++ envCharges g }

def vehiclesUnsupported (g : CanonGlobal) : List String :=
  (g.vehicles.zipIdx.filterMap fun (v, k) =>
    if !vptApplies v then some s!"vehicle {k + 1} ({v.kind}): vehicle property tax for this kind (water vehicles, snowmobiles, quadricycles 150/hp) not computed"
    else if !vptReady v then some s!"vehicle {k + 1}: vehicle property tax needs engineKw and firstRegYear (grade C)"
    else none)
  ++ (if g.vehicles.isEmpty then [] else
      ["community surcharges (art. 244(8)) not computed; firstRegYear taken as the release (production) year; environmental tax booked for the whole year (cargo vehicles, art. 168(1)(1), not inputs)"])

-- 100 kW = 136 hp car (≤ 10 seats), released 2020, tax year 2025: 136 × 300 = 40 800 at 70 % = 28 560
#guard vptFull "car" 5 13600 == 4080000
#guard vptAgePct 2025 2020 == 70
#guard vptAgePct 2025 2010 == 50
#guard vptAgePct 2025 2023 == 100
-- 200 hp car: 200 × 300 + 50 × 1 000 = 110 000; 300 hp: 300 × 500 + 150 × 1 000 = 300 000
#guard vptFull "car" 5 20000 == 11000000
#guard vptFull "car" 5 30000 == 30000000
#guard vptFull "car" 5 12000 == 2400000
-- environmental tax: 136 hp, produced 2020, 2025 = 6th year: 10 x 1,6 = 16 per hp -> 2 176; 27,2 hp in its 2nd year: 2,5 -> 68
#guard envBase10 13600 == 100
#guard envYearFactor10 2025 2020 == 16
#guard envYearFactor10 2025 2010 == 20
#guard envYearFactor10 2025 2024 == 10
#guard envBase10 2720 == 25

end AmGlobal
