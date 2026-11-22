import SgGlobal.Pit
import TaxKernel.Global2

/-!
# Singapore 2025: goods and services tax (5111); excise duties (5121)

Source: Goods and Services Tax Act 1993 (2020 Revised Edition), Singapore Statutes Online historical version "in force
from 1/7/2025 to 8/12/2025" (PDF fetched from sso.agc.gov.sg through a second machine route; `sg/law/gsta_valid20250701.pdf`,
text by pdftotext, sha256 in `SHA256SUMS`).
* **s. 16**: "Tax is charged at the rate of — … (cb) 9% from and including 1 January 2024".
* **Second Schedule para. 1 (1) (a) (ii)**: liable to register when taxable supplies in a calendar year "exceeded
  $1 million".
* **Fourth Schedule Part 1** exempt supplies: para. 1 financial services (accounts, loans, (l) life insurance); para. 2
  interests in or licences to occupy residential land and buildings (residential letting).

**Excise duties (session 8, grade B)**: Customs Act 1960 and the Customs (Duties) Order (rates not read in the Order: the
SSO schedule is not in its HTML and was not fetched), rates from Singapore Customs' List of Dutiable Goods in its
versions of 15 January 2025 and 4 July 2025 (Internet Archive; the rates of both are identical, so applied to all 2025;
the 2026 list shows a later cigarette rate of 58.9 c a gram, not dated):
* **HS 2710 12 24-26** motor spirit RON 90 to below 97: $6.60 per decalitre (66 c a litre); **2710 12 21-23** RON 97 and
  above (line `"sub": "ron97"`): $7.90 per dal; **2710 19 71** automotive diesel: $2.00 per dal.
* **HS 2203** beer and stout: excise $60.00 per litre of alcohol (customs duty $16.00 per l al on imports: not modelled);
  **2204** wine and **2208** spirits: excise $88.00 per litre of alcohol.
* **HS 2402 20 90** cigarettes: 49.1 c for every gram or part thereof of each stick (a stick of up to 1 g: 49.1 c);
  **2402 10 00** cigars and other tobacco by weight $491.00 per kg (needs the line's `"massG"`).

**Road tax on cars (5200, session 8, grade B)**: Road Traffic Act 1961 and the Road Traffic (Motor Vehicles, Registration
and Licensing) Rules (not read); formulas from the LTA's published Vehicle Tax Structure (fetched 2026-11-21; the page carries
no date: its formulas are applied to 2025, flagged):
* petrol, CNG and diesel cars, 6-monthly: EC ≤ 600 cc $200; [$200 + $0.125 (EC − 600)] to 1 000 cc; [$250 + $0.375 (EC −
  1 000)] to 1 600 cc; [$475 + $0.75 (EC − 1 600)] to 3 000 cc; [$1 525 + $1 (EC − 3 000)] above; all × 0.782. The bands
  join (a marginal schedule): yearly = 2 × 0.782 × ($200 + marginal parts) (multiplier 1.564).
* electric cars, by power rating PR (kW), 6-monthly: PR ≤ 7.5 $200; [$200 + $2 (PR − 7.5)] to 30; [$250 + $3.75 (PR − 30)]
  to 230; [$1 525 + $10 (PR − 230)] above; × 0.782; plus the additional flat component $350 every 6 months ($700 a year).
* Not modelled: the diesel special tax (by emission standard), the petrol-electric rule (the higher of the engine and the
  power calculation: the engine side only is computed), surcharges for cars over 10 years, and rounding to cents (whole
  dollars, rounded down).
-/

namespace SgGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Goods and services tax", standard := 900, threshold := 1000000,
    classOf := fun gd => match gd with
      | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "GST Act 1993 s. 16 (cb) (9 %), Second Schedule para. 1 ($1 million), Fourth Schedule Part 1 paras. 1-2"

def sgSt (hs r : String) : String := s!"Customs Act 1960; Customs (Duties) Order; List of Dutiable Goods (Singapore Customs, 15 Jan and 4 Jul 2025), HS {hs}: {r}"

def sgExcise : List ExciseRule :=
  [{ good := .petrol, sub := "ron97", name := "Excise duty (motor spirit RON 97+)", perUnitNum := 79, perUnitDen := 100,
     statute := sgSt "2710 12 21-23" "$7.90 per dal" },
   { good := .petrol, name := "Excise duty (motor spirit RON 90-97)", perUnitNum := 66, perUnitDen := 100,
     statute := sgSt "2710 12 24-26" "$6.60 per dal" },
   { good := .diesel, name := "Excise duty (automotive diesel)", perUnitNum := 20, perUnitDen := 100,
     statute := sgSt "2710 19 71" "$2.00 per dal" },
   { good := .beer, name := "Excise duty (beer)", perUnitNum := 60, onPureAlcohol := true,
     statute := sgSt "2203" "$60.00 per litre of alcohol" },
   { good := .wine, name := "Excise duty (wine)", perUnitNum := 88, onPureAlcohol := true,
     statute := sgSt "2204" "$88.00 per litre of alcohol" },
   { good := .spirits, name := "Excise duty (spirits)", perUnitNum := 88, onPureAlcohol := true,
     statute := sgSt "2208" "$88.00 per litre of alcohol" },
   { good := .cigarettes, name := "Excise duty (cigarettes)", perUnitNum := 491, perUnitDen := 1000,
     statute := sgSt "2402 20 90" "49.1 cents for every gram or part thereof of each stick (sticks of up to 1 g)" },
   { good := .tobaccoOther, name := "Excise duty (cigars and tobacco by weight)", perKgNum := 491,
     statute := sgSt "2402 10 00" "$491.00 per kg" }]

def sgRtSt : String := "Road Traffic Act 1961; LTA Vehicle Tax Structure (road tax, 6-monthly amount × 0.782, × 2 for the year)"

def sgVehicleTaxes : List VehicleTax :=
  [{ name := "Road tax (cars, by engine capacity)", kinds := ["car"], fuels := [.petrol, .diesel, .cng, .hybrid],
     fixed := 200, parts := [(.engineCcm, { steps := [(600, 125), (1000, 375), (1600, 750), (3000, 1000)], den := 1000 })],
     multiplierBp := 15640, statute := sgRtSt ++ ": $200 + $0.125/cc above 600, $0.375 above 1 000, $0.75 above 1 600, $1 above 3 000" },
   { name := "Road tax (electric cars, by power rating)", kinds := ["car"], fuels := [.electric], when := [(.engineKw, -1, 7)],
     fixed := 200, multiplierBp := 15640, statute := sgRtSt ++ ": PR up to 7.5 kW $200" },
   { name := "Road tax (electric cars, by power rating)", kinds := ["car"], fuels := [.electric], when := [(.engineKw, 7, 30)],
     fixed := 185, parts := [(.engineKw, QtyTable.perUnit 2 1)], multiplierBp := 15640, statute := sgRtSt ++ ": $200 + $2 (PR - 7.5)" },
   { name := "Road tax (electric cars, by power rating)", kinds := ["car"], fuels := [.electric], when := [(.engineKw, 30, 230)],
     fixed := 250, parts := [(.engineKw, { steps := [(30, 375)], den := 100 })], multiplierBp := 15640, statute := sgRtSt ++ ": $250 + $3.75 (PR - 30)" },
   { name := "Road tax (electric cars, by power rating)", kinds := ["car"], fuels := [.electric], when := [(.engineKw, 230, VehicleTax.noBound)],
     fixed := 1525, parts := [(.engineKw, { steps := [(230, 10)] })], multiplierBp := 15640, statute := sgRtSt ++ ": $1 525 + $10 (PR - 230)" },
   { name := "Road tax additional flat component (electric cars)", kinds := ["car"], fuels := [.electric],
     fixed := 700, statute := "LTA Vehicle Tax Structure: additional flat component $350 every 6 months" }]

def families : List Family :=
  [{ name := "5111 GST; 5121 excise duties", covers := [.vat, .excise, .useOfGoods],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ exciseRuleCharges sgExcise g (firstOnly := true)
       ++ vehicleTaxCharges sgVehicleTaxes g }]

def absent : List Absent :=
  []

def notes : List String := ["SG 5111: GST Act 1993, SSO version in force 1/7/2025 - 8/12/2025", "SG 5121: Singapore Customs List of Dutiable Goods (15 Jan / 4 Jul 2025): motor spirit, diesel, liquor, tobacco", "SG 5200: road tax on cars per the LTA Vehicle Tax Structure (engine capacity; EV power rating + AFC)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .insurance) then ["insurance taken as exempt (only life insurance is; general insurance is standard-rated)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes) then ["cigarette duty is per gram or part of a gram of each stick: sticks taken as weighing up to 1 g"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer) then ["customs duty on imported beer ($16.00 per litre of alcohol) not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .tobaccoOther) then ["tobacco by weight needs the line's \"massG\"; a line without it is charged 0"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol) then ["petrol taken as RON 90-97 unless the line has \"sub\": \"ron97\""] else [])
  ++ vehicleTaxUnknown "Road tax" sgVehicleTaxes g
  ++ vehicleTaxUnmatched "Road tax" sgVehicleTaxes g
  ++ (if g.vehicles.isEmpty then [] else ["road tax per the LTA's published formulas (Rules not read); diesel special tax, the petrol-electric higher-of rule, the surcharge for cars over 10 years and cents not modelled; motorcycles and goods vehicles not modelled"])

#guard vat.embedded { good := .food, amount := 10900 } == 900
#guard vat.embedded { good := .rent, amount := 10900 } == 0
#guard vat.net { turnover := 1000000, sales := [{ good := .other, net := 1000000 }] } == 0
#guard sgExcise.length == 8
#guard (sgExcise.find? (fun e => e.good == .petrol && e.sub == "")).map (fun e => e.dutyOn { good := .petrol, amount := 280, quantity := 100000 } {}) == some 66
#guard (sgExcise.find? (fun e => e.good == .cigarettes)).map (fun e => e.dutyOn { good := .cigarettes, amount := 15, quantity := 20000 } {}) == some 9
#guard (sgExcise.find? (fun e => e.good == .beer)).map (fun e => e.dutyOn { good := .beer, amount := 40, quantity := 6000, abvBp := 500 } {}) == some 18
#guard sgVehicleTaxes.length == 6
#guard ((sgVehicleTaxes.getD 0 default).fixed + ({ steps := [(600, 125), (1000, 375), (1600, 750), (3000, 1000)], den := 1000 } : QtyTable).amount 1598) == 474

end SgGlobal.Consumption
