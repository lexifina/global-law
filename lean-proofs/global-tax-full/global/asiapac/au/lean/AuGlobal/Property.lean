import AuGlobal.Pit
import TaxKernel.Global2

/-!
# Australia 2025 (NSW): land tax and transfer duty (4100, 4400)
(B: thresholds indexed annually, as published by Revenue NSW.) Land Tax Act 1956 (NSW) s. 9: $100 + 1.6 % of land value above
the $1,075,000 threshold, 2 % above the premium threshold $6,571,000 (`landTax`); the principal place of residence is exempt
(homes not taxed). Duties Act 1997 (NSW) s. 32: $1.25 per $100 to $17,000, $1.50 to $36,000, $1.75 to $97,000, $3.50 to
$364,000, $4.50 to $1,212,000, $5.50 above (marginal); s. 104N surcharge purchaser duty for foreign persons 8 %.

FT review (2026-11-21, third pass). Duties Act 1997 (NSW), Internet Archive copy of legislation.nsw.gov.au "whole/html/inforce/
current/act-1997-123" captured 2025-04-30 (`au/law/nsw_duties_wb20250430.txt`; the live site answers 403 to scripts):
* **s. 32 (4), Div. 3 ss. 33AB-33AD**: the s. 32 thresholds (2019: $14,000, $30,000, $81,000, $304,000, $1,013,000) are
  "adjustable amounts", multiplied each 1 July by A/B (Sydney CPI, March quarter of the preceding year over March 2019, to
  3 decimals) and rounded to the nearest $1,000. The model's thresholds are those amounts at A/B = 1.196 (Revenue NSW's
  published values, not re-derived: the Sydney CPI series and the s. 33AF notice for 2025-26 were not read; B).
* **s. 32A (1), (2C)**: residential land above $3,040,000 (an adjustable amount: at the same A/B, $3,636,000) bears "the
  premium base amount plus $7 for every $100, or part" above it: a 7 % marginal band, now applied to homes.
* **s. 104U (1)**: surcharge purchaser duty "at a rate of 9% of the dutiable value" (was 8 % in the model).
* **s. 78A (1)**: an approved first home buyer pays no duty where the dutiable value is "not more than (a) $800,000 if the
  property has a private dwelling built on it, or (b) $350,000 if the property comprises a vacant block of residential
  land"; **s. 73 (5)**: a purchaser "is not eligible unless the person is an Australian citizen or a permanent resident"
  (a `nonResident` buyer is read as not eligible). The s. 78A (2), (2A) concession above those amounts (to $1,000,000 /
  $450,000) is a formula printed as an image in the capture: listed, not computed.
* **s. 32 (1)** charges "$1.25 for every $100 (or part)" of the dutiable value and, in the higher ranges, "for every $100
  (or part) by which the dutiable value exceeds the minimum threshold amount": the value is taken up to the next $100
  for the s. 32 / s. 32A schedule (the thresholds are multiples of $1,000, so this is the same per range). The base
  amounts (s. 33AD (3): nearest dollar, 50 cents down) differ from the marginal sums by at most 50 cents. Surcharge
  purchaser duty (Chapter 2A, s. 104U) is charged on the dutiable value itself, as its own charge.
Session 11 (year in force): the Div. 3 thresholds are re-indexed every 1 July. Revenue NSW "Transfer duty" page, Internet
Archive 2025-06-21 ("From 1 July 2024": $17,000 / $36,000 / $97,000 / $364,000 / $1,212,000; premium over $3,636,000) and
2025-09-15 ("From 1 July 2025": $17,000 / $37,000 / $99,000 / $372,000 / $1,240,000; premium over $3,721,000)
(`au/law/au_revnsw_transfer_duty_wb*.html`). The schedule is taken by the purchase record's `"date"`; an undated purchase
above $36,000 (where the two schedules differ) books no s. 32 / 32A duty and is listed (grade C); the s. 104U surcharge (9 %)
is the same in both years.
-/

namespace AuGlobal.Property
open TaxKernel TaxKernel.Global

def landTax (v : Int) : Int :=
  if v ≤ 1075000 then 0 else 100 + divR .down (160 * (min v 6571000 - 1075000)) BP + divR .down (200 * pos (v - 6571000)) BP
def landF : Family :=
  { name := "4100 land tax (NSW)", covers := [.propertyRecurrent],
    run := fun _ g _ => let v := isum ((g.assets.filter fun a => a.kind == .land || a.kind == .realEstate).map (·.statutoryValue))
      if v ≤ 0 then [] else [charge .propertyRecurrent "Land tax (NSW)" v id landTax (level := .state) (statute := "Land Tax Act 1956 (NSW) s. 9; Land Tax Management Act 1956")] }
/-- s. 32 general rate (thresholds as indexed under Div. 3) and s. 104U (1) surcharge purchaser duty 9 %. -/
def duty : TransferDuty :=
  { name := "Transfer duty (NSW)", sched := Schedule.ofList [(0, 125), (17000, 150), (36000, 175), (97000, 350), (364000, 450), (1212000, 550)], kinds := [.realEstate, .land] }
/-- residential land (homes): s. 32 plus the s. 32A premium band, $7 per $100 above $3,040,000 as indexed ($3,636,000). -/
def dutyHome : TransferDuty :=
  { name := "Transfer duty (NSW)", sched := Schedule.ofList [(0, 125), (17000, 150), (36000, 175), (97000, 350), (364000, 450), (1212000, 550), (3636000, 700)], kinds := [.home] }
/-- Chapter 2A, s. 104U (1): surcharge purchaser duty, 9 % of the dutiable value (foreign persons). -/
def surcharge : TransferDuty := { name := "Surcharge purchaser duty (NSW)", sched := Schedule.flat 0, nonResidentBp := 900 }
/-- s. 32 (1): "for every $100 (or part)": the value taken up to the next $100 for the schedule. -/
def up100 (p : Purchase) : Purchase := { p with price := (p.price + 99) / 100 * 100 }
/-- s. 78A (1): approved first home buyers (citizens or permanent residents, s. 73 (5)): no duty to $800,000 (dwelling) / $350,000 (vacant land). -/
def dutyHomeFH : TransferDuty := { dutyHome with firstHomeCap := 800000 }
def dutyLandFH : TransferDuty := { duty with kinds := [.land], firstHomeCap := 350000 }
def dutyReFH : TransferDuty := { duty with kinds := [.realEstate] }
def fhEligible (p : Purchase) : Bool := p.firstHome && !p.nonResident
def dutyF24 : Family :=
  { name := "4400 transfer duty (NSW)", covers := [.transactions],
    run := fun _ g _ =>
      let st := "Duties Act 1997 (NSW) ss. 32, 32A, 33AC, 78A (1), 104U (1)"
      let ps := g.purchases.map up100
      let fh := ps.filter fhEligible
      let other := ps.filter (fun p => !fhEligible p)
      dutyHomeFH.charges fh st (level := .state) ++ dutyLandFH.charges fh st (level := .state) ++ dutyReFH.charges fh st (level := .state)
      ++ dutyHome.charges other st (level := .state) ++ duty.charges other st (level := .state)
      ++ surcharge.charges (g.purchases.filter (·.nonResident)) "Duties Act 1997 (NSW) s. 104U (1) (9 %)" (level := .state) }

/-- 2025-26 thresholds (from 1 July 2025; Revenue NSW, Internet Archive 2025-09-15). -/
def duty25 : TransferDuty := { duty with sched := Schedule.ofList [(0, 125), (17000, 150), (37000, 175), (99000, 350), (372000, 450), (1240000, 550)] }
def dutyHome25 : TransferDuty := { dutyHome with sched := Schedule.ofList [(0, 125), (17000, 150), (37000, 175), (99000, 350), (372000, 450), (1240000, 550), (3721000, 700)] }
def dutyHomeFH25 : TransferDuty := { dutyHome25 with firstHomeCap := 800000 }
def dutyLandFH25 : TransferDuty := { duty25 with kinds := [.land], firstHomeCap := 350000 }
def dutyReFH25 : TransferDuty := { duty25 with kinds := [.realEstate] }
/-- The date of purchase `i` (`"date"` on the input record), as yyyymmdd. -/
def purDay (g : CanonGlobal) (i : Nat) : Option Nat :=
  AdvanceTax.dayOfRecord ((arrField g.raw "purchases").toList.getD i Lean.Json.null)
/-- An undated purchase is charged s. 32 duty only at or below $36,000, where both years' schedules agree. -/
def sameBoth (p : Purchase) : Bool := p.price ≤ 36000
def dutyF : Family :=
  { name := "4400 transfer duty (NSW)", covers := [.transactions],
    run := fun _ g _ =>
      let st := "Duties Act 1997 (NSW) ss. 32, 32A, 33AC, 78A (1), 104U (1)"
      let ix := g.purchases.zipIdx
      let pre := (ix.filter fun (p, i) => (purDay g i).any (· < 20250701) || ((purDay g i).isNone && sameBoth (up100 p))).map fun (p, _) => up100 p
      let post := (ix.filter fun (_, i) => (purDay g i).any (· ≥ 20250701)).map fun (p, _) => up100 p
      let st24 := st ++ " (thresholds from 1 July 2024)"
      let st25 := st ++ " (thresholds from 1 July 2025)"
      dutyHomeFH.charges (pre.filter fhEligible) st24 (level := .state) ++ dutyLandFH.charges (pre.filter fhEligible) st24 (level := .state)
      ++ dutyReFH.charges (pre.filter fhEligible) st24 (level := .state)
      ++ dutyHome.charges (pre.filter (!fhEligible ·)) st24 (level := .state) ++ duty.charges (pre.filter (!fhEligible ·)) st24 (level := .state)
      ++ dutyHomeFH25.charges (post.filter fhEligible) st25 (level := .state) ++ dutyLandFH25.charges (post.filter fhEligible) st25 (level := .state)
      ++ dutyReFH25.charges (post.filter fhEligible) st25 (level := .state)
      ++ dutyHome25.charges (post.filter (!fhEligible ·)) st25 (level := .state) ++ duty25.charges (post.filter (!fhEligible ·)) st25 (level := .state)
      ++ surcharge.charges (g.purchases.filter (·.nonResident)) "Duties Act 1997 (NSW) s. 104U (1) (9 %)" (level := .state) }

def families : List Family := [landF, dutyF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .home) then ["principal residence exempt from land tax; council rates not modelled"] else [])
  ++ (if g.purchases.any (fun p => p.firstHome) then ["first home buyers: s. 78A (1) exemption applied (to $800,000 dwelling, $350,000 vacant land; foreign buyers not eligible, s. 73 (5)); the s. 78A (2), (2A) concession above those amounts (to $1,000,000 / $450,000) not computed (full duty)"] else [])
  ++ (if g.purchases.any (fun p => p.kind == .realEstate) then ["realEstate purchases taken as not residential land (no s. 32A premium rate)"] else [])
  ++ (if g.purchases.zipIdx.any (fun (p, i) => (purDay g i).isNone && !sameBoth (up100 p)) then ["transfer duty: an undated purchase above $36,000 (thresholds re-indexed on 1 July 2025): s. 32 / 32A duty not booked (grade C)"] else [])

#guard landTax 2075000 == 16100
#guard dutyHome.amount { kind := .home, price := 1000000 } == 39530
-- s. 32A: 7 % above $3,636,000
#guard dutyHome.amount { kind := .home, price := 4636000 } == duty.amount { kind := .land, price := 3636000 } + 70000
#guard dutyHomeFH.amount { kind := .home, price := 800000, firstHome := true } == 0
#guard dutyHomeFH.amount { kind := .home, price := 800001, firstHome := true } == dutyHome.amount { kind := .home, price := 800001 }
#guard dutyLandFH.amount { kind := .land, price := 350000, firstHome := true } == 0
-- s. 104U: 9 % surcharge, its own charge
#guard surcharge.amount { kind := .home, price := 1000000, nonResident := true } == 90000
-- s. 32 (1): $33,233 is taken as $33,300: 212.50 + 163 x 1.50 = 457 (s. 33AD (3) base $212: 456.50)
#guard dutyHome.amount (up100 { kind := .home, price := 33233 }) == 457
#guard dutyHome25.amount { kind := .home, price := 1000000 } == 39412
#guard dutyHome25.amount { kind := .home, price := 4721000 } == duty25.amount { kind := .land, price := 3721000 } + 70000
#guard duty25.amount { kind := .land, price := 30000 } == duty.amount { kind := .land, price := 30000 }

end AuGlobal.Property
